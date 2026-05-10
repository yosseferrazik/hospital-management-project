from app.models import db, SurgeryAssistant


def create_surgery_assistant(data):
    assistant = SurgeryAssistant(surgery_id=data["surgery_id"], nurse_id=data["nurse_id"], role=data["role"])
    db.session.add(assistant)
    db.session.commit()
    return assistant


def get_surgery_assistants():
    return SurgeryAssistant.query.all()


def get_surgery_assistant(surgery_id, nurse_id):
    return SurgeryAssistant.query.get((surgery_id, nurse_id))


def update_surgery_assistant(surgery_id, nurse_id, data):
    assistant = SurgeryAssistant.query.get((surgery_id, nurse_id))
    if assistant:
        assistant.role = data["role"]
        db.session.commit()
    return assistant


def delete_surgery_assistant(surgery_id, nurse_id):
    assistant = SurgeryAssistant.query.get((surgery_id, nurse_id))
    if assistant:
        db.session.delete(assistant)
        db.session.commit()
    return assistant