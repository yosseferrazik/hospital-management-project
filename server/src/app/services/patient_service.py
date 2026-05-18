from app.models import Patient
from app.services.base import parse_date, create_record, get_all, get_by_id, update_record, delete_record


def create_patient(data):
    return create_record(Patient,
        national_id=data["national_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        birth_date=parse_date(data["birth_date"], "%Y-%m-%d"),
        gender=data.get("gender").upper() if data.get("gender") else None,
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address"),
        emergency_contact_name=data.get("emergency_contact_name"),
        emergency_contact_phone=data.get("emergency_contact_phone"),
        blood_type=data.get("blood_type"),
        allergies=data.get("allergies"),
        health_card=data.get("health_card"),
    )


def get_patients():
    return get_all(Patient)


def get_patient(patient_id):
    return get_by_id(Patient, patient_id)


def update_patient(patient_id, data):
    patient = get_by_id(Patient, patient_id)
    return update_record(patient,
        national_id=data["national_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        birth_date=parse_date(data["birth_date"], "%Y-%m-%d"),
        gender=data.get("gender").upper() if data.get("gender") else None,
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address"),
        emergency_contact_name=data.get("emergency_contact_name"),
        emergency_contact_phone=data.get("emergency_contact_phone"),
        blood_type=data.get("blood_type"),
        allergies=data.get("allergies"),
        health_card=data.get("health_card"),
    )


def delete_patient(patient_id):
    patient = get_by_id(Patient, patient_id)
    return delete_record(patient)
