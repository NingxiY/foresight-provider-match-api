from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    patient = "patient"
    admin = "admin"


class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.patient, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match_requests = relationship("ProviderMatchRequest", back_populates="patient")
    appointment_requests = relationship("AppointmentRequest", back_populates="patient")


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    specialty = Column(String, nullable=False)
    state = Column(String, nullable=False)
    location = Column(String, nullable=False)
    accepted_insurance = Column(String)
    available_days = Column(String)          # e.g. "Monday,Wednesday,Friday" (legacy, informational only)
    accepting_new_patients = Column(Boolean, default=True, nullable=False)
    languages = Column(String)
    bio = Column(Text)
    years_experience = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    appointment_requests = relationship("AppointmentRequest", back_populates="provider")
    slots = relationship("AppointmentSlot", back_populates="provider")


class AppointmentSlot(Base):
    __tablename__ = "appointment_slots"
    __table_args__ = (UniqueConstraint("provider_id", "start_time", name="uq_slot_provider_start"),)

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    provider = relationship("Provider", back_populates="slots")
    appointment_request = relationship("AppointmentRequest", back_populates="slot", uselist=False)


class ProviderMatchRequest(Base):
    __tablename__ = "provider_match_requests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    state = Column(String, nullable=False)
    insurance = Column(String)
    concern = Column(String, nullable=False)
    preferred_day = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("User", back_populates="match_requests")


class AppointmentRequest(Base):
    __tablename__ = "appointment_requests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    slot_id = Column(Integer, ForeignKey("appointment_slots.id"), nullable=True, unique=True)
    reason = Column(Text)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.pending, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("User", back_populates="appointment_requests")
    provider = relationship("Provider", back_populates="appointment_requests")
    slot = relationship("AppointmentSlot", back_populates="appointment_request")
