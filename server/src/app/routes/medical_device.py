from app.routes.base import make_crud_blueprint
from app.services.medical_device_service import create_medical_device, get_medical_devices, get_medical_device, update_medical_device, delete_medical_device

medical_device_bp = make_crud_blueprint(
    "medical_device", "/api/medical_devices",
    create_fn=create_medical_device, list_fn=get_medical_devices, get_fn=get_medical_device,
    update_fn=update_medical_device, delete_fn=delete_medical_device,
    create_required=["device_type", "theater_id"], update_required=["device_type", "theater_id"],
    serialize=lambda d: {"device_id": d.device_id, "device_type": d.device_type, "theater_id": d.theater_id, "quantity": d.quantity},
)
