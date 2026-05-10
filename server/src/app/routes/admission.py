from flask import Blueprint, request, jsonify
from app.services.admission_service import create_admission, get_admissions, get_admission, update_admission, delete_admission

admission_bp = Blueprint("admission", __name__, url_prefix="/api/admissions")


@admission_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "patient_id" not in data or "room_id" not in data:
        return jsonify({"error": "patient_id and room_id required"}), 400
    admission = create_admission(data)
    return jsonify({"admission_id": admission.admission_id}), 201


@admission_bp.route("", methods=["GET"])
def list_admissions():
    admissions = get_admissions()
    return jsonify([{
        "admission_id": a.admission_id,
        "patient_id": a.patient_id,
        "room_id": a.room_id,
        "admission_date": str(a.admission_date),
        "expected_discharge_date": str(a.expected_discharge_date) if a.expected_discharge_date else None,
        "actual_discharge_date": str(a.actual_discharge_date) if a.actual_discharge_date else None
    } for a in admissions])


@admission_bp.route("/<int:admission_id>", methods=["GET"])
def get(admission_id):
    admission = get_admission(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404
    return jsonify({
        "admission_id": admission.admission_id,
        "patient_id": admission.patient_id,
        "room_id": admission.room_id,
        "admission_date": str(admission.admission_date),
        "expected_discharge_date": str(admission.expected_discharge_date) if admission.expected_discharge_date else None,
        "actual_discharge_date": str(admission.actual_discharge_date) if admission.actual_discharge_date else None
    })


@admission_bp.route("/<int:admission_id>", methods=["PUT"])
def update(admission_id):
    data = request.get_json()
    if not data or "patient_id" not in data or "room_id" not in data:
        return jsonify({"error": "patient_id and room_id required"}), 400
    admission = update_admission(admission_id, data)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404
    return jsonify({"message": "Admission updated"})


@admission_bp.route("/<int:admission_id>", methods=["DELETE"])
def delete(admission_id):
    admission = delete_admission(admission_id)
    if not admission:
        return jsonify({"error": "Admission not found"}), 404
    return jsonify({"message": "Admission deleted"})