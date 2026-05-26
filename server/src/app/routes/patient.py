"""Patient CRUD routes."""

from app.routes.base import make_crud_blueprint
from app.services.patient_service import create_patient, get_patients, get_patient, update_patient, delete_patient

patient_bp = make_crud_blueprint(
    "patient", "/api/patients",
    create_fn=create_patient, list_fn=get_patients, get_fn=get_patient,
    update_fn=update_patient, delete_fn=delete_patient,
    create_required=["national_id", "first_name", "last_name", "birth_date"],
    update_required=["national_id", "first_name", "last_name", "birth_date"],
    serialize=lambda p: {
        "patient_id": p.patient_id, "national_id": p.national_id,
        "first_name": p.first_name, "last_name": p.last_name,
        "birth_date": str(p.birth_date), "gender": p.gender,
        "phone": p.phone, "email": p.email, "address": p.address,
        "emergency_contact_name": p.emergency_contact_name,
        "emergency_contact_phone": p.emergency_contact_phone,
        "blood_type": p.blood_type, "allergies": p.allergies,
        "health_card": p.health_card,
    },
)
