from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # App Settings
    app_name: str = "ParodyWall API"
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=True, validation_alias="DEBUG")
    allowed_origins: str = Field(default="http://localhost:3000", validation_alias="ALLOWED_ORIGINS")

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
    # AWS S3
    aws_access_key_id: str = Field(validation_alias="AWS_ACCESS_KEY_ID", default="")
    aws_secret_access_key: str = Field(validation_alias="AWS_SECRET_ACCESS_KEY", default="")
    aws_region_name: str = Field(validation_alias="AWS_REGION_NAME", default="us-east-1")
    aws_s3_bucket_name: str = Field(validation_alias="AWS_S3_BUCKET_NAME", default="")

    # Turnstile
    turnstile_secret_key: str = Field(validation_alias="TURNSTILE_SECRET_KEY", default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
