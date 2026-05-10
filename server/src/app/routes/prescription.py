from flask import Blueprint, request, jsonify
from app.services.prescription_service import create_prescription, get_prescriptions, get_prescription, update_prescription, delete_prescription

prescription_bp = Blueprint("prescription", __name__, url_prefix="/api/prescriptions")


@prescription_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "visit_id" not in data or "medication_id" not in data or "dosage" not in data or "frequency" not in data:
        return jsonify({"error": "visit_id, medication_id, dosage, frequency required"}), 400
    prescription = create_prescription(data)
    return jsonify({"prescription_id": prescription.prescription_id}), 201


@prescription_bp.route("", methods=["GET"])
def list_prescriptions():
    prescriptions = get_prescriptions()
    return jsonify([{
        "prescription_id": p.prescription_id,
        "visit_id": p.visit_id,
        "medication_id": p.medication_id,
        "dosage": p.dosage,
        "frequency": p.frequency,
        "duration_days": p.duration_days,
        "start_date": str(p.start_date)
    } for p in prescriptions])


@prescription_bp.route("/<int:prescription_id>", methods=["GET"])
def get(prescription_id):
    prescription = get_prescription(prescription_id)
    if not prescription:
        return jsonify({"error": "Prescription not found"}), 404
    return jsonify({
        "prescription_id": prescription.prescription_id,
        "visit_id": prescription.visit_id,
        "medication_id": prescription.medication_id,
        "dosage": prescription.dosage,
        "frequency": prescription.frequency,
        "duration_days": prescription.duration_days,
        "start_date": str(prescription.start_date)
    })


@prescription_bp.route("/<int:prescription_id>", methods=["PUT"])
def update(prescription_id):
    data = request.get_json()
    if not data or "visit_id" not in data or "medication_id" not in data or "dosage" not in data or "frequency" not in data:
        return jsonify({"error": "visit_id, medication_id, dosage, frequency required"}), 400
    prescription = update_prescription(prescription_id, data)
    if not prescription:
        return jsonify({"error": "Prescription not found"}), 404
    return jsonify({"message": "Prescription updated"})


@prescription_bp.route("/<int:prescription_id>", methods=["DELETE"])
def delete(prescription_id):
    prescription = delete_prescription(prescription_id)
    if not prescription:
        return jsonify({"error": "Prescription not found"}), 404
    return jsonify({"message": "Prescription deleted"})