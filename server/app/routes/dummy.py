from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.services.dummy_service import generate_dummy_data, cleanup_dummy

dummy_bp = Blueprint("dummy", __name__, url_prefix="/api/dummy")


@dummy_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    generate_dummy_data()
    return jsonify({"message": "Dummy data generated"}), 200


@dummy_bp.route("/cleanup", methods=["DELETE"])
@jwt_required()
def cleanup():
    cleanup_dummy()
    return jsonify({"message": "Dummy data removed"}), 200
