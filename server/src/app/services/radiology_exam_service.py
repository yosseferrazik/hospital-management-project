"""Radiology exam service — CRUD delegation for RadiologyExam model."""

from app.models import RadiologyExam
from app.services.base import parse_date, create_record, get_all, get_by_id, update_record, delete_record


def create_radiology_exam(data):
    return create_record(RadiologyExam,
        patient_id=data["patient_id"],
        requesting_doctor_id=data["requesting_doctor_id"],
        exam_type=data["exam_type"],
        requested_at=parse_date(data.get("requested_at"), "%Y-%m-%d %H:%M:%S"),
        performed_at=parse_date(data.get("performed_at"), "%Y-%m-%d %H:%M:%S"),
        result_image_url=data.get("result_image_url"),
        radiologist_report=data.get("radiologist_report"),
        status=data.get("status", "REQUESTED"),
    )


def get_radiology_exams():
    return get_all(RadiologyExam)


def get_radiology_exam(exam_id):
    return get_by_id(RadiologyExam, exam_id)


def update_radiology_exam(exam_id, data):
    exam = get_by_id(RadiologyExam, exam_id)
    return update_record(exam,
        patient_id=data["patient_id"],
        requesting_doctor_id=data["requesting_doctor_id"],
        exam_type=data["exam_type"],
        requested_at=parse_date(data.get("requested_at"), "%Y-%m-%d %H:%M:%S"),
        performed_at=parse_date(data.get("performed_at"), "%Y-%m-%d %H:%M:%S"),
        result_image_url=data.get("result_image_url"),
        radiologist_report=data.get("radiologist_report"),
        status=data.get("status", "REQUESTED"),
    )


def delete_radiology_exam(exam_id):
    exam = get_by_id(RadiologyExam, exam_id)
    return delete_record(exam)
