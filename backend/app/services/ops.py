from sqlalchemy.orm import Session
from app.models.models import Tenant, User, Endpoint, Alert, SyncJob
from app.services.queue import list_dead_letter


def collect_metrics(db: Session):
    return {
        'tenants': db.query(Tenant).count(),
        'users': db.query(User).count(),
        'endpoints': db.query(Endpoint).count(),
        'alerts': db.query(Alert).count(),
        'sync_jobs': db.query(SyncJob).count(),
        'dead_letter_jobs': len(list_dead_letter(100)),
    }
