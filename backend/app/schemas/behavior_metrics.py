from pydantic import BaseModel, Field


class BehaviorMetricCreate(BaseModel):
    """Тело POST-запроса метрик с главной страницы.

    application_id и return_frequency — заглушки под будущие интеграции,
    всегда приходят 0. buttons_clicked и cursor_positions — JSON-строки
    по контракту API.
    """

    session_id: str = Field(min_length=8, max_length=64)
    application_id: int = Field(default=0, ge=0)
    time_on_page: int = Field(default=0, ge=0)
    buttons_clicked: str = ""
    cursor_positions: str = ""
    return_frequency: int = Field(default=0, ge=0)


class BehaviorPeriodStats(BaseModel):
    avg_time_on_page: int
    max_time_on_page: int
    sessions: int


class BehaviorStatsResponse(BaseModel):
    periods: dict[str, BehaviorPeriodStats]
    total_sessions: int
    cursor_positions: list[dict]
