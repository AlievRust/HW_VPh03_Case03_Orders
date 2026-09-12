from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.admin_settings import AdminSetting, AdminSettingCRUD
from app.schemas.admin_settings import (
    AdminSettingCreate,
    AdminSettingRead,
    AdminSettingUpdate,
)

router = APIRouter(prefix="/admin-settings", tags=["admin-settings"])


@router.post("", response_model=AdminSettingRead, status_code=status.HTTP_201_CREATED)
def create_setting(
    payload: AdminSettingCreate,
    db: Session = Depends(get_db),
) -> AdminSetting:
    return AdminSettingCRUD.create(db, payload.model_dump())


@router.get("", response_model=list[AdminSettingRead])
def list_settings(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[AdminSetting]:
    return AdminSettingCRUD.list(db, skip=skip, limit=limit)


@router.get("/{setting_id}", response_model=AdminSettingRead)
def get_setting(setting_id: int, db: Session = Depends(get_db)) -> AdminSetting:
    setting = AdminSettingCRUD.get(db, setting_id)
    if setting is None:
        raise HTTPException(status_code=404, detail="Admin setting not found")
    return setting


@router.put("/{setting_id}", response_model=AdminSettingRead)
def update_setting(
    setting_id: int,
    payload: AdminSettingUpdate,
    db: Session = Depends(get_db),
) -> AdminSetting:
    setting = AdminSettingCRUD.get(db, setting_id)
    if setting is None:
        raise HTTPException(status_code=404, detail="Admin setting not found")
    return AdminSettingCRUD.update(db, setting, payload.model_dump())


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_setting(setting_id: int, db: Session = Depends(get_db)) -> None:
    setting = AdminSettingCRUD.get(db, setting_id)
    if setting is None:
        raise HTTPException(status_code=404, detail="Admin setting not found")
    AdminSettingCRUD.delete(db, setting)
