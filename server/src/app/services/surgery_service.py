from app.models import db, Surgery, SurgeryAssistant
from sqlalchemy import and_
from datetime import datetime


def create_surgery(data):
    surgery = Surgery(
        patient_id=data["patient_id"],
        theater_id=data["theater_id"],
        primary_surgeon_id=data["primary_surgeon_id"],
        surgery_date=datetime.strptime(data["surgery_date"], "%Y-%m-%d"),
        start_time=datetime.strptime(data["start_time"], "%H:%M:%S").time(),
        end_time=datetime.strptime(data["end_time"], "%H:%M:%S").time(),
        procedure_type=data["procedure_type"],
        notes=data.get("notes"),
    )
    db.session.add(surgery)
    db.session.commit()
    return surgery


def get_surgeries():
    return Surgery.query.all()


def get_surgery(surgery_id):
    return Surgery.query.get(surgery_id)


def update_surgery(surgery_id, data):
    surgery = Surgery.query.get(surgery_id)
    if surgery:
        surgery.patient_id = data["patient_id"]
        surgery.theater_id = data["theater_id"]
        surgery.primary_surgeon_id = data["primary_surgeon_id"]
        surgery.surgery_date = datetime.strptime(data["surgery_date"], "%Y-%m-%d")
        surgery.start_time = datetime.strptime(data["start_time"], "%H:%M:%S").time()
        surgery.end_time = datetime.strptime(data["end_time"], "%H:%M:%S").time()
        surgery.procedure_type = data["procedure_type"]
        surgery.notes = data.get("notes")
        db.session.commit()
    return surgery


def delete_surgery(surgery_id):
    surgery = Surgery.query.get(surgery_id)
    if surgery:
        db.session.delete(surgery)
        db.session.commit()
    return surgery


def get_surgeries_by_date(date):
    surgeries = db.session.query(Surgery).filter(Surgery.surgery_date == date).all()
    result = []
    for s in surgeries:
        assistants = SurgeryAssistant.query.filter_by(surgery_id=s.surgery_id).all()
        result.append(
            {
                "surgery_id": s.surgery_id,
                "theater_id": s.theater_id,
                "patient": f"{s.patient.first_name} {s.patient.last_name}",
                "surgeon": f"{s.primary_surgeon.staff.first_name} {s.primary_surgeon.staff.last_name}",
                "start_time": str(s.start_time),
                "end_time": str(s.end_time),
                "procedure_type": s.procedure_type,
                "assistants": [
                    {"nurse_id": a.nurse_id, "role": a.role} for a in assistants
                ],
            }
        )
    return result
