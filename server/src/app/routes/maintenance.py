"""Maintenance routes — staff/patient creation, nurse assignment, lookups."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services import staff_service, patient_service, surgery_service, visit_service

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/api/maintenance")


# --- POST /api/maintenance/staff/medical — create a doctor ---
@maintenance_bp.route("/staff/medical", methods=["POST"])
@jwt_required()
def add_medical_staff():
    data = request.get_json()
    try:
        staff = staff_service.create_medical_staff(data)
        return jsonify({"staff_id": staff.staff_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --- POST /api/maintenance/staff/nursing — create a nurse ---
@maintenance_bp.route("/staff/nursing", methods=["POST"])
@jwt_required()
def add_nursing_staff():
    data = request.get_json()
    try:
        staff = staff_service.create_nursing_staff(data)
        return jsonify({"staff_id": staff.staff_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --- POST /api/maintenance/staff/general — create general staff ---
@maintenance_bp.route("/staff/general", methods=["POST"])
@jwt_required()
def add_general_staff():
    data = request.get_json()
    try:
        staff = staff_service.create_general_staff(data)
        return jsonify({"staff_id": staff.staff_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --- POST /api/maintenance/patients — create a patient record ---
@maintenance_bp.route("/patients", methods=["POST"])
@jwt_required()
def add_patient():
    data = request.get_json()
    try:
        patient = patient_service.create_patient(data)
        return jsonify({"patient_id": patient.patient_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --- PUT /api/maintenance/nursing/assign — assign nurse to doctor or floor ---
@maintenance_bp.route("/nursing/assign", methods=["PUT"])
@jwt_required()
def assign_nursing():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    nurse_id = data.get("nurse_id")
    if not nurse_id:
        return jsonify({"error": "nurse_id is required"}), 400
    try:
        if "doctor_id" in data:
            nurse = staff_service.assign_nursing_to_doctor(nurse_id, data["doctor_id"])
        elif "floor_id" in data:
            nurse = staff_service.assign_nursing_to_floor(nurse_id, data["floor_id"])
        else:
            return jsonify({"error": "doctor_id or floor_id required"}), 400
        return jsonify({"message": "Assigned"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --- GET /api/maintenance/surgeries — get surgeries by date ---
@maintenance_bp.route("/surgeries", methods=["GET"])
@jwt_required()
def get_surgeries():
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "date parameter required (YYYY-MM-DD)"}), 400
    surgeries = surgery_service.get_surgeries_by_date(date)
    return jsonify(surgeries), 200


# --- GET /api/maintenance/visits/scheduled — get scheduled visits by date ---
@maintenance_bp.route("/visits/scheduled", methods=["GET"])
@jwt_required()
def get_visits():
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "date parameter required"}), 400
    visits = visit_service.get_scheduled_visits_by_date(date)
    return jsonify(visits), 200
