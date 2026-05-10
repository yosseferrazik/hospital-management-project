from flask import Blueprint, request, jsonify
from app.services.pharmacy_dispensation_service import create_pharmacy_dispensation, get_pharmacy_dispensations, get_pharmacy_dispensation, update_pharmacy_dispensation, delete_pharmacy_dispensation

pharmacy_dispensation_bp = Blueprint("pharmacy_dispensation", __name__, url_prefix="/api/pharmacy_dispensations")


@pharmacy_dispensation_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "admission_id" not in data:
        return jsonify({"error": "admission_id required"}), 400
    dispensation = create_pharmacy_dispensation(data)
    return jsonify({"dispensation_id": dispensation.dispensation_id}), 201


@pharmacy_dispensation_bp.route("", methods=["GET"])
def list_pharmacy_dispensations():
    dispensations = get_pharmacy_dispensations()
    return jsonify([{
        "dispensation_id": d.dispensation_id,
        "admission_id": d.admission_id,
        "dispensed_at": str(d.dispensed_at),
        "total_cost": float(d.total_cost),
        "notes": d.notes
    } for d in dispensations])


@pharmacy_dispensation_bp.route("/<int:dispensation_id>", methods=["GET"])
def get(dispensation_id):
    dispensation = get_pharmacy_dispensation(dispensation_id)
    if not dispensation:
        return jsonify({"error": "Pharmacy dispensation not found"}), 404
    return jsonify({
        "dispensation_id": dispensation.dispensation_id,
        "admission_id": dispensation.admission_id,
        "dispensed_at": str(dispensation.dispensed_at),
        "total_cost": float(dispensation.total_cost),
        "notes": dispensation.notes
    })


@pharmacy_dispensation_bp.route("/<int:dispensation_id>", methods=["PUT"])
def update(dispensation_id):
    data = request.get_json()
    if not data or "admission_id" not in data:
        return jsonify({"error": "admission_id required"}), 400
    dispensation = update_pharmacy_dispensation(dispensation_id, data)
    if not dispensation:
        return jsonify({"error": "Pharmacy dispensation not found"}), 404
    return jsonify({"message": "Pharmacy dispensation updated"})


@pharmacy_dispensation_bp.route("/<int:dispensation_id>", methods=["DELETE"])
def delete(dispensation_id):
    dispensation = delete_pharmacy_dispensation(dispensation_id)
    if not dispensation:
        return jsonify({"error": "Pharmacy dispensation not found"}), 404
    return jsonify({"message": "Pharmacy dispensation deleted"})