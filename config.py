from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # App Settings
    app_name: str = "ParodyWall API"
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=True, validation_alias="DEBUG")

    # Database
    database_url: str = Field(validation_alias="DATABASE_URL")

    # JWT Authentication
    secret_key: str = Field(validation_alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", validation_alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=60 * 24 * 7, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    # 7 days

    # Email Service
    resend_api_key: str = Field(validation_alias="RESEND_API_KEY")
    resend_from_email: str = Field(validation_alias="RESEND_FROM_EMAIL")
    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
