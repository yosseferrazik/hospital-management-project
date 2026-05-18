from flask import Blueprint, jsonify
from app.services.export_service import get_dashboard_stats

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
def stats():
    try:
        return jsonify(get_dashboard_stats()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
