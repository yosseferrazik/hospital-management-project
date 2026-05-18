from flask import Blueprint, request, jsonify, Response
from app.services.export_service import (
    get_visits_data,
    generate_json,
    generate_xml,
    validate_json,
    validate_xml,
)
from app.utils.api_client import send_visits

export_bp = Blueprint("export", __name__, url_prefix="/api/export")


@export_bp.route("/visits", methods=["GET"])
def download_visits():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    fmt = request.args.get("format", "json")
    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required (YYYY-MM-DD)"}), 400
    try:
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    if end < start:
        return jsonify({"error": "end_date must be after start_date"}), 400
    try:
        data = get_visits_data(start, end)
        if not data:
            return jsonify({"error": "No visits found in the given date range"}), 404
        if fmt == "xml":
            output = generate_xml(data)
            validate_xml(output)
            return Response(output, mimetype="application/xml", headers={
                "Content-Disposition": f"attachment; filename=visits_{start_date}_{end_date}.xml"
            })
        output = generate_json(data)
        validate_json(output)
        return Response(output, mimetype="application/json", headers={
            "Content-Disposition": f"attachment; filename=visits_{start_date}_{end_date}.json"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@export_bp.route("/send", methods=["POST"])
def send_export():
    body = request.get_json(force=True) or {}
    start_date = body.get("start_date")
    end_date = body.get("end_date")
    fmt = body.get("format", "json")
    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required"}), 400
    try:
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    if end < start:
        return jsonify({"error": "end_date must be after start_date"}), 400
    try:
        data = get_visits_data(start, end)
        if not data:
            return jsonify({"error": "No visits found in the given date range"}), 404
        payload = generate_xml(data) if fmt == "xml" else generate_json(data)
        if fmt == "xml":
            validate_xml(payload)
        else:
            validate_json(payload)
        resp = send_visits(payload, format=fmt)
        return jsonify({"success": True, "status_code": resp.status_code}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
