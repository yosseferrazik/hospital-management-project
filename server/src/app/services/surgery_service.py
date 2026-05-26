"""Surgery service — CRUD delegation with date-based lookup."""

from app.models import db, Surgery, SurgeryAssistant
from app.services.base import parse_date, parse_time, create_record, get_all, get_by_id, update_record, delete_record


def create_surgery(data):
    return create_record(Surgery,
        patient_id=data["patient_id"],
        theater_id=data["theater_id"],
        primary_surgeon_id=data["primary_surgeon_id"],
        surgery_date=parse_date(data["surgery_date"], "%Y-%m-%d"),
        start_time=parse_time(data["start_time"]),
        end_time=parse_time(data["end_time"]),
        procedure_type=data["procedure_type"],
        notes=data.get("notes"),
    )


def get_surgeries():
    return get_all(Surgery)


def get_surgery(surgery_id):
    return get_by_id(Surgery, surgery_id)


def update_surgery(surgery_id, data):
    surgery = get_by_id(Surgery, surgery_id)
    return update_record(surgery,
        patient_id=data["patient_id"],
        theater_id=data["theater_id"],
        primary_surgeon_id=data["primary_surgeon_id"],
        surgery_date=parse_date(data["surgery_date"], "%Y-%m-%d"),
        start_time=parse_time(data["start_time"]),
        end_time=parse_time(data["end_time"]),
        procedure_type=data["procedure_type"],
        notes=data.get("notes"),
    )


def delete_surgery(surgery_id):
    surgery = get_by_id(Surgery, surgery_id)
    return delete_record(surgery)


def get_surgeries_by_date(date):
    """Return surgeries scheduled on a given date, including patient/surgeon/assistant info."""
    surgeries = db.session.query(Surgery).filter(Surgery.surgery_date == date).all()
    result = []
    for s in surgeries:
        patient = s.patient
        surgeon = s.primary_surgeon.staff if s.primary_surgeon else None
        assistants = SurgeryAssistant.query.filter_by(surgery_id=s.surgery_id).all()
        result.append({
            "surgery_id": s.surgery_id,
            "theater_id": s.theater_id,
            "patient": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
            "surgeon": f"{surgeon.first_name} {surgeon.last_name}" if surgeon else "Unknown",
            "start_time": str(s.start_time),
            "end_time": str(s.end_time),
            "procedure_type": s.procedure_type,
            "assistants": [{"nurse_id": a.nurse_id, "role": a.role} for a in assistants],
        })
    return result
