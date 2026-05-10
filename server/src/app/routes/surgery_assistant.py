from flask import Blueprint, request, jsonify
from app.services.surgery_assistant_service import create_surgery_assistant, get_surgery_assistants, get_surgery_assistant, update_surgery_assistant, delete_surgery_assistant

surgery_assistant_bp = Blueprint("surgery_assistant", __name__, url_prefix="/api/surgery_assistants")


@surgery_assistant_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "surgery_id" not in data or "nurse_id" not in data or "role" not in data:
        return jsonify({"error": "surgery_id, nurse_id, role required"}), 400
    assistant = create_surgery_assistant(data)
    return jsonify({"surgery_id": assistant.surgery_id, "nurse_id": assistant.nurse_id}), 201


@surgery_assistant_bp.route("", methods=["GET"])
def list_surgery_assistants():
    assistants = get_surgery_assistants()
    return jsonify([{"surgery_id": a.surgery_id, "nurse_id": a.nurse_id, "role": a.role} for a in assistants])


@surgery_assistant_bp.route("/<int:surgery_id>/<int:nurse_id>", methods=["GET"])
def get(surgery_id, nurse_id):
    assistant = get_surgery_assistant(surgery_id, nurse_id)
    if not assistant:
        return jsonify({"error": "Surgery assistant not found"}), 404
    return jsonify({"surgery_id": assistant.surgery_id, "nurse_id": assistant.nurse_id, "role": assistant.role})


@surgery_assistant_bp.route("/<int:surgery_id>/<int:nurse_id>", methods=["PUT"])
def update(surgery_id, nurse_id):
    data = request.get_json()
    if not data or "role" not in data:
        return jsonify({"error": "role required"}), 400
    assistant = update_surgery_assistant(surgery_id, nurse_id, data)
    if not assistant:
        return jsonify({"error": "Surgery assistant not found"}), 404
    return jsonify({"message": "Surgery assistant updated"})


@surgery_assistant_bp.route("/<int:surgery_id>/<int:nurse_id>", methods=["DELETE"])
def delete(surgery_id, nurse_id):
    assistant = delete_surgery_assistant(surgery_id, nurse_id)
    if not assistant:
        return jsonify({"error": "Surgery assistant not found"}), 404
    return jsonify({"message": "Surgery assistant deleted"})