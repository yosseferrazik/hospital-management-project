from datetime import datetime

from flask import Blueprint, request, jsonify
from app.models import db, AuditLog, AppUser

audit_bp = Blueprint("audit", __name__, url_prefix="/api/audit-logs")


@audit_bp.route("", methods=["GET"])
def list_audit_logs():
    table = request.args.get("table")
    action = request.args.get("action")
    user_id = request.args.get("user_id")
    start = request.args.get("start_date")
    end = request.args.get("end_date")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    query = db.session.query(
        AuditLog.log_id,
        AuditLog.user_id,
        AppUser.username,
        AuditLog.action_timestamp,
        AuditLog.action_type,
        AuditLog.table_name,
        AuditLog.record_id,
        AuditLog.notes,
    ).join(AppUser, AppUser.user_id == AuditLog.user_id)

    if table:
        query = query.filter(AuditLog.table_name == table)
    if action:
        query = query.filter(AuditLog.action_type == action)
    if user_id:
        query = query.filter(AuditLog.user_id == int(user_id))
    if start:
        query = query.filter(AuditLog.action_timestamp >= datetime.fromisoformat(start))
    if end:
        query = query.filter(AuditLog.action_timestamp <= datetime.fromisoformat(end))

    total = query.count()
    rows = query.order_by(AuditLog.log_id.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "logs": [
            {
                "log_id": r.log_id,
                "user_id": r.user_id,
                "username": r.username,
                "timestamp": r.action_timestamp.isoformat() if r.action_timestamp else None,
                "action": r.action_type,
                "table": r.table_name,
                "record_id": r.record_id,
                "notes": r.notes,
            }
            for r in rows
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }), 200
