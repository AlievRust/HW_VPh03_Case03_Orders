from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    get_current_admin,
    hash_password,
    verify_password,
)
from app.models.admin_user import AdminUser, AdminUserCRUD
from app.schemas.admin_user import AdminUserCredentials, AdminUserRead
from app.schemas.auth import LoginRequest, RegistrationStatus, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def create_admin(db: Session, credentials: AdminUserCredentials) -> AdminUser:
    """Создаёт администратора и преобразует конфликт логина в понятную ошибку."""
    try:
        return AdminUserCRUD.create(
            db,
            {
                "login": credentials.login,
                "nickname": credentials.nickname,
                "password_hash": hash_password(credentials.password),
            },
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Login already exists") from exc


@router.get("/registration-status", response_model=RegistrationStatus)
def registration_status(db: Session = Depends(get_db)) -> RegistrationStatus:
    """Проверяет, доступна ли первичная публичная регистрация."""
    return RegistrationStatus(can_register=not AdminUserCRUD.count(db))


@router.post("/register", response_model=AdminUserRead, status_code=status.HTTP_201_CREATED)
def register_first_admin(
    credentials: AdminUserCredentials,
    db: Session = Depends(get_db),
) -> AdminUser:
    """Регистрирует первого администратора, пока таблица пуста."""
    if AdminUserCRUD.count(db):
        raise HTTPException(status_code=403, detail="Public registration is closed")
    return create_admin(db, credentials)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Проверяет учётные данные и выдаёт access JWT."""
    admin = AdminUserCRUD.get_by_login(db, payload.login)
    if admin is None or not admin.is_active or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid login or password")
    return TokenResponse(access_token=create_access_token(admin.id), admin=admin)


@router.get("/me", response_model=AdminUserRead)
def me(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
    """Возвращает текущего администратора."""
    return admin


@router.post("/admins", response_model=AdminUserRead, status_code=status.HTTP_201_CREATED)
def create_admin_user(
    credentials: AdminUserCredentials,
    db: Session = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
) -> AdminUser:
    """Создаёт администратора из защищённой панели."""
    return create_admin(db, credentials)
