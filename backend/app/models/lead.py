from datetime import datetime

from sqlalchemy import String, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Lead(Base, TimestampMixin):
    """Заявка клиента.

    SQL:
        CREATE TABLE leads (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            middle_name VARCHAR(100),
            contact_value VARCHAR(255) NOT NULL,
            business_niche VARCHAR(255) NOT NULL,
            company_size VARCHAR(100) NOT NULL,
            business_info TEXT,
            task_volume VARCHAR(255) NOT NULL,
            budget VARCHAR(100) NOT NULL,
            result_deadline VARCHAR(100) NOT NULL,
            customer_role VARCHAR(100) NOT NULL,
            task_type VARCHAR(255) NOT NULL,
            product_interest VARCHAR(255) NOT NULL,
            contact_method VARCHAR(100) NOT NULL,
            preferred_time VARCHAR(100) NOT NULL,
            comments TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(100))
    contact_value: Mapped[str] = mapped_column(String(255), nullable=False)
    business_niche: Mapped[str] = mapped_column(String(255), nullable=False)
    company_size: Mapped[str] = mapped_column(String(100), nullable=False)
    business_info: Mapped[str | None] = mapped_column(Text)
    task_volume: Mapped[str] = mapped_column(String(255), nullable=False)
    budget: Mapped[str] = mapped_column(String(100), nullable=False)
    result_deadline: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_role: Mapped[str] = mapped_column(String(100), nullable=False)
    task_type: Mapped[str] = mapped_column(String(255), nullable=False)
    product_interest: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_method: Mapped[str] = mapped_column(String(100), nullable=False)
    preferred_time: Mapped[str] = mapped_column(String(100), nullable=False)
    comments: Mapped[str | None] = mapped_column(Text)

    analytics = relationship(
        "LeadAnalytics", back_populates="lead", uselist=False,
        cascade="all, delete-orphan"
    )


class LeadCRUD:
    """CRUD-операции для заявок клиентов."""

    @staticmethod
    def create(db: Session, data: dict) -> Lead:
        lead = Lead(**data)
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def get(db: Session, lead_id: int) -> Lead | None:
        return db.get(Lead, lead_id)

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> list[Lead]:
        return list(db.scalars(select(Lead).offset(skip).limit(limit)))

    @staticmethod
    def update(db: Session, lead: Lead, data: dict) -> Lead:
        for field, value in data.items():
            setattr(lead, field, value)
        db.commit()
        db.refresh(lead)
        return lead

    @staticmethod
    def delete(db: Session, lead: Lead) -> None:
        db.delete(lead)
        db.commit()
