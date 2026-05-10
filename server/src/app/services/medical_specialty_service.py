from app.models import db, MedicalSpecialty


def create_medical_specialty(data):
    specialty = MedicalSpecialty(name=data["name"], description=data.get("description"))
    db.session.add(specialty)
    db.session.commit()
    return specialty


def get_medical_specialties():
    return MedicalSpecialty.query.all()


def get_medical_specialty(specialty_id):
    return MedicalSpecialty.query.get(specialty_id)


def update_medical_specialty(specialty_id, data):
    specialty = MedicalSpecialty.query.get(specialty_id)
    if specialty:
        specialty.name = data["name"]
        specialty.description = data.get("description")
        db.session.commit()
    return specialty


def delete_medical_specialty(specialty_id):
    specialty = MedicalSpecialty.query.get(specialty_id)
    if specialty:
        db.session.delete(specialty)
        db.session.commit()
    return specialty