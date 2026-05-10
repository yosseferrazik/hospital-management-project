from flask import Blueprint, request, jsonify
from app.services.operating_theater_service import create_operating_theater, get_operating_theaters, get_operating_theater, update_operating_theater, delete_operating_theater

operating_theater_bp = Blueprint("operating_theater", __name__, url_prefix="/api/operating_theaters")


@operating_theater_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "theater_code" not in data or "floor_id" not in data:
        return jsonify({"error": "theater_code and floor_id required"}), 400
    theater = create_operating_theater(data)
    return jsonify({"theater_id": theater.theater_id}), 201


@operating_theater_bp.route("", methods=["GET"])
def list_operating_theaters():
    theaters = get_operating_theaters()
    return jsonify([{"theater_id": t.theater_id, "theater_code": t.theater_code, "floor_id": t.floor_id} for t in theaters])


@operating_theater_bp.route("/<int:theater_id>", methods=["GET"])
def get(theater_id):
    theater = get_operating_theater(theater_id)
    if not theater:
        return jsonify({"error": "Operating theater not found"}), 404
    return jsonify({"theater_id": theater.theater_id, "theater_code": theater.theater_code, "floor_id": theater.floor_id})


@operating_theater_bp.route("/<int:theater_id>", methods=["PUT"])
def update(theater_id):
    data = request.get_json()
    if not data or "theater_code" not in data or "floor_id" not in data:
        return jsonify({"error": "theater_code and floor_id required"}), 400
    theater = update_operating_theater(theater_id, data)
    if not theater:
        return jsonify({"error": "Operating theater not found"}), 404
    return jsonify({"message": "Operating theater updated"})


@operating_theater_bp.route("/<int:theater_id>", methods=["DELETE"])
def delete(theater_id):
    theater = delete_operating_theater(theater_id)
    if not theater:
        return jsonify({"error": "Operating theater not found"}), 404
    return jsonify({"message": "Operating theater deleted"})