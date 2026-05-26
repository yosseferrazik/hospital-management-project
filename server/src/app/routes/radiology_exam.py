"""Radiology exam CRUD routes."""

from app.routes.base import make_crud_blueprint
from app.services.radiology_exam_service import create_radiology_exam, get_radiology_exams, get_radiology_exam, update_radiology_exam, delete_radiology_exam

radiology_exam_bp = make_crud_blueprint(
    "radiology_exam", "/api/radiology_exams",
    create_fn=create_radiology_exam, list_fn=get_radiology_exams, get_fn=get_radiology_exam,
    update_fn=update_radiology_exam, delete_fn=delete_radiology_exam,
    create_required=["patient_id", "requesting_doctor_id", "exam_type"],
    update_required=["patient_id", "requesting_doctor_id", "exam_type"],
    serialize=lambda e: {
        "exam_id": e.exam_id, "patient_id": e.patient_id, "requesting_doctor_id": e.requesting_doctor_id,
        "exam_type": e.exam_type, "requested_at": str(e.requested_at) if e.requested_at else None,
        "performed_at": str(e.performed_at) if e.performed_at else None,
        "result_image_url": e.result_image_url, "radiologist_report": e.radiologist_report, "status": e.status,
    },
)
