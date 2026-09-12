from sqlalchemy import ForeignKey, Integer, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class LeadAnalytics(Base, TimestampMixin):
    """Агрегированная и техническая аналитика заявки.

    SQL:
        CREATE TABLE lead_analytics (
            lead_id INTEGER PRIMARY KEY REFERENCES leads(id) ON DELETE CASCADE,
            time_on_page_seconds INTEGER NOT NULL DEFAULT 0,
            button_clicks INTEGER NOT NULL DEFAULT 0,
            cursor_pauses INTEGER NOT NULL DEFAULT 0,
            return_visits INTEGER NOT NULL DEFAULT 0,
            events JSONB NOT NULL DEFAULT '[]',
            technical_info JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """

    __tablename__ = "lead_analytics"

    lead_id: Mapped[int] = mapped_column(
        ForeignKey("leads.id", ondelete="CASCADE"), primary_key=True
    )
    time_on_page_seconds: Mapped[int] = mapped_column(Integer, default=0)
    button_clicks: Mapped[int] = mapped_column(Integer, default=0)
    cursor_pauses: Mapped[int] = mapped_column(Integer, default=0)
    return_visits: Mapped[int] = mapped_column(Integer, default=0)
    events: Mapped[list] = mapped_column(JSONB, default=list)
    technical_info: Mapped[dict] = mapped_column(JSONB, default=dict)

    lead = relationship("Lead", back_populates="analytics")


class LeadAnalyticsCRUD:
    """CRUD-операции для аналитики заявок."""

    @staticmethod
    def create(db: Session, data: dict) -> LeadAnalytics:
        analytics = LeadAnalytics(**data)
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
        return analytics

    @staticmethod
    def get(db: Session, lead_id: int) -> LeadAnalytics | None:
        return db.get(LeadAnalytics, lead_id)

    @staticmethod
    def update(db: Session, analytics: LeadAnalytics, data: dict) -> LeadAnalytics:
        for field, value in data.items():
            setattr(analytics, field, value)
        db.commit()
        db.refresh(analytics)
        return analytics

    @staticmethod
    def delete(db: Session, analytics: LeadAnalytics) -> None:
        db.delete(analytics)
        db.commit()
