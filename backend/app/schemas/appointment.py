from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime


class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    symptoms: Optional[str] = None
    consultation_type: str  # audio | video | chat
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None


class AppointmentStatusUpdate(BaseModel):
    status: str  # pending | confirmed | completed | cancelled


class AppointmentResponse(AppointmentCreate):
    appointment_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
