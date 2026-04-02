from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    FERNET_KEY: str
    APP_BASE_URL: str = 'http://localhost:8000'
    FRONTEND_URL: str = 'http://localhost:5173'
    DEFAULT_RATE_LIMIT_PER_MINUTE: int = 120
    OPS_SYNC_INTERVAL_SECONDS: int = 300
    WORKER_MAX_RETRIES: int = 5
    WORKER_RETRY_DELAY_SECONDS: int = 10

    WAZUH_API_URL: str = ''
    WAZUH_API_USER: str = ''
    WAZUH_API_PASSWORD: str = ''
    WAZUH_INDEXER_URL: str = ''
    WAZUH_INDEXER_USER: str = ''
    WAZUH_INDEXER_PASSWORD: str = ''
    WAZUH_VERIFY_SSL: bool = False

    SMTP_HOST: str = ''
    SMTP_PORT: int = 587
    SMTP_USER: str = ''
    SMTP_PASSWORD: str = ''
    SMTP_FROM: str = 'alerts@example.com'
    SMTP_TLS: bool = True

    OIDC_ENABLED: bool = False
    OIDC_ISSUER: str = ''
    OIDC_CLIENT_ID: str = ''
    OIDC_CLIENT_SECRET: str = ''
    OIDC_REDIRECT_URI: str = ''
    OIDC_SCOPES: str = 'openid profile email'


settings = Settings()
