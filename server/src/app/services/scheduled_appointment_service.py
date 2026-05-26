"""Scheduled appointment service — CRUD delegation for ScheduledAppointment."""

from app.models import ScheduledAppointment
from app.services.base import parse_date, parse_time, create_record, get_all, get_by_id, update_record, delete_record


def create_scheduled_appointment(data):
    return create_record(ScheduledAppointment,
        visit_id=data["visit_id"],
        appointment_date=parse_date(data["appointment_date"], "%Y-%m-%d"),
        appointment_time=parse_time(data["appointment_time"]),
        status=data.get("status", "SCHEDULED"),
    )


def get_scheduled_appointments():
    return get_all(ScheduledAppointment)


def get_scheduled_appointment(appointment_id):
    return get_by_id(ScheduledAppointment, appointment_id)


def update_scheduled_appointment(appointment_id, data):
    appointment = get_by_id(ScheduledAppointment, appointment_id)
    return update_record(appointment,
        visit_id=data["visit_id"],
        appointment_date=parse_date(data["appointment_date"], "%Y-%m-%d"),
        appointment_time=parse_time(data["appointment_time"]),
        status=data.get("status", "SCHEDULED"),
    )


def delete_scheduled_appointment(appointment_id):
    appointment = get_by_id(ScheduledAppointment, appointment_id)
    return delete_record(appointment)
