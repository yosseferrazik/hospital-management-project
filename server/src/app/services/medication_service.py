"""Medication service — CRUD delegation for Medication model."""

from app.models import Medication
from app.services.base import create_record, get_all, get_by_id, update_record, delete_record


def create_medication(data):
    return create_record(Medication, medication_name=data["medication_name"], description=data.get("description"))


def get_medications():
    return get_all(Medication)


def get_medication(medication_id):
    return get_by_id(Medication, medication_id)


def update_medication(medication_id, data):
    medication = get_by_id(Medication, medication_id)
    return update_record(medication, medication_name=data["medication_name"], description=data.get("description"))


def delete_medication(medication_id):
    medication = get_by_id(Medication, medication_id)
    return delete_record(medication)
