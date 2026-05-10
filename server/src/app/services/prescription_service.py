from app.models import db, Prescription
from datetime import datetime


def create_prescription(data):
    prescription = Prescription(
        visit_id=data["visit_id"],
        medication_id=data["medication_id"],
        dosage=data["dosage"],
        frequency=data["frequency"],
        duration_days=data.get("duration_days"),
        start_date=datetime.strptime(data["start_date"], "%Y-%m-%d") if "start_date" in data else None,
    )
    db.session.add(prescription)
    db.session.commit()
    return prescription


def get_prescriptions():
    return Prescription.query.all()


def get_prescription(prescription_id):
    return Prescription.query.get(prescription_id)


def update_prescription(prescription_id, data):
    prescription = Prescription.query.get(prescription_id)
    if prescription:
        prescription.visit_id = data["visit_id"]
        prescription.medication_id = data["medication_id"]
        prescription.dosage = data["dosage"]
        prescription.frequency = data["frequency"]
        prescription.duration_days = data.get("duration_days")
        prescription.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d") if "start_date" in data else None
        db.session.commit()
    return prescription


def delete_prescription(prescription_id):
    prescription = Prescription.query.get(prescription_id)
    if prescription:
        db.session.delete(prescription)
        db.session.commit()
    return prescription