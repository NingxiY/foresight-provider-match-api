from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app import models, schemas
from app.deps import get_db, get_current_user, require_admin

router = APIRouter(prefix="/appointment-requests", tags=["Appointments"])

# Statuses in which a slot is considered released back to the pool.
_SLOT_RELEASING_STATUSES = {models.AppointmentStatus.declined, models.AppointmentStatus.cancelled}


@router.post("/", response_model=schemas.AppointmentRequestOut, status_code=201)
def create_appointment(
    payload: schemas.AppointmentRequestCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    provider = db.query(models.Provider).filter(models.Provider.id == payload.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    slot = (
        db.query(models.AppointmentSlot)
        .filter(
            models.AppointmentSlot.id == payload.slot_id,
            models.AppointmentSlot.provider_id == payload.provider_id,
        )
        .first()
    )
    if not slot:
        raise HTTPException(status_code=404, detail="Appointment slot not found")
    if not slot.is_available:
        raise HTTPException(status_code=409, detail="This appointment slot has already been booked.")

    slot.is_available = False
    appt = models.AppointmentRequest(
        patient_id=current_user.id,
        provider_id=payload.provider_id,
        slot_id=payload.slot_id,
        reason=payload.reason,
    )
    db.add(appt)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This appointment slot has already been booked.")
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


@router.get("/", response_model=list[schemas.AppointmentRequestOut])
def list_all_appointments(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    return db.query(models.AppointmentRequest).order_by(models.AppointmentRequest.created_at.desc()).all()


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
    if payload.status in _SLOT_RELEASING_STATUSES and appt.slot_id is not None:
        slot = db.query(models.AppointmentSlot).filter(models.AppointmentSlot.id == appt.slot_id).first()
        if slot:
            slot.is_available = True
        appt.slot_id = None

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

    if appt.slot_id is not None:
        slot = db.query(models.AppointmentSlot).filter(models.AppointmentSlot.id == appt.slot_id).first()
        if slot:
            slot.is_available = True

    db.delete(appt)
    db.commit()
