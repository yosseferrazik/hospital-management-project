from flask import Blueprint, request, jsonify
from app.services.medical_device_service import create_medical_device, get_medical_devices, get_medical_device, update_medical_device, delete_medical_device

medical_device_bp = Blueprint("medical_device", __name__, url_prefix="/api/medical_devices")


@medical_device_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "device_type" not in data or "theater_id" not in data:
        return jsonify({"error": "device_type and theater_id required"}), 400
    device = create_medical_device(data)
    return jsonify({"device_id": device.device_id}), 201


@medical_device_bp.route("", methods=["GET"])
def list_medical_devices():
    devices = get_medical_devices()
    return jsonify([{"device_id": d.device_id, "device_type": d.device_type, "theater_id": d.theater_id, "quantity": d.quantity} for d in devices])


@medical_device_bp.route("/<int:device_id>", methods=["GET"])
def get(device_id):
    device = get_medical_device(device_id)
    if not device:
        return jsonify({"error": "Medical device not found"}), 404
    return jsonify({"device_id": device.device_id, "device_type": device.device_type, "theater_id": device.theater_id, "quantity": device.quantity})


@medical_device_bp.route("/<int:device_id>", methods=["PUT"])
def update(device_id):
    data = request.get_json()
    if not data or "device_type" not in data or "theater_id" not in data:
        return jsonify({"error": "device_type and theater_id required"}), 400
    device = update_medical_device(device_id, data)
    if not device:
        return jsonify({"error": "Medical device not found"}), 404
    return jsonify({"message": "Medical device updated"})


@medical_device_bp.route("/<int:device_id>", methods=["DELETE"])
def delete(device_id):
    device = delete_medical_device(device_id)
    if not device:
        return jsonify({"error": "Medical device not found"}), 404
    return jsonify({"message": "Medical device deleted"})