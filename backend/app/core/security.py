from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
fernet = Fernet(settings.FERNET_KEY.encode())


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(subject: str, tenant_id: int, role: str) -> str:
    payload = {
        'sub': subject,
        'tenant_id': tenant_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=12),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


def encrypt_secret(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()
