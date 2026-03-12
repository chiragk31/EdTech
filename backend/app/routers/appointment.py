from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentStatusUpdate
from app.utils.id_generator import generate_id

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("/book", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(appt_in: AppointmentCreate, db: Session = Depends(get_db)):
    appointment_id = generate_id(db, Appointment, "appointment_id", "APT")
    db_appt = Appointment(**appt_in.dict(), appointment_id=appointment_id)
    db.add(db_appt)
    db.commit()
    db.refresh(db_appt)
    return db_appt


@router.get("/patient/{patient_id}", response_model=list[AppointmentResponse])
def get_patient_appointments(patient_id: str, db: Session = Depends(get_db)):
    return db.query(Appointment).filter(Appointment.patient_id == patient_id).all()


@router.get("/doctor/{doctor_id}", response_model=list[AppointmentResponse])
def get_doctor_appointments(doctor_id: str, db: Session = Depends(get_db)):
    return db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_status(
    appointment_id: str, update: AppointmentStatusUpdate, db: Session = Depends(get_db)
):
    valid_statuses = ["pending", "confirmed", "completed", "cancelled"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {valid_statuses}")

    appt = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.status = update.status
    db.commit()
    db.refresh(appt)
    return appt


@router.delete("/{appointment_id}", status_code=status.HTTP_200_OK)
def cancel_appointment(appointment_id: str, db: Session = Depends(get_db)):
    appt = db.query(Appointment).filter(Appointment.appointment_id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(appt)
    db.commit()
    return {"message": f"Appointment {appointment_id} deleted successfully"}
