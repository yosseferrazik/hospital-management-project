"""Medication CRUD routes."""

from app.routes.base import make_crud_blueprint
from app.services.medication_service import create_medication, get_medications, get_medication, update_medication, delete_medication

medication_bp = make_crud_blueprint(
    "medication", "/api/medications",
    create_fn=create_medication, list_fn=get_medications, get_fn=get_medication,
    update_fn=update_medication, delete_fn=delete_medication,
    create_required=["medication_name"], update_required=["medication_name"],
    serialize=lambda m: {"medication_id": m.medication_id, "medication_name": m.medication_name, "description": m.description},
)
