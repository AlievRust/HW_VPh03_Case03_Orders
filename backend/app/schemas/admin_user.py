from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminUserCredentials(BaseModel):
    login: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=8, max_length=256)
    nickname: str = Field(min_length=1, max_length=150)


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    login: str
    nickname: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
