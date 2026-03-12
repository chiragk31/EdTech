from fastapi import FastAPI
from app.core.database import engine, Base
from app import models
from app.routers import patient, patient_auth, doctor, appointment, record, pharmacy, ai, sync, asha, vitals, voice_reports, admin_auth, doctor_auth, ai_risk

app = FastAPI(
    title="Rural TeleHealth Access System",
    description="Backend API enabling rural patients to consult doctors remotely, maintain digital health records, check medicine availability, and access AI-based symptom guidance.",
    version="1.0.0"
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(patient.router)
app.include_router(patient_auth.router)
app.include_router(admin_auth.router)
app.include_router(doctor_auth.router)
app.include_router(doctor.router)
app.include_router(appointment.router)
app.include_router(record.router)
app.include_router(pharmacy.router)
app.include_router(ai.router)
app.include_router(sync.router)
app.include_router(asha.router)
app.include_router(vitals.router)
app.include_router(voice_reports.router)
app.include_router(ai_risk.router)

# ─── Create Tables ────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)


@app.get("/", tags=["health"])
def root():
    return {"message": "Rural TeleHealth Backend is running 🏥", "status": "ok"}