from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.analytics import AnalyticsBase, AnalyticsRead


class LeadBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    contact_value: str = Field(min_length=1, max_length=255)
    business_niche: str = Field(min_length=1, max_length=255)
    company_size: str = Field(min_length=1, max_length=100)
    business_info: str | None = None
    task_volume: str = Field(min_length=1, max_length=255)
    budget: str = Field(min_length=1, max_length=100)
    result_deadline: str = Field(min_length=1, max_length=100)
    customer_role: str = Field(min_length=1, max_length=100)
    task_type: str = Field(min_length=1, max_length=255)
    product_interest: str = Field(min_length=1, max_length=255)
    contact_method: str = Field(min_length=1, max_length=100)
    preferred_time: str = Field(min_length=1, max_length=100)
    comments: str | None = None


class LeadCreate(LeadBase):
    analytics: AnalyticsBase | None = None


class LeadUpdate(LeadBase):
    pass


class LeadRead(LeadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    analytics: AnalyticsRead | None = None
