from app.models import db, ScheduledAppointment
from datetime import datetime


def create_scheduled_appointment(data):
    appointment = ScheduledAppointment(
        visit_id=data["visit_id"],
        appointment_date=datetime.strptime(data["appointment_date"], "%Y-%m-%d"),
        appointment_time=datetime.strptime(data["appointment_time"], "%H:%M:%S").time(),
        status=data.get("status", "SCHEDULED"),
    )
    db.session.add(appointment)
    db.session.commit()
    return appointment


def get_scheduled_appointments():
    return ScheduledAppointment.query.all()


def get_scheduled_appointment(appointment_id):
    return ScheduledAppointment.query.get(appointment_id)


def update_scheduled_appointment(appointment_id, data):
    appointment = ScheduledAppointment.query.get(appointment_id)
    if appointment:
        appointment.visit_id = data["visit_id"]
        appointment.appointment_date = datetime.strptime(data["appointment_date"], "%Y-%m-%d")
        appointment.appointment_time = datetime.strptime(data["appointment_time"], "%H:%M:%S").time()
        appointment.status = data.get("status", "SCHEDULED")
        db.session.commit()
    return appointment


def delete_scheduled_appointment(appointment_id):
    appointment = ScheduledAppointment.query.get(appointment_id)
    if appointment:
        db.session.delete(appointment)
        db.session.commit()
    return appointment