from app.models import db, RadiologyExam
from datetime import datetime


def create_radiology_exam(data):
    exam = RadiologyExam(
        patient_id=data["patient_id"],
        requesting_doctor_id=data["requesting_doctor_id"],
        exam_type=data["exam_type"],
        requested_at=datetime.strptime(data["requested_at"], "%Y-%m-%d %H:%M:%S") if "requested_at" in data else None,
        performed_at=datetime.strptime(data["performed_at"], "%Y-%m-%d %H:%M:%S") if "performed_at" in data else None,
        result_image_url=data.get("result_image_url"),
        radiologist_report=data.get("radiologist_report"),
        status=data.get("status", "REQUESTED"),
    )
    db.session.add(exam)
    db.session.commit()
    return exam


def get_radiology_exams():
    return RadiologyExam.query.all()


def get_radiology_exam(exam_id):
    return RadiologyExam.query.get(exam_id)


def update_radiology_exam(exam_id, data):
    exam = RadiologyExam.query.get(exam_id)
    if exam:
        exam.patient_id = data["patient_id"]
        exam.requesting_doctor_id = data["requesting_doctor_id"]
        exam.exam_type = data["exam_type"]
        exam.requested_at = datetime.strptime(data["requested_at"], "%Y-%m-%d %H:%M:%S") if "requested_at" in data else None
        exam.performed_at = datetime.strptime(data["performed_at"], "%Y-%m-%d %H:%M:%S") if "performed_at" in data else None
        exam.result_image_url = data.get("result_image_url")
        exam.radiologist_report = data.get("radiologist_report")
        exam.status = data.get("status", "REQUESTED")
        db.session.commit()
    return exam


def delete_radiology_exam(exam_id):
    exam = RadiologyExam.query.get(exam_id)
    if exam:
        db.session.delete(exam)
        db.session.commit()
    return exam