"""Dispensation item service — CRUD delegation for DispensationItem."""

from app.models import DispensationItem
from app.services.base import create_record, get_all, get_by_id, update_record, delete_record


def create_dispensation_item(data):
    return create_record(DispensationItem, dispensation_id=data["dispensation_id"], medication_id=data["medication_id"], quantity=data["quantity"], unit_price=data["unit_price"])


def get_dispensation_items():
    return get_all(DispensationItem)


def get_dispensation_item(item_id):
    return get_by_id(DispensationItem, item_id)


def update_dispensation_item(item_id, data):
    item = get_by_id(DispensationItem, item_id)
    return update_record(item, dispensation_id=data["dispensation_id"], medication_id=data["medication_id"], quantity=data["quantity"], unit_price=data["unit_price"])


def delete_dispensation_item(item_id):
    item = get_by_id(DispensationItem, item_id)
    return delete_record(item)
