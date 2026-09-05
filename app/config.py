import logging
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings
    """

    # Application settings
    APP_NAME: str = Field(env='APP_NAME', default='Smalim Ecom')
    DEBUG: bool = Field(env='DEBUG', default=False)
    SECRET_KEY: str = Field(env='SECRET_KEY', default='')

    LOG_LEVEL: str = Field(env='LOG_LEVEL', default='INFO')

    # Database settings
    POSTGRES_HOST: str = Field(env='POSTGRES_HOST', default='localhost')
    POSTGRES_PORT: int = Field(env='POSTGRES_PORT', default=5432)
    POSTGRES_DB: str = Field(env='POSTGRES_DB', default='app_db')
    POSTGRES_USER: str = Field(env='POSTGRES_USER', default='app_user')
    POSTGRES_PASSWORD: str = Field(
        env='POSTGRES_PASSWORD', default='app_password')

    # Database pool settings
    DB_POOL_SIZE: int = Field(env='DB_POOL_SIZE', default=10)
    DB_MAX_OVERFLOW: int = Field(env='DB_MAX_OVERFLOW', default=20)
    DB_POOL_TIMEOUT: int = Field(env='DB_POOL_TIMEOUT', default=30)
    DB_ECHO: bool = Field(env='DB_ECHO', default=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("POSTGRES_PASSWORD")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate that password is not empty."""
        if not v:
            raise ValueError("Password cannot be empty")
        return v

    @property
    def database_url(self) -> str:
        """Get async database URL for asyncpg."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


# Singleton instance
settings = Settings()


# Configure logging based on settings
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# Dependency injection function
def get_settings() -> Settings:
    """Get settings instance for dependency injection."""
    return settings
