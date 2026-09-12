from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models.analytics import LeadAnalytics
from app.models.lead import Lead, LeadCRUD
from app.schemas.lead import LeadCreate, LeadRead, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])


def get_lead_or_404(db: Session, lead_id: int) -> Lead:
    lead = db.get(
        Lead,
        lead_id,
        options=[selectinload(Lead.analytics)],
    )
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)) -> Lead:
    lead_data = payload.model_dump(exclude={"analytics"})
    try:
        lead = LeadCRUD.create(db, lead_data)
        if payload.analytics is not None:
            analytics = LeadAnalytics(
                lead_id=lead.id,
                **payload.analytics.model_dump(),
            )
            db.add(analytics)
            db.commit()
            db.refresh(lead)
        return get_lead_or_404(db, lead.id)
    except Exception:
        db.rollback()
        raise


@router.get("", response_model=list[LeadRead])
def list_leads(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Lead]:
    return list(
        db.query(Lead)
        .options(selectinload(Lead.analytics))
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: int, db: Session = Depends(get_db)) -> Lead:
    return get_lead_or_404(db, lead_id)


@router.put("/{lead_id}", response_model=LeadRead)
def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
) -> Lead:
    lead = get_lead_or_404(db, lead_id)
    updated = LeadCRUD.update(db, lead, payload.model_dump())
    return get_lead_or_404(db, updated.id)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: int, db: Session = Depends(get_db)) -> None:
    lead = get_lead_or_404(db, lead_id)
    LeadCRUD.delete(db, lead)
