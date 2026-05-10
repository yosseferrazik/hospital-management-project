from app.models import db, Admission
from datetime import datetime


def create_admission(data):
    admission = Admission(
        patient_id=data["patient_id"],
        room_id=data["room_id"],
        admission_date=datetime.strptime(data["admission_date"], "%Y-%m-%d %H:%M:%S") if "admission_date" in data else None,
        expected_discharge_date=datetime.strptime(data["expected_discharge_date"], "%Y-%m-%d") if "expected_discharge_date" in data else None,
        actual_discharge_date=datetime.strptime(data["actual_discharge_date"], "%Y-%m-%d") if "actual_discharge_date" in data else None,
    )
    db.session.add(admission)
    db.session.commit()
    return admission


def get_admissions():
    return Admission.query.all()


def get_admission(admission_id):
    return Admission.query.get(admission_id)


def update_admission(admission_id, data):
    admission = Admission.query.get(admission_id)
    if admission:
        admission.patient_id = data["patient_id"]
        admission.room_id = data["room_id"]
        admission.admission_date = datetime.strptime(data["admission_date"], "%Y-%m-%d %H:%M:%S") if "admission_date" in data else None
        admission.expected_discharge_date = datetime.strptime(data["expected_discharge_date"], "%Y-%m-%d") if "expected_discharge_date" in data else None
        admission.actual_discharge_date = datetime.strptime(data["actual_discharge_date"], "%Y-%m-%d") if "actual_discharge_date" in data else None
        db.session.commit()
    return admission


def delete_admission(admission_id):
    admission = Admission.query.get(admission_id)
    if admission:
        db.session.delete(admission)
        db.session.commit()
    return admission