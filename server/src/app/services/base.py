from app.models import db
from datetime import datetime, time


def parse_date(value, fmt):
    if not value:
        return None
    try:
        return datetime.strptime(value, fmt)
    except (ValueError, TypeError):
        return None


def parse_time(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%H:%M:%S").time()
    except (ValueError, TypeError):
        return None


def create_record(model_class, commit=True, **kwargs):
    record = model_class(**kwargs)
    db.session.add(record)
    if commit:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
    return record


def get_all(model_class):
    return model_class.query.all()


def get_by_id(model_class, record_id):
    return model_class.query.get(record_id)


def update_record(record, **kwargs):
    if not record:
        return None
    for key, value in kwargs.items():
        setattr(record, key, value)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return record


def delete_record(record):
    if not record:
        return None
    db.session.delete(record)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return record


def bulk_commit():
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
