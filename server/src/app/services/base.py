"""Base service layer — generic CRUD helpers with automatic audit logging."""

from app.models import db
from datetime import datetime


def _get_pk(record):
    """Extract the primary key value from a model instance."""
    try:
        mapper = record.__class__.__mapper__
        pk_cols = mapper.primary_key
        if pk_cols:
            return getattr(record, pk_cols[0].key)
    except Exception:
        pass
    return None


# Tables excluded from automatic audit logging
_def_audit_tables = {
    "audit_logs", "dummy_registry", "app_users",
}


def _try_audit(action, record, old_record=None, new_record=None):
    """Write an audit log entry for a CRUD operation if the table is tracked."""
    table = record.__class__.__tablename__ if record else None
    if not table or table in _def_audit_tables:
        return
    pk = _get_pk(record)
    try:
        from app.services.audit_log_service import log_audit
        log_audit(
            action_type=action,
            table_name=table,
            record_id=pk,
            old_record=old_record,
            new_record=new_record if action != "DELETE" else None,
            notes=f"Auto-audit: {action} on {table}",
        )
    except Exception:
        pass


def parse_date(value, fmt):
    """Parse a date string using the given format, returning None on failure."""
    if not value:
        return None
    try:
        return datetime.strptime(value, fmt)
    except (ValueError, TypeError):
        return None


def parse_time(value):
    """Parse a time string (HH:MM:SS), returning None on failure."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%H:%M:%S").time()
    except (ValueError, TypeError):
        return None


def create_record(model_class, commit=True, **kwargs):
    """Create a new record, auto-audit, and commit."""
    record = model_class(**kwargs)
    db.session.add(record)
    if commit:
        try:
            db.session.flush()
            _try_audit("INSERT", record, new_record=record)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
    return record


def get_all(model_class):
    """Return all records for the given model."""
    return model_class.query.all()


def get_by_id(model_class, record_id):
    """Fetch a single record by primary key."""
    return model_class.query.get(record_id)


def update_record(record, **kwargs):
    """Update a record with the given attributes, auto-audit, and commit."""
    if not record:
        return None
    old_data = None
    try:
        from app.services.audit_log_service import _record_to_dict
        old_data = _record_to_dict(record)
    except Exception:
        pass
    for key, value in kwargs.items():
        setattr(record, key, value)
    try:
        db.session.flush()
        _try_audit("UPDATE", record, old_record=old_data, new_record=record)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return record


def delete_record(record):
    """Delete a record, auto-audit, and commit."""
    if not record:
        return None
    try:
        db.session.flush()
        _try_audit("DELETE", record, old_record=record)
        db.session.delete(record)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return record



