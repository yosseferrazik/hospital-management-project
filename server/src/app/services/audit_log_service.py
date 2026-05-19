from datetime import datetime, timezone, timedelta

from app.models import db, AuditLog


RETENTION_DAYS = 90


def trim_audit_logs(days=None):
    if days is None:
        days = RETENTION_DAYS
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    deleted = AuditLog.query.filter(AuditLog.action_timestamp < cutoff).delete()
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return deleted


def get_retention_info():
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
