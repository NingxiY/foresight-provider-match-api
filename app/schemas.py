from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models import UserRole, AppointmentStatus


# --- User ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.patient


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


# --- Auth ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# --- Provider ---
class ProviderOut(BaseModel):
    id: int
    full_name: str
    specialty: str
    state: str
    location: str
    accepted_insurance: Optional[str]
    available_days: Optional[str]
    accepting_new_patients: bool
    languages: Optional[str]
    bio: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Provider Match ---
class ProviderMatchCreate(BaseModel):
    state: str
    insurance: Optional[str] = None
    concern: str
    preferred_day: Optional[str] = None


class ProviderScore(BaseModel):
    provider: ProviderOut
    score: int


class ProviderMatchOut(BaseModel):
    id: int
    patient_id: int
    state: str
    insurance: Optional[str]
    concern: str
    preferred_day: Optional[str]
    matched_providers: list[ProviderScore]

    class Config:
        from_attributes = True


# --- Appointment Request ---
class AppointmentRequestCreate(BaseModel):
    provider_id: int
    preferred_date: Optional[str] = None
    reason: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentRequestOut(BaseModel):
    id: int
    patient_id: int
    provider_id: int
    preferred_date: Optional[str]
    reason: Optional[str]
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
