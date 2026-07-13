from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Aegis Cloud"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://aegis:aegis_secret_2024@localhost:5432/aegis_cloud"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "aegis-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    STRIPE_SECRET_KEY: str = "sk_test_placeholder"
    STRIPE_WEBHOOK_SECRET: str = "whsec_placeholder"
    STRIPE_PRICES: dict = {
        "pro": "price_pro_monthly",
        "business": "price_business_monthly",
        "enterprise": "price_enterprise_monthly",
    }

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@aegiscloud.io"

    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_DEVICES_FREE: int = 2
    MAX_DEVICES_PRO: int = 10
    MAX_DEVICES_BUSINESS: int = 50

    PAIR_CODE_EXPIRY_MINUTES: int = 10
    TASK_TIMEOUT_SECONDS: int = 300
    HEARTBEAT_INTERVAL_SECONDS: int = 30

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
