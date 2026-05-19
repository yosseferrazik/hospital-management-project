from flask import Blueprint, request, jsonify

from app.services.report_service import (
    visits_report,
    surgeries_report,
    admissions_report,
    medications_report,
    financial_report,
    radiology_report,
    doctor_workload_report,
    summary_report,
)

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


def _date_params():
    return {
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
    }


@reports_bp.route("/visits", methods=["GET"])
def report_visits():
    try:
        params = _date_params()
        params["specialty"] = request.args.get("specialty")
        params["doctor_id"] = request.args.get("doctor_id", type=int)
        return jsonify(visits_report(**params)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@reports_bp.route("/surgeries", methods=["GET"])
def report_surgeries():
    try:
        params = _date_params()
        params["procedure_type"] = request.args.get("procedure_type")
        params["surgeon_id"] = request.args.get("surgeon_id", type=int)
        return jsonify(surgeries_report(**params)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@reports_bp.route("/admissions", methods=["GET"])
def report_admissions():
    try:
        params = _date_params()
        params["floor_id"] = request.args.get("floor_id", type=int)
        return jsonify(admissions_report(**params)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@reports_bp.route("/medications", methods=["GET"])
def report_medications():
    try:
        return jsonify(medications_report(**_date_params())), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@reports_bp.route("/financial", methods=["GET"])
def report_financial():
    try:
        return jsonify(financial_report(**_date_params())), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@reports_bp.route("/radiology", methods=["GET"])
def report_radiology():
    try:
        params = _date_params()
        params["status"] = request.args.get("status")
        return jsonify(radiology_report(**params)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@reports_bp.route("/doctor-workload", methods=["GET"])
def report_doctor_workload():
    try:
        return jsonify(doctor_workload_report(**_date_params())), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@reports_bp.route("/summary", methods=["GET"])
def report_summary():
    try:
        return jsonify(summary_report(**_date_params())), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
