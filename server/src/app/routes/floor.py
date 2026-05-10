from flask import Blueprint, request, jsonify
from app.services.floor_service import create_floor, get_floors, get_floor, update_floor, delete_floor

floor_bp = Blueprint("floor", __name__, url_prefix="/api/floors")


@floor_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "floor_number" not in data:
        return jsonify({"error": "floor_number required"}), 400
    floor = create_floor(data)
    return jsonify({"floor_id": floor.floor_id}), 201


@floor_bp.route("", methods=["GET"])
def list_floors():
    floors = get_floors()
    return jsonify([{"floor_id": f.floor_id, "floor_number": f.floor_number} for f in floors])


@floor_bp.route("/<int:floor_id>", methods=["GET"])
def get(floor_id):
    floor = get_floor(floor_id)
    if not floor:
        return jsonify({"error": "Floor not found"}), 404
    return jsonify({"floor_id": floor.floor_id, "floor_number": floor.floor_number})


@floor_bp.route("/<int:floor_id>", methods=["PUT"])
def update(floor_id):
    data = request.get_json()
    if not data or "floor_number" not in data:
        return jsonify({"error": "floor_number required"}), 400
    floor = update_floor(floor_id, data)
    if not floor:
        return jsonify({"error": "Floor not found"}), 404
    return jsonify({"message": "Floor updated"})


@floor_bp.route("/<int:floor_id>", methods=["DELETE"])
def delete(floor_id):
    floor = delete_floor(floor_id)
    if not floor:
        return jsonify({"error": "Floor not found"}), 404
    return jsonify({"message": "Floor deleted"})