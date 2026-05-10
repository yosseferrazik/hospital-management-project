from flask import Blueprint, request, jsonify
from app.services.medical_specialty_service import create_medical_specialty, get_medical_specialties, get_medical_specialty, update_medical_specialty, delete_medical_specialty

medical_specialty_bp = Blueprint("medical_specialty", __name__, url_prefix="/api/medical_specialties")


@medical_specialty_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name required"}), 400
    specialty = create_medical_specialty(data)
    return jsonify({"specialty_id": specialty.specialty_id}), 201


@medical_specialty_bp.route("", methods=["GET"])
def list_medical_specialties():
    specialties = get_medical_specialties()
    return jsonify([{"specialty_id": s.specialty_id, "name": s.name, "description": s.description} for s in specialties])


@medical_specialty_bp.route("/<int:specialty_id>", methods=["GET"])
def get(specialty_id):
    specialty = get_medical_specialty(specialty_id)
    if not specialty:
        return jsonify({"error": "Medical specialty not found"}), 404
    return jsonify({"specialty_id": specialty.specialty_id, "name": specialty.name, "description": specialty.description})


@medical_specialty_bp.route("/<int:specialty_id>", methods=["PUT"])
def update(specialty_id):
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name required"}), 400
    specialty = update_medical_specialty(specialty_id, data)
    if not specialty:
        return jsonify({"error": "Medical specialty not found"}), 404
    return jsonify({"message": "Medical specialty updated"})


@medical_specialty_bp.route("/<int:specialty_id>", methods=["DELETE"])
def delete(specialty_id):
    specialty = delete_medical_specialty(specialty_id)
    if not specialty:
        return jsonify({"error": "Medical specialty not found"}), 404
    return jsonify({"message": "Medical specialty deleted"})