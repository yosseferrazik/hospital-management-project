from app.models import Floor
from app.services.base import create_record, get_all, get_by_id, update_record, delete_record


def create_floor(data):
    return create_record(Floor, floor_number=data["floor_number"])


def get_floors():
    return get_all(Floor)


def get_floor(floor_id):
    return get_by_id(Floor, floor_id)


def update_floor(floor_id, data):
    floor = get_by_id(Floor, floor_id)
    return update_record(floor, floor_number=data["floor_number"])


def delete_floor(floor_id):
    floor = get_by_id(Floor, floor_id)
    return delete_record(floor)
