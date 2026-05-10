from app.models import db, OperatingTheater


def create_operating_theater(data):
    theater = OperatingTheater(theater_code=data["theater_code"], floor_id=data["floor_id"])
    db.session.add(theater)
    db.session.commit()
    return theater


def get_operating_theaters():
    return OperatingTheater.query.all()


def get_operating_theater(theater_id):
    return OperatingTheater.query.get(theater_id)


def update_operating_theater(theater_id, data):
    theater = OperatingTheater.query.get(theater_id)
    if theater:
        theater.theater_code = data["theater_code"]
        theater.floor_id = data["floor_id"]
        db.session.commit()
    return theater


def delete_operating_theater(theater_id):
    theater = OperatingTheater.query.get(theater_id)
    if theater:
        db.session.delete(theater)
        db.session.commit()
    return theater