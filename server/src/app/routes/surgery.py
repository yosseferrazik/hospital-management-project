from flask import Blueprint, request, jsonify
from app.services.surgery_service import create_surgery, get_surgeries, get_surgery, update_surgery, delete_surgery, get_surgeries_by_date

surgery_bp = Blueprint("surgery", __name__, url_prefix="/api/surgeries")


@surgery_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "patient_id" not in data or "theater_id" not in data or "primary_surgeon_id" not in data or "surgery_date" not in data or "start_time" not in data or "end_time" not in data or "procedure_type" not in data:
        return jsonify({"error": "patient_id, theater_id, primary_surgeon_id, surgery_date, start_time, end_time, procedure_type required"}), 400
    surgery = create_surgery(data)
    return jsonify({"surgery_id": surgery.surgery_id}), 201


@surgery_bp.route("", methods=["GET"])
def list_surgeries():
    surgeries = get_surgeries()
    return jsonify([{
        "surgery_id": s.surgery_id,
        "patient_id": s.patient_id,
        "theater_id": s.theater_id,
        "primary_surgeon_id": s.primary_surgeon_id,
        "surgery_date": str(s.surgery_date),
        "start_time": str(s.start_time),
        "end_time": str(s.end_time),
        "procedure_type": s.procedure_type,
        "notes": s.notes
    } for s in surgeries])


@surgery_bp.route("/<int:surgery_id>", methods=["GET"])
def get(surgery_id):
    surgery = get_surgery(surgery_id)
    if not surgery:
        return jsonify({"error": "Surgery not found"}), 404
    return jsonify({
        "surgery_id": surgery.surgery_id,
        "patient_id": surgery.patient_id,
        "theater_id": surgery.theater_id,
        "primary_surgeon_id": surgery.primary_surgeon_id,
        "surgery_date": str(surgery.surgery_date),
        "start_time": str(surgery.start_time),
        "end_time": str(surgery.end_time),
        "procedure_type": surgery.procedure_type,
        "notes": surgery.notes
    })


@surgery_bp.route("/<int:surgery_id>", methods=["PUT"])
def update(surgery_id):
    data = request.get_json()
    if not data or "patient_id" not in data or "theater_id" not in data or "primary_surgeon_id" not in data or "surgery_date" not in data or "start_time" not in data or "end_time" not in data or "procedure_type" not in data:
        return jsonify({"error": "patient_id, theater_id, primary_surgeon_id, surgery_date, start_time, end_time, procedure_type required"}), 400
    surgery = update_surgery(surgery_id, data)
    if not surgery:
        return jsonify({"error": "Surgery not found"}), 404
    return jsonify({"message": "Surgery updated"})


@surgery_bp.route("/<int:surgery_id>", methods=["DELETE"])
def delete(surgery_id):
    surgery = delete_surgery(surgery_id)
    if not surgery:
        return jsonify({"error": "Surgery not found"}), 404
    return jsonify({"message": "Surgery deleted"})


@surgery_bp.route("/by_date/<date>", methods=["GET"])
def get_by_date(date):
    surgeries = get_surgeries_by_date(date)
    return jsonify(surgeries)