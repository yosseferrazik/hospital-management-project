from app.models import db, PharmacyDispensation
from datetime import datetime


def create_pharmacy_dispensation(data):
    dispensation = PharmacyDispensation(
        admission_id=data["admission_id"],
        dispensed_at=datetime.strptime(data["dispensed_at"], "%Y-%m-%d %H:%M:%S") if "dispensed_at" in data else None,
        total_cost=data.get("total_cost", 0),
        notes=data.get("notes"),
    )
    db.session.add(dispensation)
    db.session.commit()
    return dispensation


def get_pharmacy_dispensations():
    return PharmacyDispensation.query.all()


def get_pharmacy_dispensation(dispensation_id):
    return PharmacyDispensation.query.get(dispensation_id)


def update_pharmacy_dispensation(dispensation_id, data):
    dispensation = PharmacyDispensation.query.get(dispensation_id)
    if dispensation:
        dispensation.admission_id = data["admission_id"]
        dispensation.dispensed_at = datetime.strptime(data["dispensed_at"], "%Y-%m-%d %H:%M:%S") if "dispensed_at" in data else None
        dispensation.total_cost = data.get("total_cost", 0)
        dispensation.notes = data.get("notes")
        db.session.commit()
    return dispensation


def delete_pharmacy_dispensation(dispensation_id):
    dispensation = PharmacyDispensation.query.get(dispensation_id)
    if dispensation:
        db.session.delete(dispensation)
        db.session.commit()
    return dispensation