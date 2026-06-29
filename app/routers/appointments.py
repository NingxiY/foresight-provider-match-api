from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user, require_admin

router = APIRouter(prefix="/appointment-requests", tags=["Appointments"])


@router.post("/", response_model=schemas.AppointmentRequestOut, status_code=201)
def create_appointment(
    payload: schemas.AppointmentRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    provider = db.query(models.Provider).filter(models.Provider.id == payload.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    appt = models.AppointmentRequest(
        patient_id=current_user.id,
        provider_id=payload.provider_id,
        preferred_date=payload.preferred_date,
        reason=payload.reason,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@router.get("/me", response_model=list[schemas.AppointmentRequestOut])
def my_appointments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.AppointmentRequest)
        .filter(models.AppointmentRequest.patient_id == current_user.id)
        .all()
    )


@router.patch("/{request_id}/status", response_model=schemas.AppointmentRequestOut)
def update_status(
    request_id: int,
    payload: schemas.AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    appt = db.query(models.AppointmentRequest).filter(models.AppointmentRequest.id == request_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment request not found")
    appt.status = payload.status
    db.commit()
    db.refresh(appt)
    return appt


@router.delete("/{request_id}", status_code=204)
def delete_appointment(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    appt = db.query(models.AppointmentRequest).filter(models.AppointmentRequest.id == request_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment request not found")
    if current_user.role != models.UserRole.admin and appt.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete another patient's request")
    db.delete(appt)
    db.commit()
