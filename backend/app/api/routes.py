from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from app.api.deps import get_current_user, require_role
from app.core.config import settings
from app.core.db import get_db
from app.core.security import verify_password, create_access_token, encrypt_secret, decrypt_secret
from app.models.models import User, TenantIntegration, Endpoint, Alert, AuditLog, NotificationChannel, Subscription, SyncJob, TenantPolicy
from app.schemas.schemas import LoginIn, IntegrationIn, NotificationChannelIn, RotateSecretIn, PolicyIn
from app.services.audit import log_action
from app.services.wazuh import WazuhClient, WazuhIndexerClient
from app.services.rate_limit import tenant_rate_limit
from app.services.queue import enqueue, QUEUE_MAIN, QUEUE_SYNC, list_dead_letter
from app.services.ops import collect_metrics

router = APIRouter(prefix='/api')

oauth = OAuth()
if settings.OIDC_ENABLED and settings.OIDC_ISSUER and settings.OIDC_CLIENT_ID:
    oauth.register(
        name='oidc',
        server_metadata_url=f"{settings.OIDC_ISSUER.rstrip('/')}/.well-known/openid-configuration",
        client_id=settings.OIDC_CLIENT_ID,
        client_secret=settings.OIDC_CLIENT_SECRET,
        client_kwargs={'scope': settings.OIDC_SCOPES},
    )


@router.post('/auth/login')
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = create_access_token(user.email, user.tenant_id, user.role)
    log_action(db, user.tenant_id, user.email, 'auth.login', 'password login')
    return {'access_token': token, 'token_type': 'bearer'}


@router.get('/auth/oidc/login')
async def oidc_login(request: Request):
    if not settings.OIDC_ENABLED:
        raise HTTPException(status_code=400, detail='OIDC is disabled')
    if 'oidc' not in oauth:
        raise HTTPException(status_code=400, detail='OIDC provider is not configured')
    redirect_uri = settings.OIDC_REDIRECT_URI
    return await oauth.oidc.authorize_redirect(request, redirect_uri)


@router.get('/auth/oidc/callback')
async def oidc_callback(request: Request, db: Session = Depends(get_db)):
    if 'oidc' not in oauth:
        raise HTTPException(status_code=400, detail='OIDC provider is not configured')
    token = await oauth.oidc.authorize_access_token(request)
    userinfo = token.get('userinfo') or {}
    email = userinfo.get('email')
    subject = userinfo.get('sub')
    if not email:
        raise HTTPException(status_code=400, detail='OIDC provider did not return email')
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=403, detail='No local account mapped for this OIDC identity')
    user.oidc_subject = subject
    db.commit()
    jwt_token = create_access_token(user.email, user.tenant_id, user.role)
    log_action(db, user.tenant_id, user.email, 'auth.login', 'oidc login')
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/#token={jwt_token}")


@router.get('/me')
def me(user=Depends(get_current_user)):
    return {'email': user.email, 'role': user.role, 'tenant_id': user.tenant_id}


@router.get('/billing')
def billing(user=Depends(get_current_user), db: Session = Depends(get_db)):
    sub = db.query(Subscription).filter(Subscription.tenant_id == user.tenant_id).first()
    return sub.__dict__ if sub else {'plan': 'starter', 'status': 'trial'}


@router.put('/integrations/wazuh')
def set_wazuh_integration(payload: IntegrationIn, request: Request, user=Depends(require_role('owner', 'admin')), db: Session = Depends(get_db)):
    tenant_rate_limit(request, f'tenant:{user.tenant_id}')
    row = db.query(TenantIntegration).filter(TenantIntegration.tenant_id == user.tenant_id, TenantIntegration.provider == payload.provider).first()
    encrypted = encrypt_secret(payload.password)
    if row:
        row.base_url = payload.base_url
        row.username = payload.username
        row.encrypted_password = encrypted
        row.verify_ssl = payload.verify_ssl
        row.rotated_at = datetime.utcnow()
    else:
        row = TenantIntegration(
            tenant_id=user.tenant_id,
            provider=payload.provider,
            base_url=payload.base_url,
            username=payload.username,
            encrypted_password=encrypted,
            verify_ssl=payload.verify_ssl,
            rotated_at=datetime.utcnow(),
        )
        db.add(row)
    db.commit()
    log_action(db, user.tenant_id, user.email, 'integration.updated', payload.provider)
    return {'ok': True}


@router.get('/integrations/wazuh')
def get_wazuh_integration(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(TenantIntegration).filter(TenantIntegration.tenant_id == user.tenant_id).all()
    return [
        {
            'provider': row.provider,
            'configured': True,
            'base_url': row.base_url,
            'username': row.username,
            'verify_ssl': row.verify_ssl,
            'rotated_at': str(row.rotated_at) if row.rotated_at else None,
        } for row in rows
    ]


@router.post('/ops/rotate-secret/{provider}')
def rotate_secret(provider: str, payload: RotateSecretIn, user=Depends(require_role('owner', 'admin')), db: Session = Depends(get_db)):
    row = db.query(TenantIntegration).filter(TenantIntegration.tenant_id == user.tenant_id, TenantIntegration.provider == provider).first()
    if not row:
        raise HTTPException(status_code=404, detail='Integration not found')
    if payload.username:
        row.username = payload.username
    row.encrypted_password = encrypt_secret(payload.password)
    row.rotated_at = datetime.utcnow()
    db.commit()
    log_action(db, user.tenant_id, user.email, 'integration.secret_rotated', provider)
    return {'ok': True, 'provider': provider, 'rotated_at': str(row.rotated_at)}


@router.post('/sync/agents')
def sync_agents(request: Request, user=Depends(require_role('owner', 'admin', 'analyst')), db: Session = Depends(get_db)):
    tenant_rate_limit(request, f'tenant:{user.tenant_id}')
    row = db.query(TenantIntegration).filter(TenantIntegration.tenant_id == user.tenant_id, TenantIntegration.provider == 'wazuh_api').first()
    if not row:
        raise HTTPException(status_code=400, detail='Wazuh API integration not configured')
    client = WazuhClient(row.base_url, row.username, decrypt_secret(row.encrypted_password), row.verify_ssl)
    data = client.list_agents()
    items = data.get('data', {}).get('affected_items', [])
    count = 0
    for item in items:
        agent_id = str(item.get('id'))
        ep = db.query(Endpoint).filter(Endpoint.tenant_id == user.tenant_id, Endpoint.wazuh_agent_id == agent_id).first()
        if not ep:
            ep = Endpoint(tenant_id=user.tenant_id, wazuh_agent_id=agent_id, name=item.get('name', 'unknown'))
            db.add(ep)
        ep.name = item.get('name', ep.name)
        ep.ip = item.get('ip')
        ep.os = (item.get('os') or {}).get('name') if isinstance(item.get('os'), dict) else None
        ep.status = item.get('status')
        ep.last_seen = item.get('lastKeepAlive')
        count += 1
    db.commit()
    log_action(db, user.tenant_id, user.email, 'sync.agents', f'{count} agents')
    return {'synced_agents': count}


@router.post('/sync/alerts')
def sync_alerts(request: Request, user=Depends(require_role('owner', 'admin', 'analyst')), db: Session = Depends(get_db)):
    tenant_rate_limit(request, f'tenant:{user.tenant_id}')
    row = db.query(TenantIntegration).filter(TenantIntegration.tenant_id == user.tenant_id, TenantIntegration.provider == 'wazuh_indexer').first()
    if not row:
        raise HTTPException(status_code=400, detail='Wazuh indexer integration not configured')
    client = WazuhIndexerClient(row.base_url, row.username, decrypt_secret(row.encrypted_password), row.verify_ssl)
    data = client.search_alerts(limit=50)
    items = data.get('hits', {}).get('hits', [])
    count = 0
    for item in items:
        src = item.get('_source', {})
        external_id = item.get('_id')
        existing = db.query(Alert).filter(Alert.tenant_id == user.tenant_id, Alert.external_id == external_id).first()
        if existing:
            continue
        db.add(Alert(
            tenant_id=user.tenant_id,
            external_id=external_id,
            rule_level=((src.get('rule') or {}).get('level') if isinstance(src.get('rule'), dict) else None),
            rule_description=((src.get('rule') or {}).get('description') if isinstance(src.get('rule'), dict) else None),
            agent_name=((src.get('agent') or {}).get('name') if isinstance(src.get('agent'), dict) else None),
            timestamp=src.get('@timestamp'),
            raw=str(src),
        ))
        count += 1
    db.commit()
    log_action(db, user.tenant_id, user.email, 'sync.alerts', f'{count} alerts')
    return {'synced_alerts': count}


@router.post('/ops/jobs/sync')
def enqueue_sync_job(payload: dict, user=Depends(require_role('owner', 'admin', 'analyst')), db: Session = Depends(get_db)):
    sync_type = payload.get('sync_type', 'agents')
    enqueue(QUEUE_SYNC, {'tenant_id': user.tenant_id, 'sync_type': sync_type, 'attempts': 0})
    db.add(SyncJob(tenant_id=user.tenant_id, job_type=sync_type, status='queued', detail='queued via api'))
    db.commit()
    log_action(db, user.tenant_id, user.email, 'sync.job.queued', sync_type)
    return {'queued': True, 'sync_type': sync_type}


@router.get('/ops/jobs')
def get_sync_jobs(user=Depends(require_role('owner', 'admin', 'analyst')), db: Session = Depends(get_db)):
    rows = db.query(SyncJob).filter(SyncJob.tenant_id == user.tenant_id).order_by(SyncJob.id.desc()).limit(50).all()
    return [{'job_type': x.job_type, 'status': x.status, 'detail': x.detail, 'updated_at': str(x.updated_at)} for x in rows]


@router.get('/ops/jobs/dead-letter')
def dead_letter(user=Depends(require_role('owner', 'admin')), db: Session = Depends(get_db)):
    log_action(db, user.tenant_id, user.email, 'ops.dead_letter.view', 'viewed dead-letter queue')
    return list_dead_letter(100)


@router.post('/ops/test-notification')
def test_notification(user=Depends(require_role('owner', 'admin')), db: Session = Depends(get_db)):
    enqueue(QUEUE_MAIN, {
        'tenant_id': user.tenant_id,
        'subject': 'OpenSOC notification test',
        'body': f'Notification pipeline test for tenant {user.tenant_id}',
        'attempts': 0,
    })
    log_action(db, user.tenant_id, user.email, 'notification.test_queued', 'test notification queued')
    return {'queued': True}


@router.get('/ops/metrics')
def metrics(user=Depends(require_role('owner', 'admin', 'analyst')), db: Session = Depends(get_db)):
    return collect_metrics(db)


@router.get('/ops/wazuh-health')
def wazuh_health(user=Depends(require_role('owner', 'admin', 'analyst')), db: Session = Depends(get_db)):
    row = db.query(TenantIntegration).filter(TenantIntegration.tenant_id == user.tenant_id, TenantIntegration.provider == 'wazuh_api').first()
    if not row:
        raise HTTPException(status_code=400, detail='Wazuh API integration not configured')
    client = WazuhClient(row.base_url, row.username, decrypt_secret(row.encrypted_password), row.verify_ssl)
    return client.health()


@router.get('/endpoints')
def endpoints(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Endpoint).filter(Endpoint.tenant_id == user.tenant_id).all()
    return [{'id': x.id, 'agent_id': x.wazuh_agent_id, 'name': x.name, 'ip': x.ip, 'status': x.status} for x in rows]


@router.get('/alerts')
def alerts(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Alert).filter(Alert.tenant_id == user.tenant_id).order_by(Alert.id.desc()).limit(50).all()
    return [{'external_id': x.external_id, 'rule_level': x.rule_level, 'rule_description': x.rule_description, 'agent_name': x.agent_name, 'timestamp': x.timestamp} for x in rows]


@router.get('/audit-logs')
def audit_logs(user=Depends(require_role('owner', 'admin', 'analyst')), db: Session = Depends(get_db)):
    rows = db.query(AuditLog).filter((AuditLog.tenant_id == user.tenant_id) | (AuditLog.tenant_id.is_(None))).order_by(AuditLog.id.desc()).limit(100).all()
    return [{'action': x.action, 'detail': x.detail, 'actor_email': x.actor_email, 'created_at': str(x.created_at)} for x in rows]


@router.get('/notifications')
def list_channels(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(NotificationChannel).filter(NotificationChannel.tenant_id == user.tenant_id).all()
    return [{'id': x.id, 'type': x.type, 'target': x.target, 'enabled': x.enabled} for x in rows]


@router.post('/notifications')
def add_channel(payload: NotificationChannelIn, user=Depends(require_role('owner', 'admin')), db: Session = Depends(get_db)):
    row = NotificationChannel(tenant_id=user.tenant_id, type=payload.type, target=payload.target, enabled=payload.enabled)
    db.add(row)
    db.commit()
    log_action(db, user.tenant_id, user.email, 'notification_channel.created', f'{payload.type}:{payload.target}')
    return {'ok': True}


@router.get('/policy')
def get_policy(user=Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.query(TenantPolicy).filter(TenantPolicy.tenant_id == user.tenant_id).first()
    if not row:
        return {'min_alert_level': 7, 'notifications_enabled': True, 'auto_sync_enabled': True}
    return {'min_alert_level': row.min_alert_level, 'notifications_enabled': row.notifications_enabled, 'auto_sync_enabled': row.auto_sync_enabled}


@router.put('/policy')
def set_policy(payload: PolicyIn, user=Depends(require_role('owner', 'admin')), db: Session = Depends(get_db)):
    row = db.query(TenantPolicy).filter(TenantPolicy.tenant_id == user.tenant_id).first()
    if not row:
        row = TenantPolicy(tenant_id=user.tenant_id)
        db.add(row)
    row.min_alert_level = payload.min_alert_level
    row.notifications_enabled = payload.notifications_enabled
    row.auto_sync_enabled = payload.auto_sync_enabled
    row.updated_at = datetime.utcnow()
    db.commit()
    log_action(db, user.tenant_id, user.email, 'policy.updated', str(payload.model_dump()))
    return {'ok': True}
