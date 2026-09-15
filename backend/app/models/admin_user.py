from sqlalchemy import Boolean, String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.models.base import Base, TimestampMixin


class AdminUser(Base, TimestampMixin):
    """Администратор панели управления услугами."""

    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(150), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class AdminUserCRUD:
    """CRUD-операции администраторов."""

    @staticmethod
    def count(db: Session) -> int:
        return db.scalar(select(func.count()).select_from(AdminUser)) or 0

    @staticmethod
    def get_by_login(db: Session, login: str) -> AdminUser | None:
        return db.scalar(select(AdminUser).where(AdminUser.login == login))

    @staticmethod
    def get(db: Session, user_id: int) -> AdminUser | None:
        return db.get(AdminUser, user_id)

    @staticmethod
    def create(db: Session, data: dict) -> AdminUser:
        user = AdminUser(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
