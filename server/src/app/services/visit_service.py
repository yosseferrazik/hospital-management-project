"""Visit service — CRUD delegation with scheduled visit lookup."""

from app.models import db, ScheduledAppointment, Visit
from app.services.base import parse_date, create_record, get_all, get_by_id, update_record, delete_record


def create_visit(data):
    return create_record(Visit,
        patient_id=data["patient_id"],
        doctor_id=data["doctor_id"],
        visit_timestamp=parse_date(data.get("visit_timestamp"), "%Y-%m-%d %H:%M:%S"),
        diagnosis=data.get("diagnosis"),
        notes=data.get("notes"),
    )


def get_visits():
    return get_all(Visit)


def get_visit(visit_id):
    return get_by_id(Visit, visit_id)


def update_visit(visit_id, data):
    visit = get_by_id(Visit, visit_id)
    return update_record(visit,
        patient_id=data["patient_id"],
        doctor_id=data["doctor_id"],
        visit_timestamp=parse_date(data.get("visit_timestamp"), "%Y-%m-%d %H:%M:%S"),
        diagnosis=data.get("diagnosis"),
        notes=data.get("notes"),
    )


def delete_visit(visit_id):
    visit = get_by_id(Visit, visit_id)
    return delete_record(visit)


def get_scheduled_visits_by_date(date):
    """Return scheduled appointments for a given date with patient/doctor details."""
    appointments = (
        db.session.query(ScheduledAppointment)
        .filter(ScheduledAppointment.appointment_date == date)
        .all()
    )
    result = []
    for app in appointments:
        visit = get_by_id(Visit, app.visit_id)
        if visit:
            patient = visit.patient
            doctor_staff = visit.doctor.staff if visit.doctor else None
            result.append({
                "appointment_id": app.appointment_id,
                "time": str(app.appointment_time),
                "patient": f"{patient.first_name} {patient.last_name}" if patient else "Unknown",
                "doctor": f"{doctor_staff.first_name} {doctor_staff.last_name}" if doctor_staff else "Unknown",
                "diagnosis": visit.diagnosis,
                "status": app.status,
            })
    return result
