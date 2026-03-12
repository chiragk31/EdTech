from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorResponse, DoctorAvailabilityUpdate
from app.utils.id_generator import generate_id
from app.utils.security import get_password_hash
from app.dependencies.auth import get_current_admin, get_current_doctor

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("/register", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def register_doctor(
    doctor_in: DoctorCreate, 
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    existing = db.query(Doctor).filter(Doctor.phone == doctor_in.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Doctor with this phone already exists")
    
    existing_email = db.query(Doctor).filter(Doctor.email == doctor_in.email).first()
    if existing_email and doctor_in.email:
         raise HTTPException(status_code=400, detail="Doctor with this email already exists")

    doctor_id = generate_id(db, Doctor, "doctor_id", "DOC")
    
    doctor_data = doctor_in.dict()
    password = doctor_data.pop("password")
    pwd_hash = get_password_hash(password)
    
    db_doctor = Doctor(**doctor_data, password_hash=pwd_hash, doctor_id=doctor_id)
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

@router.get("/me", response_model=DoctorResponse)
def get_current_doctor_profile(current_doctor: Doctor = Depends(get_current_doctor)):
    """Return the profile of the currently logged-in doctor."""
    return current_doctor


@router.get("/", response_model=list[DoctorResponse])
def get_all_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).all()


@router.get("/specialization/{specialization}", response_model=list[DoctorResponse])
def get_doctors_by_specialization(specialization: str, db: Session = Depends(get_db)):
    doctors = db.query(Doctor).filter(Doctor.specialization.ilike(f"%{specialization}%")).all()
    if not doctors:
        raise HTTPException(status_code=404, detail="No doctors found for this specialization")
    return doctors


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: str, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.patch("/{doctor_id}/availability", response_model=DoctorResponse)
def update_availability(doctor_id: str, update: DoctorAvailabilityUpdate, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    doctor.availability_status = update.availability_status
    db.commit()
    db.refresh(doctor)
    return doctor
