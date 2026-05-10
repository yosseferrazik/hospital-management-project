from app.models import db, Patient
from datetime import datetime


def create_patient(data):
    patient = Patient(
        national_id=data["national_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        birth_date=datetime.strptime(data["birth_date"], "%Y-%m-%d"),
        gender=data.get("gender"),
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address"),
        emergency_contact_name=data.get("emergency_contact_name"),
        emergency_contact_phone=data.get("emergency_contact_phone"),
        blood_type=data.get("blood_type"),
        allergies=data.get("allergies"),
    )
    db.session.add(patient)
    db.session.commit()
    return patient


def get_patients():
    return Patient.query.all()


def get_patient(patient_id):
    return Patient.query.get(patient_id)


def update_patient(patient_id, data):
    patient = Patient.query.get(patient_id)
    if patient:
        patient.national_id = data["national_id"]
        patient.first_name = data["first_name"]
        patient.last_name = data["last_name"]
        patient.birth_date = datetime.strptime(data["birth_date"], "%Y-%m-%d")
        patient.gender = data.get("gender")
        patient.phone = data.get("phone")
        patient.email = data.get("email")
        patient.address = data.get("address")
        patient.emergency_contact_name = data.get("emergency_contact_name")
        patient.emergency_contact_phone = data.get("emergency_contact_phone")
        patient.blood_type = data.get("blood_type")
        patient.allergies = data.get("allergies")
        db.session.commit()
    return patient


def delete_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if patient:
        db.session.delete(patient)
        db.session.commit()
    return patient
