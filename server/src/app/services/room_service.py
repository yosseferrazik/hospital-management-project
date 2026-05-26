"""Room service — CRUD delegation for Room model."""

from app.models import Room
from app.services.base import create_record, get_all, get_by_id, update_record, delete_record


def create_room(data):
    return create_record(Room, room_number=data["room_number"], floor_id=data["floor_id"])


def get_rooms():
    return get_all(Room)


def get_room(room_id):
    return get_by_id(Room, room_id)


def update_room(room_id, data):
    room = get_by_id(Room, room_id)
    return update_record(room, room_number=data["room_number"], floor_id=data["floor_id"])


def delete_room(room_id):
    room = get_by_id(Room, room_id)
    return delete_record(room)
