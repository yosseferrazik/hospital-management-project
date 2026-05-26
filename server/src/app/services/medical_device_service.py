"""Medical device service — CRUD delegation for MedicalDevice."""

from app.models import MedicalDevice
from app.services.base import create_record, get_all, get_by_id, update_record, delete_record


def create_medical_device(data):
    return create_record(MedicalDevice, device_type=data["device_type"], theater_id=data["theater_id"], quantity=data.get("quantity", 1))


def get_medical_devices():
    return get_all(MedicalDevice)


def get_medical_device(device_id):
    return get_by_id(MedicalDevice, device_id)


def update_medical_device(device_id, data):
    device = get_by_id(MedicalDevice, device_id)
    return update_record(device, device_type=data["device_type"], theater_id=data["theater_id"], quantity=data.get("quantity", 1))


def delete_medical_device(device_id):
    device = get_by_id(MedicalDevice, device_id)
    return delete_record(device)
