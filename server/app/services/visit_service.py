from app.models import db, ScheduledAppointment, Visit
from sqlalchemy import and_


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
