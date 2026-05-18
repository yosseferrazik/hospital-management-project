from app.models import PharmacyDispensation
from app.services.base import parse_date, create_record, get_all, get_by_id, update_record, delete_record


def create_pharmacy_dispensation(data):
    return create_record(PharmacyDispensation,
        admission_id=data["admission_id"],
        dispensed_at=parse_date(data.get("dispensed_at"), "%Y-%m-%d %H:%M:%S"),
        total_cost=data.get("total_cost", 0),
        notes=data.get("notes"),
    )


def get_pharmacy_dispensations():
    return get_all(PharmacyDispensation)


def get_pharmacy_dispensation(dispensation_id):
    return get_by_id(PharmacyDispensation, dispensation_id)


def update_pharmacy_dispensation(dispensation_id, data):
    dispensation = get_by_id(PharmacyDispensation, dispensation_id)
    return update_record(dispensation,
        admission_id=data["admission_id"],
        dispensed_at=parse_date(data.get("dispensed_at"), "%Y-%m-%d %H:%M:%S"),
        total_cost=data.get("total_cost", 0),
        notes=data.get("notes"),
    )


def delete_pharmacy_dispensation(dispensation_id):
    dispensation = get_by_id(PharmacyDispensation, dispensation_id)
    return delete_record(dispensation)
