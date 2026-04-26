from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import staff_service, patient_service, surgery_service, visit_service

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/api/maintenance")


@maintenance_bp.route("/staff/medical", methods=["POST"])
@jwt_required()
def add_medical_staff():
    data = request.json
    try:
        staff = staff_service.create_medical_staff(data)
        return jsonify({"staff_id": staff.staff_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@maintenance_bp.route("/staff/nursing", methods=["POST"])
@jwt_required()
def add_nursing_staff():
    data = request.json
    staff = staff_service.create_nursing_staff(data)
    return jsonify({"staff_id": staff.staff_id}), 201


@maintenance_bp.route("/staff/general", methods=["POST"])
@jwt_required()
def add_general_staff():
    data = request.json
    staff = staff_service.create_general_staff(data)
    return jsonify({"staff_id": staff.staff_id}), 201


@maintenance_bp.route("/patients", methods=["POST"])
@jwt_required()
def add_patient():
    data = request.json
    patient = patient_service.create_patient(data)
    return jsonify({"patient_id": patient.patient_id}), 201


@maintenance_bp.route("/nursing/assign", methods=["PUT"])
@jwt_required()
def assign_nursing():
    data = request.json
    nurse_id = data["nurse_id"]
    if "doctor_id" in data:
        nurse = staff_service.assign_nursing_to_doctor(nurse_id, data["doctor_id"])
    elif "floor_id" in data:
        nurse = staff_service.assign_nursing_to_floor(nurse_id, data["floor_id"])
    else:
        return jsonify({"error": "doctor_id or floor_id required"}), 400
    return jsonify({"message": "Assigned"}), 200


@maintenance_bp.route("/surgeries", methods=["GET"])
@jwt_required()
def get_surgeries():
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "date parameter required (YYYY-MM-DD)"}), 400
    surgeries = surgery_service.get_surgeries_by_date(date)
    return jsonify(surgeries), 200


@maintenance_bp.route("/visits/scheduled", methods=["GET"])
@jwt_required()
def get_visits():
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "date parameter required"}), 400
    visits = visit_service.get_scheduled_visits_by_date(date)
    return jsonify(visits), 200
