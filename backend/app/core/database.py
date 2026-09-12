from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models.base import Base

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def create_tables() -> None:
    """Создаёт таблицы приложения при запуске сервиса."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Выдаёт SQLAlchemy-сессию и закрывает её после запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database() -> bool:
    """Проверяет доступность PostgreSQL простым SQL-запросом."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
