from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, AuditLog, AppUser
from app.services.audit_log_service import log_audit, trim_audit_logs, get_retention_info

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
    ).outerjoin(AppUser, AppUser.user_id == AuditLog.user_id)

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
                "username": r.username or "SYSTEM",
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


@audit_bp.route("/diagnostics", methods=["GET"])
def diagnostics():
    try:
        total_logs = AuditLog.query.count()
        triggers_installed = False
        try:
            result = db.session.execute(db.text(
                "SELECT COUNT(*) FROM pg_trigger "
                "WHERE tgname LIKE 'audit_%'"
            )).scalar()
            triggers_installed = result > 0
        except Exception:
            pass

        return jsonify({
            "total_logs": total_logs,
            "triggers_installed": triggers_installed,
            "message": (
                "Audit logs found" if total_logs > 0 else
                ("Triggers installed but no logs yet. Perform some CRUD operations to generate audit entries."
                 if triggers_installed else
                 "No audit triggers found in the database. Run scripts/sql/security.sql to install them.")
            ),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@audit_bp.route("/retention", methods=["GET"])
def retention_info():
    try:
        return jsonify(get_retention_info()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@audit_bp.route("/test", methods=["POST"])
def test_audit():
    try:
        log = log_audit(
            action_type="TEST",
            table_name="audit_logs",
            record_id=None,
            notes="Test audit entry created at " + datetime.utcnow().isoformat(),
        )
        db.session.commit()
        return jsonify({"log_id": log.log_id, "status": "created"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@audit_bp.route("/cleanup", methods=["DELETE"])
@jwt_required()
def cleanup():
    days = request.args.get("days", 90, type=int)
    try:
        deleted = trim_audit_logs(days=days)
        return jsonify({"deleted": deleted, "retention_days": days}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
