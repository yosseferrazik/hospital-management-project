from flask import Blueprint, request, jsonify
from app.services.medication_service import create_medication, get_medications, get_medication, update_medication, delete_medication

medication_bp = Blueprint("medication", __name__, url_prefix="/api/medications")


@medication_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "medication_name" not in data:
        return jsonify({"error": "medication_name required"}), 400
    medication = create_medication(data)
    return jsonify({"medication_id": medication.medication_id}), 201


@medication_bp.route("", methods=["GET"])
def list_medications():
    medications = get_medications()
    return jsonify([{"medication_id": m.medication_id, "medication_name": m.medication_name, "description": m.description} for m in medications])


@medication_bp.route("/<int:medication_id>", methods=["GET"])
def get(medication_id):
    medication = get_medication(medication_id)
    if not medication:
        return jsonify({"error": "Medication not found"}), 404
    return jsonify({"medication_id": medication.medication_id, "medication_name": medication.medication_name, "description": medication.description})


@medication_bp.route("/<int:medication_id>", methods=["PUT"])
def update(medication_id):
    data = request.get_json()
    if not data or "medication_name" not in data:
        return jsonify({"error": "medication_name required"}), 400
    medication = update_medication(medication_id, data)
    if not medication:
        return jsonify({"error": "Medication not found"}), 404
    return jsonify({"message": "Medication updated"})


@medication_bp.route("/<int:medication_id>", methods=["DELETE"])
def delete(medication_id):
    medication = delete_medication(medication_id)
    if not medication:
        return jsonify({"error": "Medication not found"}), 404
    return jsonify({"message": "Medication deleted"})