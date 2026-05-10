from flask import Blueprint, request, jsonify
from app.services.radiology_exam_service import create_radiology_exam, get_radiology_exams, get_radiology_exam, update_radiology_exam, delete_radiology_exam

radiology_exam_bp = Blueprint("radiology_exam", __name__, url_prefix="/api/radiology_exams")


@radiology_exam_bp.route("", methods=["POST"])
def create():
    data = request.get_json()
    if not data or "patient_id" not in data or "requesting_doctor_id" not in data or "exam_type" not in data:
        return jsonify({"error": "patient_id, requesting_doctor_id, exam_type required"}), 400
    exam = create_radiology_exam(data)
    return jsonify({"exam_id": exam.exam_id}), 201


@radiology_exam_bp.route("", methods=["GET"])
def list_radiology_exams():
    exams = get_radiology_exams()
    return jsonify([{
        "exam_id": e.exam_id,
        "patient_id": e.patient_id,
        "requesting_doctor_id": e.requesting_doctor_id,
        "exam_type": e.exam_type,
        "requested_at": str(e.requested_at),
        "performed_at": str(e.performed_at) if e.performed_at else None,
        "result_image_url": e.result_image_url,
        "radiologist_report": e.radiologist_report,
        "status": e.status
    } for e in exams])


@radiology_exam_bp.route("/<int:exam_id>", methods=["GET"])
def get(exam_id):
    exam = get_radiology_exam(exam_id)
    if not exam:
        return jsonify({"error": "Radiology exam not found"}), 404
    return jsonify({
        "exam_id": exam.exam_id,
        "patient_id": exam.patient_id,
        "requesting_doctor_id": exam.requesting_doctor_id,
        "exam_type": exam.exam_type,
        "requested_at": str(exam.requested_at),
        "performed_at": str(exam.performed_at) if exam.performed_at else None,
        "result_image_url": exam.result_image_url,
        "radiologist_report": exam.radiologist_report,
        "status": exam.status
    })


@radiology_exam_bp.route("/<int:exam_id>", methods=["PUT"])
def update(exam_id):
    data = request.get_json()
    if not data or "patient_id" not in data or "requesting_doctor_id" not in data or "exam_type" not in data:
        return jsonify({"error": "patient_id, requesting_doctor_id, exam_type required"}), 400
    exam = update_radiology_exam(exam_id, data)
    if not exam:
        return jsonify({"error": "Radiology exam not found"}), 404
    return jsonify({"message": "Radiology exam updated"})


@radiology_exam_bp.route("/<int:exam_id>", methods=["DELETE"])
def delete(exam_id):
    exam = delete_radiology_exam(exam_id)
    if not exam:
        return jsonify({"error": "Radiology exam not found"}), 404
    return jsonify({"message": "Radiology exam deleted"})