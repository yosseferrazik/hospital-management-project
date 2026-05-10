from app.models import db, Medication


def create_medication(data):
    medication = Medication(medication_name=data["medication_name"], description=data.get("description"))
    db.session.add(medication)
    db.session.commit()
    return medication


def get_medications():
    return Medication.query.all()


def get_medication(medication_id):
    return Medication.query.get(medication_id)


def update_medication(medication_id, data):
    medication = Medication.query.get(medication_id)
    if medication:
        medication.medication_name = data["medication_name"]
        medication.description = data.get("description")
        db.session.commit()
    return medication


def delete_medication(medication_id):
    medication = Medication.query.get(medication_id)
    if medication:
        db.session.delete(medication)
        db.session.commit()
    return medication