from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.record import MedicalRecord
from app.schemas.sync import SyncRequest, SyncResponse
from app.utils.id_generator import generate_id

router = APIRouter(prefix="/sync", tags=["offline sync"])


@router.post("/patient-records", response_model=SyncResponse, status_code=status.HTTP_200_OK)
def sync_patient_records(payload: SyncRequest, db: Session = Depends(get_db)):
    """
    Offline-first sync endpoint.
    Accepts a batch of medical records from a mobile app and inserts them
    into the database. Skips duplicates based on patient_id + doctor_id +
    consultation_date to ensure idempotency.
    """
    synced = 0
    skipped = 0

    for record_data in payload.records:
        # ── Idempotency check: skip if exact record already exists ──────────
        existing = (
            db.query(MedicalRecord)
            .filter(
                MedicalRecord.patient_id == record_data.patient_id,
                MedicalRecord.doctor_id == record_data.doctor_id,
                MedicalRecord.consultation_date == record_data.consultation_date,
            )
            .first()
        )
        if existing:
            skipped += 1
            continue

        # ── Generate unique record_id ───────────────────────────────────────
        record_id = generate_id(db, MedicalRecord, "record_id", "REC")

        db_record = MedicalRecord(
            record_id=record_id,
            patient_id=record_data.patient_id,
            doctor_id=record_data.doctor_id,
            diagnosis=record_data.diagnosis,
            prescription=record_data.prescription,
            notes=record_data.notes,
            consultation_date=record_data.consultation_date,
        )
        db.add(db_record)
        synced += 1

    db.commit()

    return {
        "message": "Records synced successfully",
        "records_synced": synced,
        "records_skipped": skipped,
    }
