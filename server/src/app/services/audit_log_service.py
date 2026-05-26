"""Audit log service — create, trim, and inspect audit trail entries."""

import json
from datetime import datetime, timezone, timedelta

from app.models import db, AuditLog


# Default retention period in days
RETENTION_DAYS = 90


def _get_current_user_id():
    """Extract the authenticated user's ID from the JWT, or None."""
    try:
        from flask import has_request_context
        from flask_jwt_extended import get_jwt
        if has_request_context():
            claims = get_jwt()
            if claims:
                return int(claims.get("sub", 0))
    except Exception:
        pass
    return None


def _record_to_dict(record):
    """Convert a SQLAlchemy model instance to a plain dict for serialization."""
    if record is None:
        return None
    if isinstance(record, dict):
        return record
    cols = {}
    for c in record.__table__.columns:
        try:
            val = getattr(record, c.key)
            if isinstance(val, (datetime,)):
                val = val.isoformat()
            cols[c.key] = val
        except Exception:
            cols[c.key] = None
    return cols


def _serialize(obj):
    """Serialize a model instance to a JSON string for storage."""
    if obj is None:
        return None
    d = _record_to_dict(obj)
    return json.dumps(d, ensure_ascii=False, default=str) if d else None


def log_audit(action_type, table_name, record_id, old_record=None, new_record=None, notes=None):
    """Create a new audit log entry and add it to the session."""
    user_id = _get_current_user_id()
    old_data = _serialize(old_record)
    new_data = _serialize(new_record)
    log = AuditLog(
        user_id=user_id,
        action_timestamp=datetime.now(timezone.utc),
        action_type=action_type,
        table_name=table_name,
        record_id=record_id,
        old_data=old_data,
        new_data=new_data,
        notes=notes or None,
    )
    db.session.add(log)
    return log


def trim_audit_logs(days=None):
    """Delete audit log entries older than the given number of days."""
    if days is None:
        days = RETENTION_DAYS
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    deleted = AuditLog.query.filter(AuditLog.action_timestamp < cutoff).delete(synchronize_session="fetch")
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return deleted


def get_retention_info():
    """Return summary stats about the audit log table."""
    from sqlalchemy import func
    oldest = db.session.query(func.min(AuditLog.action_timestamp)).scalar()
    newest = db.session.query(func.max(AuditLog.action_timestamp)).scalar()
    total = AuditLog.query.count()
    return {
        "total_logs": total,
        "oldest": oldest.isoformat() if oldest else None,
        "newest": newest.isoformat() if newest else None,
        "retention_days": RETENTION_DAYS,
    }
