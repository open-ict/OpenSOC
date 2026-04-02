from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.api.routes import router
from app.core.db import Base, engine, SessionLocal
from app.core.security import hash_password
from app.models.models import Tenant, User, Subscription, TenantPolicy
from app.services.ops import collect_metrics

app = FastAPI(title='OpenSOC SaaS v6')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(router)


@app.on_event('startup')
def startup():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        if not db.query(Tenant).first():
            tenant = Tenant(name='Default Tenant', slug='default', plan='starter')
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            user = User(email='admin@example.com', password_hash=hash_password('ChangeMe123!'), role='owner', tenant_id=tenant.id)
            db.add(user)
            db.add(Subscription(tenant_id=tenant.id, plan='starter', status='trial', endpoint_limit=50))
            db.add(TenantPolicy(tenant_id=tenant.id, min_alert_level=7, notifications_enabled=True, auto_sync_enabled=True))
            db.commit()
    finally:
        db.close()


@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'opensoc-api-v6'}


@app.get('/health/live')
def health_live():
    return {'status': 'alive'}


@app.get('/health/ready')
def health_ready():
    db = SessionLocal()
    try:
        db.execute(text('SELECT 1'))
        return {'status': 'ready', 'database': 'ok'}
    finally:
        db.close()


@app.get('/metrics')
def metrics_root():
    db = SessionLocal()
    try:
        return collect_metrics(db)
    finally:
        db.close()
