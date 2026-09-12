from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AdminSettingBase(BaseModel):
    service_name: str = Field(min_length=1, max_length=255)
    service_description: str | None = None
    budget_min: int = Field(ge=0)
    budget_max: int = Field(ge=0)
    budget_step: int = Field(default=1, gt=0)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_budget_range(self):
        if self.budget_max < self.budget_min:
            raise ValueError("budget_max must be greater than or equal to budget_min")
        return self


class AdminSettingCreate(AdminSettingBase):
    pass


class AdminSettingUpdate(AdminSettingBase):
    pass


class AdminSettingRead(AdminSettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
