from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import check_database, create_tables, get_db
from app.routers import admin_settings, analytics, leads


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Создаёт таблицы приложения перед началом обработки запросов."""
    create_tables()
    yield


app = FastAPI(
    title="Orders Leads API",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(leads.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(admin_settings.router, prefix="/api")


@app.get("/health")
@app.get("/api/health")
def health() -> dict[str, str]:
    """Проверяет, что процесс FastAPI запущен."""
    return {"status": "ok"}


@app.get("/health/db")
@app.get("/api/health/db")
def database_health(db: Session = Depends(get_db)) -> dict[str, str]:
    """Проверяет доступность PostgreSQL через текущую сессию."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ok"}
