"""Dashboard routes — statistics endpoint and static HTML view."""

import os
from flask import Blueprint, jsonify, send_from_directory
from app.services.export_service import get_dashboard_stats

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


# --- GET /api/dashboard/stats — return aggregated hospital stats ---
@dashboard_bp.route("/stats", methods=["GET"])
def stats():
    try:
        return jsonify(get_dashboard_stats()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- GET /api/dashboard/view — serve the static dashboard HTML ---
@dashboard_bp.route("/view", methods=["GET"])
def view():
    return send_from_directory(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
        "dashboard.html",
    )
