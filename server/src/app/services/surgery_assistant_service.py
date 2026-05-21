from app.models import SurgeryAssistant
from app.services.base import create_record, get_all, get_by_id, update_record, delete_record


def create_surgery_assistant(data):
    return create_record(SurgeryAssistant, surgery_id=data["surgery_id"], nurse_id=data["nurse_id"], role=data["role"])


def get_surgery_assistants():
    return get_all(SurgeryAssistant)


def get_surgery_assistant(surgery_id, nurse_id):
    return get_by_id(SurgeryAssistant, (surgery_id, nurse_id))


def update_surgery_assistant(surgery_id, nurse_id, data):
    assistant = get_by_id(SurgeryAssistant, (surgery_id, nurse_id))
    return update_record(assistant, role=data["role"])


def delete_surgery_assistant(surgery_id, nurse_id):
    assistant = get_by_id(SurgeryAssistant, (surgery_id, nurse_id))
    return delete_record(assistant)
