from flask import Blueprint, request, jsonify
from app.services.staff_service import get_staff, get_staff_member, update_staff, delete_staff, create_medical_staff, create_nursing_staff, create_general_staff, assign_nursing_to_doctor, assign_nursing_to_floor

staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")


@staff_bp.route("", methods=["GET"])
def list_staff():
    staff = get_staff()
    return jsonify([{
        "staff_id": s.staff_id,
        "national_id": s.national_id,
        "first_name": s.first_name,
        "last_name": s.last_name,
        "birth_date": str(s.birth_date),
        "phone": s.phone,
        "ssn": s.ssn,
        "email": s.email,
        "address": s.address,
        "hire_date": str(s.hire_date),
        "staff_type": s.staff_type
    } for s in staff])


@staff_bp.route("/<int:staff_id>", methods=["GET"])
def get(staff_id):
    staff = get_staff_member(staff_id)
    if not staff:
        return jsonify({"error": "Staff member not found"}), 404
    return jsonify({
        "staff_id": staff.staff_id,
        "national_id": staff.national_id,
        "first_name": staff.first_name,
        "last_name": staff.last_name,
        "birth_date": str(staff.birth_date),
        "phone": staff.phone,
        "ssn": staff.ssn,
        "email": staff.email,
        "address": staff.address,
        "hire_date": str(staff.hire_date),
        "staff_type": staff.staff_type
    })


@staff_bp.route("/<int:staff_id>", methods=["PUT"])
def update(staff_id):
    data = request.get_json()
    if not data or "national_id" not in data or "first_name" not in data or "last_name" not in data or "birth_date" not in data or "staff_type" not in data:
        return jsonify({"error": "national_id, first_name, last_name, birth_date, staff_type required"}), 400
    staff = update_staff(staff_id, data)
    if not staff:
        return jsonify({"error": "Staff member not found"}), 404
    return jsonify({"message": "Staff updated"})


@staff_bp.route("/<int:staff_id>", methods=["DELETE"])
def delete(staff_id):
    staff = delete_staff(staff_id)
    if not staff:
        return jsonify({"error": "Staff member not found"}), 404
    return jsonify({"message": "Staff deleted"})


@staff_bp.route("/medical", methods=["POST"])
def create_medical():
    data = request.get_json()
    if not data or "national_id" not in data or "first_name" not in data or "last_name" not in data or "birth_date" not in data or "specialty_id" not in data or "license_number" not in data:
        return jsonify({"error": "national_id, first_name, last_name, birth_date, specialty_id, license_number required"}), 400
    staff = create_medical_staff(data)
    return jsonify({"staff_id": staff.staff_id}), 201


@staff_bp.route("/nursing", methods=["POST"])
def create_nursing():
    data = request.get_json()
    if not data or "national_id" not in data or "first_name" not in data or "last_name" not in data or "birth_date" not in data or "nursing_license" not in data:
        return jsonify({"error": "national_id, first_name, last_name, birth_date, nursing_license required"}), 400
    staff = create_nursing_staff(data)
    return jsonify({"staff_id": staff.staff_id}), 201


@staff_bp.route("/general", methods=["POST"])
def create_general():
    data = request.get_json()
    if not data or "national_id" not in data or "first_name" not in data or "last_name" not in data or "birth_date" not in data or "job_type" not in data:
        return jsonify({"error": "national_id, first_name, last_name, birth_date, job_type required"}), 400
    staff = create_general_staff(data)
    return jsonify({"staff_id": staff.staff_id}), 201


@staff_bp.route("/nursing/<int:nurse_id>/assign_doctor/<int:doctor_id>", methods=["PUT"])
def assign_doctor(nurse_id, doctor_id):
    try:
        nurse = assign_nursing_to_doctor(nurse_id, doctor_id)
        return jsonify({"message": "Nurse assigned to doctor"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@staff_bp.route("/nursing/<int:nurse_id>/assign_floor/<int:floor_id>", methods=["PUT"])
def assign_floor(nurse_id, floor_id):
    try:
        nurse = assign_nursing_to_floor(nurse_id, floor_id)
        return jsonify({"message": "Nurse assigned to floor"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400