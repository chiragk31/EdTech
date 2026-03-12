import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.patient import Patient
from app.schemas.auth import PhoneRequest, OTPVerify, LoginResponse
from app.utils.jwt import create_access_token

router = APIRouter(
    prefix="/auth/patient",
    tags=["patient auth"]
)

# Temporary in-memory OTP storage
otp_store = {}

@router.post("/send-otp")
def send_otp(request: PhoneRequest):
    # Generate random 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP in dictionary
    otp_store[request.phone] = otp
    
    # Print OTP in server console (simulate SMS)
    print(f"--- SMS SIMULATION ---")
    print(f"To: {request.phone}")
    print(f"OTP: {otp}")
    print(f"----------------------")
    
    return {"message": "OTP sent successfully", "phone": request.phone}

@router.post("/verify-otp", response_model=LoginResponse)
def verify_otp(request: OTPVerify, db: Session = Depends(get_db)):
    # 1. Check if phone exists in OTP store
    if request.phone not in otp_store:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP not sent or expired")
    
    # 2. Check if OTP matches
    if otp_store[request.phone] != request.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    
    # 3. Query patients table using phone number
    patient = db.query(Patient).filter(Patient.phone == request.phone).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found. Please register first.")
    
    # 5. generate JWT access token
    access_token = create_access_token(
        data={"patient_id": patient.patient_id, "phone": patient.phone}
    )
    
    # Ensure OTP verification deletes OTP after successful login
    del otp_store[request.phone]
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "patient_id": patient.patient_id
    }
