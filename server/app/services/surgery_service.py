from app.models import db, Surgery, SurgeryAssistant
from sqlalchemy import and_


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
