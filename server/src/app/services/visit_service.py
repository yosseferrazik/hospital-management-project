from app.models import db, ScheduledAppointment, Visit
from sqlalchemy import and_
from datetime import datetime


def create_visit(data):
    visit = Visit(
        patient_id=data["patient_id"],
        doctor_id=data["doctor_id"],
        visit_timestamp=datetime.strptime(data["visit_timestamp"], "%Y-%m-%d %H:%M:%S") if "visit_timestamp" in data else None,
        diagnosis=data.get("diagnosis"),
        notes=data.get("notes"),
    )
    db.session.add(visit)
    db.session.commit()
    return visit


def get_visits():
    return Visit.query.all()


def get_visit(visit_id):
    return Visit.query.get(visit_id)


def update_visit(visit_id, data):
    visit = Visit.query.get(visit_id)
    if visit:
        visit.patient_id = data["patient_id"]
        visit.doctor_id = data["doctor_id"]
        visit.visit_timestamp = datetime.strptime(data["visit_timestamp"], "%Y-%m-%d %H:%M:%S") if "visit_timestamp" in data else None
        visit.diagnosis = data.get("diagnosis")
        visit.notes = data.get("notes")
        db.session.commit()
    return visit


def delete_visit(visit_id):
    visit = Visit.query.get(visit_id)
    if visit:
        db.session.delete(visit)
        db.session.commit()
    return visit


def get_scheduled_visits_by_date(date):
    appointments = (
        db.session.query(ScheduledAppointment)
        .filter(ScheduledAppointment.appointment_date == date)
        .all()
    )
    result = []
    for app in appointments:
        visit = Visit.query.get(app.visit_id)
        if visit:
            result.append(
                {
                    "appointment_id": app.appointment_id,
                    "time": str(app.appointment_time),
                    "patient": f"{visit.patient.first_name} {visit.patient.last_name}",
                    "doctor": f"{visit.doctor.staff.first_name} {visit.doctor.staff.last_name}",
                    "diagnosis": visit.diagnosis,
                    "status": app.status,
                }
            )
    return result
