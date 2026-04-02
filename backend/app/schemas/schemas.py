from pydantic import BaseModel, EmailStr


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class IntegrationIn(BaseModel):
    provider: str
    base_url: str
    username: str
    password: str
    verify_ssl: bool = False


class NotificationChannelIn(BaseModel):
    type: str
    target: str
    enabled: bool = True


class RotateSecretIn(BaseModel):
    username: str | None = None
    password: str


class PolicyIn(BaseModel):
    min_alert_level: int = 7
    notifications_enabled: bool = True
    auto_sync_enabled: bool = True
