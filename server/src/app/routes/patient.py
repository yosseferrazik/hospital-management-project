from flask import Blueprint, request, jsonify
from app.services.patient_service import create_patient, get_patients, get_patient, update_patient, delete_patient

patient_bp = Blueprint("patient", __name__, url_prefix="/api/patients")


@patient_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "national_id" not in data or "first_name" not in data or "last_name" not in data or "birth_date" not in data:
        return jsonify({"error": "national_id, first_name, last_name, birth_date required"}), 400
    patient = create_patient(data)
    return jsonify({"patient_id": patient.patient_id}), 201


@patient_bp.route("", methods=["GET"])
def list_patients():
    patients = get_patients()
    return jsonify([{
        "patient_id": p.patient_id,
        "national_id": p.national_id,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "birth_date": str(p.birth_date),
        "gender": p.gender,
        "phone": p.phone,
        "email": p.email,
        "address": p.address,
        "emergency_contact_name": p.emergency_contact_name,
        "emergency_contact_phone": p.emergency_contact_phone,
        "blood_type": p.blood_type,
        "allergies": p.allergies
    } for p in patients])


@patient_bp.route("/<int:patient_id>", methods=["GET"])
def get(patient_id):
    patient = get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify({
        "patient_id": patient.patient_id,
        "national_id": patient.national_id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "birth_date": str(patient.birth_date),
        "gender": patient.gender,
        "phone": patient.phone,
        "email": patient.email,
        "address": patient.address,
        "emergency_contact_name": patient.emergency_contact_name,
        "emergency_contact_phone": patient.emergency_contact_phone,
        "blood_type": patient.blood_type,
        "allergies": patient.allergies
    })


@patient_bp.route("/<int:patient_id>", methods=["PUT"])
def update(patient_id):
    data = request.get_json()
    if not data or "national_id" not in data or "first_name" not in data or "last_name" not in data or "birth_date" not in data:
        return jsonify({"error": "national_id, first_name, last_name, birth_date required"}), 400
    patient = update_patient(patient_id, data)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify({"message": "Patient updated"})


@patient_bp.route("/<int:patient_id>", methods=["DELETE"])
def delete(patient_id):
    patient = delete_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify({"message": "Patient deleted"})