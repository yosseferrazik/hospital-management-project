from flask import Blueprint, request, jsonify
from app.services.room_service import create_room, get_rooms, get_room, update_room, delete_room

room_bp = Blueprint("room", __name__, url_prefix="/api/rooms")


@room_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "room_number" not in data or "floor_id" not in data:
        return jsonify({"error": "room_number and floor_id required"}), 400
    room = create_room(data)
    return jsonify({"room_id": room.room_id}), 201


@room_bp.route("", methods=["GET"])
def list_rooms():
    rooms = get_rooms()
    return jsonify([{"room_id": r.room_id, "room_number": r.room_number, "floor_id": r.floor_id} for r in rooms])


@room_bp.route("/<int:room_id>", methods=["GET"])
def get(room_id):
    room = get_room(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404
    return jsonify({"room_id": room.room_id, "room_number": room.room_number, "floor_id": room.floor_id})


@room_bp.route("/<int:room_id>", methods=["PUT"])
def update(room_id):
    data = request.get_json()
    if not data or "room_number" not in data or "floor_id" not in data:
        return jsonify({"error": "room_number and floor_id required"}), 400
    room = update_room(room_id, data)
    if not room:
        return jsonify({"error": "Room not found"}), 404
    return jsonify({"message": "Room updated"})


@room_bp.route("/<int:room_id>", methods=["DELETE"])
def delete(room_id):
    room = delete_room(room_id)
    if not room:
        return jsonify({"error": "Room not found"}), 404
    return jsonify({"message": "Room deleted"})