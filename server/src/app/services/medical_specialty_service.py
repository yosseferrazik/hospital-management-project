"""Medical specialty service — CRUD delegation for MedicalSpecialty."""

from app.models import MedicalSpecialty
from app.services.base import create_record, get_all, get_by_id, update_record, delete_record


def create_medical_specialty(data):
    return create_record(MedicalSpecialty, name=data["name"], description=data.get("description"))


def get_medical_specialties():
    return get_all(MedicalSpecialty)


def get_medical_specialty(specialty_id):
    return get_by_id(MedicalSpecialty, specialty_id)


def update_medical_specialty(specialty_id, data):
    specialty = get_by_id(MedicalSpecialty, specialty_id)
    return update_record(specialty, name=data["name"], description=data.get("description"))


def delete_medical_specialty(specialty_id):
    specialty = get_by_id(MedicalSpecialty, specialty_id)
    return delete_record(specialty)
