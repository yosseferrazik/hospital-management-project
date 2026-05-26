"""Admission CRUD routes."""

from app.routes.base import make_crud_blueprint
from app.services.admission_service import create_admission, get_admissions, get_admission, update_admission, delete_admission

admission_bp = make_crud_blueprint(
    "admission", "/api/admissions",
    create_fn=create_admission, list_fn=get_admissions, get_fn=get_admission,
    update_fn=update_admission, delete_fn=delete_admission,
    create_required=["patient_id", "room_id"], update_required=["patient_id", "room_id"],
    serialize=lambda a: {
        "admission_id": a.admission_id, "patient_id": a.patient_id, "room_id": a.room_id,
        "admission_date": str(a.admission_date) if a.admission_date else None,
        "expected_discharge_date": str(a.expected_discharge_date) if a.expected_discharge_date else None,
        "actual_discharge_date": str(a.actual_discharge_date) if a.actual_discharge_date else None,
    },
)
