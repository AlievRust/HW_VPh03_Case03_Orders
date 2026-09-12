from sqlalchemy import Boolean, Integer, String, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.models.base import Base, TimestampMixin


class AdminSetting(Base, TimestampMixin):
    """Настройка услуги и диапазона бюджета для frontend.

    SQL:
        CREATE TABLE admin_settings (
            id SERIAL PRIMARY KEY,
            service_name VARCHAR(255) NOT NULL,
            service_description TEXT,
            budget_min INTEGER NOT NULL,
            budget_max INTEGER NOT NULL,
            budget_step INTEGER NOT NULL DEFAULT 1,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """

    __tablename__ = "admin_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    service_description: Mapped[str | None] = mapped_column(Text)
    budget_min: Mapped[int] = mapped_column(Integer, nullable=False)
    budget_max: Mapped[int] = mapped_column(Integer, nullable=False)
    budget_step: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class AdminSettingCRUD:
    """CRUD-операции для административных настроек."""

    @staticmethod
    def create(db: Session, data: dict) -> AdminSetting:
        setting = AdminSetting(**data)
        db.add(setting)
        db.commit()
        db.refresh(setting)
        return setting

    @staticmethod
    def get(db: Session, setting_id: int) -> AdminSetting | None:
        return db.get(AdminSetting, setting_id)

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> list[AdminSetting]:
        return list(db.scalars(select(AdminSetting).offset(skip).limit(limit)))

    @staticmethod
    def update(db: Session, setting: AdminSetting, data: dict) -> AdminSetting:
        for field, value in data.items():
            setattr(setting, field, value)
        db.commit()
        db.refresh(setting)
        return setting

    @staticmethod
    def delete(db: Session, setting: AdminSetting) -> None:
        db.delete(setting)
        db.commit()
