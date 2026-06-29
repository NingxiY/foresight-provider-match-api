from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app import models, schemas
from app.deps import get_db

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("/", response_model=list[schemas.ProviderOut])
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
    return query.all()


@router.get("/{provider_id}", response_model=schemas.ProviderOut)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.query(models.Provider).filter(models.Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider
