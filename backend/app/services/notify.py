import smtplib
from email.message import EmailMessage
import httpx
from app.core.config import settings


class NotificationError(Exception):
    pass


def send_email(target: str, subject: str, body: str):
    if not settings.SMTP_HOST:
        return {'skipped': True, 'reason': 'SMTP not configured'}
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = settings.SMTP_FROM
    msg['To'] = target
    msg.set_content(body)
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as exc:
        raise NotificationError(f'email delivery failed: {exc}') from exc
    return {'sent': True}


def send_webhook(target: str, payload: dict):
    try:
        with httpx.Client(timeout=15) as client:
            r = client.post(target, json=payload)
            r.raise_for_status()
        return {'sent': True, 'status_code': r.status_code}
    except Exception as exc:
        raise NotificationError(f'webhook delivery failed: {exc}') from exc
