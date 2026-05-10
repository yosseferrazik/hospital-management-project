from flask import Blueprint, request, jsonify
from app.services.visit_service import create_visit, get_visits, get_visit, update_visit, delete_visit, get_scheduled_visits_by_date

visit_bp = Blueprint("visit", __name__, url_prefix="/api/visits")


@visit_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "patient_id" not in data or "doctor_id" not in data:
        return jsonify({"error": "patient_id and doctor_id required"}), 400
    visit = create_visit(data)
    return jsonify({"visit_id": visit.visit_id}), 201


@visit_bp.route("", methods=["GET"])
def list_visits():
    visits = get_visits()
    return jsonify([{
        "visit_id": v.visit_id,
        "patient_id": v.patient_id,
        "doctor_id": v.doctor_id,
        "visit_timestamp": str(v.visit_timestamp),
        "diagnosis": v.diagnosis,
        "notes": v.notes
    } for v in visits])


@visit_bp.route("/<int:visit_id>", methods=["GET"])
def get(visit_id):
    visit = get_visit(visit_id)
    if not visit:
        return jsonify({"error": "Visit not found"}), 404
    return jsonify({
        "visit_id": visit.visit_id,
        "patient_id": visit.patient_id,
        "doctor_id": visit.doctor_id,
        "visit_timestamp": str(visit.visit_timestamp),
        "diagnosis": visit.diagnosis,
        "notes": visit.notes
    })


@visit_bp.route("/<int:visit_id>", methods=["PUT"])
def update(visit_id):
    data = request.get_json()
    if not data or "patient_id" not in data or "doctor_id" not in data:
        return jsonify({"error": "patient_id and doctor_id required"}), 400
    visit = update_visit(visit_id, data)
    if not visit:
        return jsonify({"error": "Visit not found"}), 404
    return jsonify({"message": "Visit updated"})


@visit_bp.route("/<int:visit_id>", methods=["DELETE"])
def delete(visit_id):
    visit = delete_visit(visit_id)
    if not visit:
        return jsonify({"error": "Visit not found"}), 404
    return jsonify({"message": "Visit deleted"})


@visit_bp.route("/scheduled/<date>", methods=["GET"])
def get_scheduled(date):
    visits = get_scheduled_visits_by_date(date)
    return jsonify(visits)