from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения и параметры подключения к PostgreSQL."""

    postgres_db: str = "orders"
    postgres_user: str = "orders_app"
    postgres_password: str = ""
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        """Формирует URL драйвера PostgreSQL для SQLAlchemy."""
        return (
            "postgresql+psycopg://"
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
