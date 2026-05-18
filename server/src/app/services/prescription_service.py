from app.models import Prescription
from app.services.base import parse_date, create_record, get_all, get_by_id, update_record, delete_record


def create_prescription(data):
    return create_record(Prescription,
        visit_id=data["visit_id"],
        medication_id=data["medication_id"],
        dosage=data["dosage"],
        frequency=data["frequency"],
        duration_days=data.get("duration_days"),
        start_date=parse_date(data.get("start_date"), "%Y-%m-%d"),
    )


def get_prescriptions():
    return get_all(Prescription)


def get_prescription(prescription_id):
    return get_by_id(Prescription, prescription_id)


def update_prescription(prescription_id, data):
    prescription = get_by_id(Prescription, prescription_id)
    return update_record(prescription,
        visit_id=data["visit_id"],
        medication_id=data["medication_id"],
        dosage=data["dosage"],
        frequency=data["frequency"],
        duration_days=data.get("duration_days"),
        start_date=parse_date(data.get("start_date"), "%Y-%m-%d"),
    )


def delete_prescription(prescription_id):
    prescription = get_by_id(Prescription, prescription_id)
    return delete_record(prescription)
