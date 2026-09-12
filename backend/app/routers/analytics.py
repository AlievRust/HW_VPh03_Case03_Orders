from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analytics import LeadAnalytics, LeadAnalyticsCRUD
from app.models.lead import Lead
from app.schemas.analytics import AnalyticsCreate, AnalyticsRead, AnalyticsUpdate

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("", response_model=AnalyticsRead, status_code=status.HTTP_201_CREATED)
def create_analytics(
    payload: AnalyticsCreate,
    db: Session = Depends(get_db),
) -> LeadAnalytics:
    if db.get(Lead, payload.lead_id) is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    if LeadAnalyticsCRUD.get(db, payload.lead_id) is not None:
        raise HTTPException(status_code=409, detail="Analytics already exists")
    return LeadAnalyticsCRUD.create(db, payload.model_dump())


@router.get("/{lead_id}", response_model=AnalyticsRead)
def get_analytics(lead_id: int, db: Session = Depends(get_db)) -> LeadAnalytics:
    analytics = LeadAnalyticsCRUD.get(db, lead_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Analytics not found")
    return analytics


@router.put("/{lead_id}", response_model=AnalyticsRead)
def update_analytics(
    lead_id: int,
    payload: AnalyticsUpdate,
    db: Session = Depends(get_db),
) -> LeadAnalytics:
    analytics = LeadAnalyticsCRUD.get(db, lead_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Analytics not found")
    return LeadAnalyticsCRUD.update(db, analytics, payload.model_dump())


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analytics(lead_id: int, db: Session = Depends(get_db)) -> None:
    analytics = LeadAnalyticsCRUD.get(db, lead_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Analytics not found")
    LeadAnalyticsCRUD.delete(db, analytics)
