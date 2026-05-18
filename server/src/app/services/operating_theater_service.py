from app.models import OperatingTheater
from app.services.base import create_record, get_all, get_by_id, update_record, delete_record


def create_operating_theater(data):
    return create_record(OperatingTheater, theater_code=data["theater_code"], floor_id=data["floor_id"])


def get_operating_theaters():
    return get_all(OperatingTheater)


def get_operating_theater(theater_id):
    return get_by_id(OperatingTheater, theater_id)


def update_operating_theater(theater_id, data):
    theater = get_by_id(OperatingTheater, theater_id)
    return update_record(theater, theater_code=data["theater_code"], floor_id=data["floor_id"])


def delete_operating_theater(theater_id):
    theater = get_by_id(OperatingTheater, theater_id)
    return delete_record(theater)
