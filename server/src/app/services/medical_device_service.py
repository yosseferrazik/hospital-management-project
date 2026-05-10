from app.models import db, MedicalDevice


def create_medical_device(data):
    device = MedicalDevice(device_type=data["device_type"], theater_id=data["theater_id"], quantity=data.get("quantity", 1))
    db.session.add(device)
    db.session.commit()
    return device


def get_medical_devices():
    return MedicalDevice.query.all()


def get_medical_device(device_id):
    return MedicalDevice.query.get(device_id)


def update_medical_device(device_id, data):
    device = MedicalDevice.query.get(device_id)
    if device:
        device.device_type = data["device_type"]
        device.theater_id = data["theater_id"]
        device.quantity = data.get("quantity", 1)
        db.session.commit()
    return device


def delete_medical_device(device_id):
    device = MedicalDevice.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
    return device