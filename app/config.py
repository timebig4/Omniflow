from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Core
    database_url: str = "postgresql://postgres:postgres@localhost:5432/omniflow"
    redis_url: str = "redis://localhost:6379/0"

    # Telegram
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = "change-me"

    # Public base URL of this deployment (Railway gives you one, e.g.
    # https://omniflow-production.up.railway.app). Used to build webhook
    # ingest URLs shown to users and to register the Telegram webhook.
    public_base_url: str = "http://localhost:8000"

    # Used to encrypt credentials stored in the Credential table
    fernet_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
