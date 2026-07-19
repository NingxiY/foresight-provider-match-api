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


# --- Appointment Slot ---
class AppointmentSlotOut(BaseModel):
    id: int
    provider_id: int
    start_time: datetime
    end_time: datetime
    is_available: bool

    class Config:
        from_attributes = True


# --- Provider ---
def provider_headline(bio: Optional[str]) -> Optional[str]:
    if not bio:
        return None
    return bio if len(bio) <= 80 else bio[:77].rstrip() + "..."


class ProviderSummary(BaseModel):
    """Lightweight provider info for list/search results (mirrors a provider search results page)."""

    id: int
    full_name: str
    specialty: str
    state: str
    accepting_new_patients: bool
    headline: Optional[str] = None
    next_available_slot: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProviderDetail(BaseModel):
    """Full provider info for a provider detail page."""

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
    years_experience: Optional[int]
    created_at: datetime
    available_slots: list[AppointmentSlotOut] = []

    class Config:
        from_attributes = True


# --- Provider Match ---
class ProviderMatchCreate(BaseModel):
    state: str
    insurance: Optional[str] = None
    concern: str
    preferred_day: Optional[str] = None


class ProviderScore(BaseModel):
    provider: ProviderSummary
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
    slot_id: int
    reason: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentRequestOut(BaseModel):
    id: int
    patient_id: int
    provider_id: int
    slot: Optional[AppointmentSlotOut] = None
    reason: Optional[str]
    status: AppointmentStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
