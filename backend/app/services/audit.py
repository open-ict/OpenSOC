from sqlalchemy.orm import Session
from app.models.models import AuditLog


def log_action(db: Session, tenant_id: int | None, actor_email: str | None, action: str, detail: str = ''):
    db.add(AuditLog(tenant_id=tenant_id, actor_email=actor_email, action=action, detail=detail))
    db.commit()


def safe_log_action(db: Session, tenant_id: int | None, actor_email: str | None, action: str, detail: str = ''):
    try:
        log_action(db, tenant_id, actor_email, action, detail)
    except Exception:
        db.rollback()
