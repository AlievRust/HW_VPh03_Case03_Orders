from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AnalyticsBase(BaseModel):
    time_on_page_seconds: int = Field(default=0, ge=0)
    button_clicks: int = Field(default=0, ge=0)
    cursor_pauses: int = Field(default=0, ge=0)
    return_visits: int = Field(default=0, ge=0)
    events: list[dict[str, Any]] = Field(default_factory=list)
    technical_info: dict[str, Any] = Field(default_factory=dict)


class AnalyticsCreate(AnalyticsBase):
    lead_id: int


class AnalyticsUpdate(AnalyticsBase):
    pass


class AnalyticsRead(AnalyticsBase):
    model_config = ConfigDict(from_attributes=True)

    lead_id: int
    created_at: datetime
    updated_at: datetime
