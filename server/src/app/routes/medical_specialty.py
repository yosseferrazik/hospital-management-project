from app.routes.base import make_crud_blueprint
from app.services.medical_specialty_service import create_medical_specialty, get_medical_specialties, get_medical_specialty, update_medical_specialty, delete_medical_specialty

medical_specialty_bp = make_crud_blueprint(
    "medical_specialty", "/api/medical_specialties",
    create_fn=create_medical_specialty, list_fn=get_medical_specialties, get_fn=get_medical_specialty,
    update_fn=update_medical_specialty, delete_fn=delete_medical_specialty,
    create_required=["name"], update_required=["name"],
    serialize=lambda s: {"specialty_id": s.specialty_id, "name": s.name, "description": s.description},
)
