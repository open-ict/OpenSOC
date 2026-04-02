import json
import time
from datetime import datetime
import redis
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import SessionLocal
from app.models.models import NotificationChannel, SyncJob, Tenant, TenantIntegration, Endpoint, Alert
from app.services.notify import send_email, send_webhook, NotificationError
from app.services.audit import safe_log_action
from app.services.queue import QUEUE_MAIN, QUEUE_DLQ, QUEUE_SYNC
from app.services.wazuh import WazuhClient, WazuhIndexerClient
from app.core.security import decrypt_secret


def deliver_notification(db: Session, job: dict):
    tenant_id = job.get('tenant_id')
    channels = db.query(NotificationChannel).filter(NotificationChannel.tenant_id == tenant_id, NotificationChannel.enabled == True).all()  # noqa
    for ch in channels:
        if ch.type == 'email':
            send_email(ch.target, job.get('subject', 'OpenSOC Alert'), job.get('body', ''))
        elif ch.type == 'webhook':
            send_webhook(ch.target, job)


def _touch_sync_job(db: Session, tenant_id: int, job_type: str, status: str, detail: str = ''):
    row = SyncJob(tenant_id=tenant_id, job_type=job_type, status=status, detail=detail, updated_at=datetime.utcnow())
    db.add(row)
    db.commit()


def sync_agents(db: Session, tenant_id: int):
    row = db.query(TenantIntegration).filter(TenantIntegration.tenant_id == tenant_id, TenantIntegration.provider == 'wazuh_api').first()
    if not row:
        return 0
    client = WazuhClient(row.base_url, row.username, decrypt_secret(row.encrypted_password), row.verify_ssl)
    data = client.list_agents()
    items = data.get('data', {}).get('affected_items', [])
    count = 0
    for item in items:
        agent_id = str(item.get('id'))
        ep = db.query(Endpoint).filter(Endpoint.tenant_id == tenant_id, Endpoint.wazuh_agent_id == agent_id).first()
        if not ep:
            ep = Endpoint(tenant_id=tenant_id, wazuh_agent_id=agent_id, name=item.get('name', 'unknown'))
            db.add(ep)
        ep.name = item.get('name', ep.name)
        ep.ip = item.get('ip')
        ep.os = (item.get('os') or {}).get('name') if isinstance(item.get('os'), dict) else None
        ep.status = item.get('status')
        ep.last_seen = item.get('lastKeepAlive')
        count += 1
    db.commit()
    return count


def sync_alerts(db: Session, tenant_id: int):
    api = db.query(TenantIntegration).filter(TenantIntegration.tenant_id == tenant_id, TenantIntegration.provider == 'wazuh_indexer').first()
    if not api:
        return 0
    client = WazuhIndexerClient(api.base_url, api.username, decrypt_secret(api.encrypted_password), api.verify_ssl)
    data = client.search_alerts(limit=50)
    items = data.get('hits', {}).get('hits', [])
    count = 0
    for item in items:
        src = item.get('_source', {})
        external_id = item.get('_id')
        row = db.query(Alert).filter(Alert.tenant_id == tenant_id, Alert.external_id == external_id).first()
        if row:
            continue
        row = Alert(
            tenant_id=tenant_id,
            external_id=external_id,
            rule_level=((src.get('rule') or {}).get('level') if isinstance(src.get('rule'), dict) else None),
            rule_description=((src.get('rule') or {}).get('description') if isinstance(src.get('rule'), dict) else None),
            agent_name=((src.get('agent') or {}).get('name') if isinstance(src.get('agent'), dict) else None),
            timestamp=src.get('@timestamp'),
            raw=json.dumps(src),
        )
        db.add(row)
        count += 1
    db.commit()
    return count


def process_sync_job(db: Session, payload: dict):
    tenant_id = int(payload['tenant_id'])
    sync_type = payload.get('sync_type', 'agents')
    _touch_sync_job(db, tenant_id, sync_type, 'running', 'worker started')
    if sync_type == 'agents':
        count = sync_agents(db, tenant_id)
    else:
        count = sync_alerts(db, tenant_id)
    _touch_sync_job(db, tenant_id, sync_type, 'completed', f'synced {count} records')
    safe_log_action(db, tenant_id, None, f'worker.sync.{sync_type}', f'synced {count} records')


def requeue_or_deadletter(r, queue_name: str, job: dict, exc: Exception):
    attempts = int(job.get('attempts', 0)) + 1
    job['attempts'] = attempts
    job['last_error'] = str(exc)
    if attempts >= settings.WORKER_MAX_RETRIES:
        r.rpush(QUEUE_DLQ, json.dumps(job))
    else:
        time.sleep(settings.WORKER_RETRY_DELAY_SECONDS)
        r.rpush(queue_name, json.dumps(job))


def periodic_sync_scheduler(r, db: Session):
    now = int(time.time())
    key = 'opensoc:ops:last_sync_tick'
    last = int(r.get(key) or 0)
    if now - last < settings.OPS_SYNC_INTERVAL_SECONDS:
        return
    tenants = db.query(Tenant).all()
    for tenant in tenants:
        r.rpush(QUEUE_SYNC, json.dumps({'tenant_id': tenant.id, 'sync_type': 'agents', 'attempts': 0}))
    r.set(key, now)


def main():
    r = redis.from_url(settings.REDIS_URL)
    while True:
        db = SessionLocal()
        try:
            periodic_sync_scheduler(r, db)
        finally:
            db.close()

        item = r.blpop([QUEUE_MAIN, QUEUE_SYNC], timeout=5)
        if not item:
            continue
        queue_name, raw = item
        queue_name = queue_name.decode() if isinstance(queue_name, bytes) else queue_name
        raw = raw.decode() if isinstance(raw, bytes) else raw
        job = json.loads(raw)
        db = SessionLocal()
        try:
            if queue_name == QUEUE_SYNC:
                process_sync_job(db, job)
            else:
                deliver_notification(db, job)
        except NotificationError as exc:
            requeue_or_deadletter(r, queue_name, job, exc)
            safe_log_action(db, job.get('tenant_id'), None, 'worker.notification.retry', str(exc))
        except Exception as exc:
            requeue_or_deadletter(r, queue_name, job, exc)
            safe_log_action(db, job.get('tenant_id'), None, 'worker.job.retry', str(exc))
        finally:
            db.close()
        time.sleep(0.1)


if __name__ == '__main__':
    main()
