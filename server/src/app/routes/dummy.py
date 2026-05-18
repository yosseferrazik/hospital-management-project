from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.services.dummy_service import generate_dummy_data, cleanup_dummy

dummy_bp = Blueprint("dummy", __name__, url_prefix="/api/dummy")


@dummy_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    try:
        body = request.get_json(force=True) or {}
        count = body.get("count") or body.get("patient_count") or 14
        generate_dummy_data(patient_count=int(count))
        return jsonify({"message": "Dummy data generated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@dummy_bp.route("/cleanup", methods=["DELETE"])
@jwt_required()
def cleanup():
    try:
        cleanup_dummy()
        return jsonify({"message": "Dummy data removed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
