from pydantic import BaseModel

from app.schemas.admin_user import AdminUserRead


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminUserRead


class RegistrationStatus(BaseModel):
    can_register: bool
