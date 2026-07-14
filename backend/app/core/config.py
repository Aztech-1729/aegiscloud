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

    LEMON_SQUEEZY_API_KEY: str = "ls_test_placeholder"
    LEMON_SQUEEZY_WEBHOOK_SECRET: str = "whsec_placeholder"
    LEMON_SQUEEZY_STORE_ID: str = "store_id_placeholder"
    LEMON_SQUEEZY_VARIANTS: dict = {
        "pro": "variant_pro_monthly",
        "business": "variant_business_monthly",
        "enterprise": "variant_enterprise_monthly",
    }

    GOOGLE_CLIENT_ID: str = "1054542396762-3kn4smausm4s9cpqdrtok8upk6ldjvd7.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    OPENAI_API_KEY: str = "sk-S2Xl3ZHCIQgBy3fV4sO8B041jNzxW2tnukEcVl31ofjbMpYfWfqnI2cFMLEPKJAp"
    OPENAI_API_BASE: str = "https://opencode.ai/zen/v1"
    OPENAI_MODEL: str = "deepseek-v4-flash-free"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@aegiscloud.io"

    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    LEMONSQUEEZY_API_KEY: str = ""
    LEMONSQUEEZY_STORE_ID: str = ""
    LEMONSQUEEZY_WEBHOOK_SECRET: str = ""
    LEMONSQUEEZY_PRO_MONTHLY_ID: str = ""
    LEMONSQUEEZY_PRO_YEARLY_ID: str = ""
    LEMONSQUEEZY_BUSINESS_MONTHLY_ID: str = ""
    LEMONSQUEEZY_BUSINESS_YEARLY_ID: str = ""

    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_DEVICES_FREE: int = 2
    MAX_DEVICES_PRO: int = 10
    MAX_DEVICES_BUSINESS: int = 50

    PAIR_CODE_EXPIRY_MINUTES: int = 10
    TASK_TIMEOUT_SECONDS: int = 300
    HEARTBEAT_INTERVAL_SECONDS: int = 30

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}


settings = Settings()
