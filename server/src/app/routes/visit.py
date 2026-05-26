"""Visit CRUD routes with date-based scheduled lookup."""

from flask import jsonify
from app.routes.base import make_crud_blueprint
from app.services.visit_service import create_visit, get_visits, get_visit, update_visit, delete_visit, get_scheduled_visits_by_date

visit_bp = make_crud_blueprint(
    "visit", "/api/visits",
    create_fn=create_visit, list_fn=get_visits, get_fn=get_visit,
    update_fn=update_visit, delete_fn=delete_visit,
    create_required=["patient_id", "doctor_id"],
    update_required=["patient_id", "doctor_id"],
    serialize=lambda v: {
        "visit_id": v.visit_id, "patient_id": v.patient_id, "doctor_id": v.doctor_id,
        "visit_timestamp": str(v.visit_timestamp) if v.visit_timestamp else None,
        "diagnosis": v.diagnosis, "notes": v.notes,
    },
)


# --- GET /api/visits/scheduled/<date> — lookup scheduled visits by date ---
@visit_bp.route("/scheduled/<date>", methods=["GET"])
def get_scheduled(date):
    visits = get_scheduled_visits_by_date(date)
    return jsonify(visits)
