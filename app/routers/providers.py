from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Optional
from app import models, schemas
from app.deps import get_db

router = APIRouter(prefix="/providers", tags=["Providers"])


def next_available_slot(db: Session, provider_id: int):
    return (
        db.query(models.AppointmentSlot)
        .filter(
            models.AppointmentSlot.provider_id == provider_id,
            models.AppointmentSlot.is_available.is_(True),
            models.AppointmentSlot.start_time >= func.now(),
        )
        .order_by(models.AppointmentSlot.start_time.asc())
        .first()
    )


@router.get("/", response_model=list[schemas.ProviderSummary])
def list_providers(
    state: Optional[str] = None,
    insurance: Optional[str] = None,
    specialty: Optional[str] = None,
    accepting_new_patients: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Provider)
    if state:
        query = query.filter(models.Provider.state == state)
    if insurance:
        query = query.filter(models.Provider.accepted_insurance.ilike(f"%{insurance}%"))
    if specialty:
        query = query.filter(models.Provider.specialty.ilike(f"%{specialty}%"))
    if accepting_new_patients is not None:
        query = query.filter(models.Provider.accepting_new_patients == accepting_new_patients)
    providers = query.all()

    results = []
    for provider in providers:
        next_slot = next_available_slot(db, provider.id)
        results.append(
            schemas.ProviderSummary(
                id=provider.id,
                full_name=provider.full_name,
                specialty=provider.specialty,
                state=provider.state,
                accepting_new_patients=provider.accepting_new_patients,
                headline=schemas.provider_headline(provider.bio),
                next_available_slot=next_slot.start_time if next_slot else None,
            )
        )
    return results


@router.get("/{provider_id}", response_model=schemas.ProviderDetail)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(models.Provider).filter(models.Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    available_slots = (
        db.query(models.AppointmentSlot)
        .filter(
            models.AppointmentSlot.provider_id == provider_id,
            models.AppointmentSlot.is_available.is_(True),
            models.AppointmentSlot.start_time >= func.now(),
        )
        .order_by(models.AppointmentSlot.start_time.asc())
        .all()
    )

    return schemas.ProviderDetail(
        id=provider.id,
        full_name=provider.full_name,
        specialty=provider.specialty,
        state=provider.state,
        location=provider.location,
        accepted_insurance=provider.accepted_insurance,
        available_days=provider.available_days,
        accepting_new_patients=provider.accepting_new_patients,
        languages=provider.languages,
        bio=provider.bio,
        years_experience=provider.years_experience,
        created_at=provider.created_at,
        available_slots=[schemas.AppointmentSlotOut.model_validate(s) for s in available_slots],
    )
