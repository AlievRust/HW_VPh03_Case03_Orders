from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.admin_user import AdminUser
from app.models.behavior_metric import BehaviorMetricCRUD
from app.schemas.behavior_metrics import (
    BehaviorMetricCreate,
    BehaviorStatsResponse,
)

router = APIRouter(prefix="/behavior-metrics", tags=["behavior-metrics"])

# Периоды статистики: ключ ответа -> число дней назад.
STATS_PERIODS = {"day": 1, "week": 7, "month": 30}


@router.post("/", status_code=status.HTTP_200_OK)
def submit_metrics(
    payload: BehaviorMetricCreate,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Принимает накопительные метрики визита с главной страницы.

    Публичный endpoint: посетители сайта не авторизованы.
    """
    BehaviorMetricCRUD.upsert(db, payload.model_dump())
    return {"status": "ok"}


@router.get("/stats", response_model=BehaviorStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> BehaviorStatsResponse:
    """Возвращает агрегаты времени по периодам и точки курсора для хитмэпа."""
    periods = {
        name: BehaviorMetricCRUD.period_stats(db, days)
        for name, days in STATS_PERIODS.items()
    }
    return BehaviorStatsResponse(
        periods=periods,
        total_sessions=BehaviorMetricCRUD.count(db),
        cursor_positions=BehaviorMetricCRUD.cursor_points(db),
    )
