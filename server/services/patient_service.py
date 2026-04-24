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
