from app.models import db, Room


def create_room(data):
    room = Room(room_number=data["room_number"], floor_id=data["floor_id"])
    db.session.add(room)
    db.session.commit()
    return room


def get_rooms():
    return Room.query.all()


def get_room(room_id):
    return Room.query.get(room_id)


def update_room(room_id, data):
    room = Room.query.get(room_id)
    if room:
        room.room_number = data["room_number"]
        room.floor_id = data["floor_id"]
        db.session.commit()
    return room


def delete_room(room_id):
    room = Room.query.get(room_id)
    if room:
        db.session.delete(room)
        db.session.commit()
    return room