from datetime import UTC, datetime, timedelta

import json

from sqlalchemy import Integer, String, Text, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.models.base import Base, TimestampMixin

# Сколько последних визитов учитывается при построении хитмэпа.
CURSOR_SESSIONS_LIMIT = 1000
# Верхняя граница точек в ответе статистики, чтобы не отдавать мегабайты JSON.
CURSOR_POINTS_LIMIT = 5000


class BehaviorMetric(Base, TimestampMixin):
    """Поведенческие метрики одного визита главной страницы.

    Клиент шлёт накопительные данные раз в секунду, строка визита
    обновляется по session_id (upsert), а не создаётся заново.
    """

    __tablename__ = "behavior_metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    application_id: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    time_on_page: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # JSON-строка вида {"кнопка": счётчик} — тип поля оставлен строкой по контракту API.
    buttons_clicked: Mapped[str] = mapped_column(Text, default="", nullable=False)
    # JSON-строка вида [{"x": 12.5, "y": 40.0}] — координаты в процентах окна (0–100).
    cursor_positions: Mapped[str] = mapped_column(Text, default="", nullable=False)
    return_frequency: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class BehaviorMetricCRUD:
    """Запись метрик визитов и агрегаты для статистики админ-панели."""

    @staticmethod
    def upsert(db: Session, data: dict) -> BehaviorMetric:
        """Создаёт строку визита или обновляет существующую по session_id."""
        metric = db.scalar(
            select(BehaviorMetric).where(BehaviorMetric.session_id == data["session_id"])
        )
        if metric is None:
            metric = BehaviorMetric(**data)
            db.add(metric)
        else:
            for field, value in data.items():
                setattr(metric, field, value)
        db.commit()
        db.refresh(metric)
        return metric

    @staticmethod
    def count(db: Session) -> int:
        return db.scalar(select(func.count()).select_from(BehaviorMetric)) or 0

    @staticmethod
    def period_stats(db: Session, days: int) -> dict:
        """Среднее/максимальное время и число визитов за последние `days` дней."""
        since = datetime.now(UTC) - timedelta(days=days)
        row = db.execute(
            select(
                func.avg(BehaviorMetric.time_on_page),
                func.max(BehaviorMetric.time_on_page),
                func.count(),
            ).where(BehaviorMetric.updated_at >= since)
        ).one()
        avg_time, max_time, sessions = row
        return {
            "avg_time_on_page": int(round(avg_time)) if avg_time is not None else 0,
            "max_time_on_page": int(max_time) if max_time is not None else 0,
            "sessions": int(sessions),
        }

    @staticmethod
    def cursor_points(db: Session) -> list[dict]:
        """Собирает точки курсора из последних визитов для хитмэпа."""
        rows = db.scalars(
            select(BehaviorMetric.cursor_positions)
            .order_by(BehaviorMetric.updated_at.desc())
            .limit(CURSOR_SESSIONS_LIMIT)
        ).all()

        points: list[dict] = []
        for raw in rows:
            try:
                parsed = json.loads(raw) if raw else []
            except (TypeError, ValueError):
                continue  # битые данные одного визита не ломают всю статистику
            if not isinstance(parsed, list):
                continue
            for point in parsed:
                if not isinstance(point, dict):
                    continue
                x, y = point.get("x"), point.get("y")
                if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                    continue
                if not (0 <= x <= 100 and 0 <= y <= 100):
                    continue
                points.append({"x": round(float(x), 2), "y": round(float(y), 2)})
                if len(points) >= CURSOR_POINTS_LIMIT:
                    return points
        return points
