"""Scheduled appointment CRUD routes."""

from app.routes.base import make_crud_blueprint
from app.services.scheduled_appointment_service import create_scheduled_appointment, get_scheduled_appointments, get_scheduled_appointment, update_scheduled_appointment, delete_scheduled_appointment

scheduled_appointment_bp = make_crud_blueprint(
    "scheduled_appointment", "/api/scheduled_appointments",
    create_fn=create_scheduled_appointment, list_fn=get_scheduled_appointments, get_fn=get_scheduled_appointment,
    update_fn=update_scheduled_appointment, delete_fn=delete_scheduled_appointment,
    create_required=["visit_id", "appointment_date", "appointment_time"],
    update_required=["visit_id", "appointment_date", "appointment_time"],
    serialize=lambda a: {
        "appointment_id": a.appointment_id, "visit_id": a.visit_id,
        "appointment_date": str(a.appointment_date), "appointment_time": str(a.appointment_time), "status": a.status,
    },
)
