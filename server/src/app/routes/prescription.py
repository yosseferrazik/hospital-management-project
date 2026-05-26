"""Prescription CRUD routes."""

from app.routes.base import make_crud_blueprint
from app.services.prescription_service import create_prescription, get_prescriptions, get_prescription, update_prescription, delete_prescription

prescription_bp = make_crud_blueprint(
    "prescription", "/api/prescriptions",
    create_fn=create_prescription, list_fn=get_prescriptions, get_fn=get_prescription,
    update_fn=update_prescription, delete_fn=delete_prescription,
    create_required=["visit_id", "medication_id", "dosage", "frequency"],
    update_required=["visit_id", "medication_id", "dosage", "frequency"],
    serialize=lambda p: {
        "prescription_id": p.prescription_id, "visit_id": p.visit_id, "medication_id": p.medication_id,
        "dosage": p.dosage, "frequency": p.frequency, "duration_days": p.duration_days,
        "start_date": str(p.start_date) if p.start_date else None,
    },
)
