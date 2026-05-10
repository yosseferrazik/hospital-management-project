from app.models import db, Floor


def create_floor(data):
    floor = Floor(floor_number=data["floor_number"])
    db.session.add(floor)
    db.session.commit()
    return floor


def get_floors():
    return Floor.query.all()


def get_floor(floor_id):
    return Floor.query.get(floor_id)


def update_floor(floor_id, data):
    floor = Floor.query.get(floor_id)
    if floor:
        floor.floor_number = data["floor_number"]
        db.session.commit()
    return floor


def delete_floor(floor_id):
    floor = Floor.query.get(floor_id)
    if floor:
        db.session.delete(floor)
        db.session.commit()
    return floor