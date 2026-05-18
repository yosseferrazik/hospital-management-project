from flask import jsonify
from app.routes.base import make_crud_blueprint
from app.services.surgery_service import create_surgery, get_surgeries, get_surgery, update_surgery, delete_surgery, get_surgeries_by_date

surgery_bp = make_crud_blueprint(
    "surgery", "/api/surgeries",
    create_fn=create_surgery, list_fn=get_surgeries, get_fn=get_surgery,
    update_fn=update_surgery, delete_fn=delete_surgery,
    create_required=["patient_id", "theater_id", "primary_surgeon_id", "surgery_date", "start_time", "end_time", "procedure_type"],
    update_required=["patient_id", "theater_id", "primary_surgeon_id", "surgery_date", "start_time", "end_time", "procedure_type"],
    serialize=lambda s: {
        "surgery_id": s.surgery_id, "patient_id": s.patient_id, "theater_id": s.theater_id,
        "primary_surgeon_id": s.primary_surgeon_id, "surgery_date": str(s.surgery_date),
        "start_time": str(s.start_time), "end_time": str(s.end_time),
        "procedure_type": s.procedure_type, "notes": s.notes,
    },
)


@surgery_bp.route("/by_date/<date>", methods=["GET"])
def get_by_date(date):
    surgeries = get_surgeries_by_date(date)
    return jsonify(surgeries)
