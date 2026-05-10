from flask import Blueprint, request, jsonify
from app.services.scheduled_appointment_service import create_scheduled_appointment, get_scheduled_appointments, get_scheduled_appointment, update_scheduled_appointment, delete_scheduled_appointment

scheduled_appointment_bp = Blueprint("scheduled_appointment", __name__, url_prefix="/api/scheduled_appointments")


@scheduled_appointment_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "visit_id" not in data or "appointment_date" not in data or "appointment_time" not in data:
        return jsonify({"error": "visit_id, appointment_date, appointment_time required"}), 400
    appointment = create_scheduled_appointment(data)
    return jsonify({"appointment_id": appointment.appointment_id}), 201


@scheduled_appointment_bp.route("", methods=["GET"])
def list_scheduled_appointments():
    appointments = get_scheduled_appointments()
    return jsonify([{
        "appointment_id": a.appointment_id,
        "visit_id": a.visit_id,
        "appointment_date": str(a.appointment_date),
        "appointment_time": str(a.appointment_time),
        "status": a.status
    } for a in appointments])


@scheduled_appointment_bp.route("/<int:appointment_id>", methods=["GET"])
def get(appointment_id):
    appointment = get_scheduled_appointment(appointment_id)
    if not appointment:
        return jsonify({"error": "Scheduled appointment not found"}), 404
    return jsonify({
        "appointment_id": appointment.appointment_id,
        "visit_id": appointment.visit_id,
        "appointment_date": str(appointment.appointment_date),
        "appointment_time": str(appointment.appointment_time),
        "status": appointment.status
    })


@scheduled_appointment_bp.route("/<int:appointment_id>", methods=["PUT"])
def update(appointment_id):
    data = request.get_json()
    if not data or "visit_id" not in data or "appointment_date" not in data or "appointment_time" not in data:
        return jsonify({"error": "visit_id, appointment_date, appointment_time required"}), 400
    appointment = update_scheduled_appointment(appointment_id, data)
    if not appointment:
        return jsonify({"error": "Scheduled appointment not found"}), 404
    return jsonify({"message": "Scheduled appointment updated"})


@scheduled_appointment_bp.route("/<int:appointment_id>", methods=["DELETE"])
def delete(appointment_id):
    appointment = delete_scheduled_appointment(appointment_id)
    if not appointment:
        return jsonify({"error": "Scheduled appointment not found"}), 404
    return jsonify({"message": "Scheduled appointment deleted"})