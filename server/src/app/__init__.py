from datetime import datetime, timezone

from flask import Flask, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, get_jwt_identity, get_jwt
from flask_cors import CORS
from sqlalchemy import text
from app.config import Config
from app.models import db
from app.routes import (
    auth_bp,
    maintenance_bp,
    dummy_bp,
    floor_bp,
    room_bp,
    operating_theater_bp,
    medical_device_bp,
    medical_specialty_bp,
    patient_bp,
    visit_bp,
    scheduled_appointment_bp,
    medication_bp,
    prescription_bp,
    admission_bp,
    surgery_bp,
    surgery_assistant_bp,
    pharmacy_dispensation_bp,
    dispensation_item_bp,
    radiology_exam_bp,
    staff_bp,
    export_bp,
    dashboard_bp,
    audit_bp,
)


def _register_health_endpoint(app):
    @app.route("/health", methods=["GET"])
    def health():
        db_ok = False
        try:
            db.session.execute(db.text("SELECT 1"))
            db_ok = True
        except Exception:
            pass
        status_code = 200 if db_ok else 503
        return jsonify(
            {
                "status": "healthy" if db_ok else "degraded",
                "database": "connected" if db_ok else "disconnected",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ), status_code


def _set_session_vars():
    from flask import g
    try:
        claims = get_jwt()
        if claims:
            uid = claims.get("sub")
            sid = claims.get("staff_id")
            if uid:
                db.session.execute(text("SELECT set_config('app.current_user_id', :uid, true)"), {"uid": uid})
            if sid:
                db.session.execute(text("SELECT set_config('app.current_staff_id', :sid, true)"), {"sid": str(sid)})
    except Exception:
        pass


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)

    @app.route("/")
    def index():
        return redirect("/api/dashboard/view")

    @app.before_request
    def before_request():
        _set_session_vars()

    _register_health_endpoint(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(maintenance_bp)
    app.register_blueprint(dummy_bp)
    app.register_blueprint(floor_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(operating_theater_bp)
    app.register_blueprint(medical_device_bp)
    app.register_blueprint(medical_specialty_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(visit_bp)
    app.register_blueprint(scheduled_appointment_bp)
    app.register_blueprint(medication_bp)
    app.register_blueprint(prescription_bp)
    app.register_blueprint(admission_bp)
    app.register_blueprint(surgery_bp)
    app.register_blueprint(surgery_assistant_bp)
    app.register_blueprint(pharmacy_dispensation_bp)
    app.register_blueprint(dispensation_item_bp)
    app.register_blueprint(radiology_exam_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(audit_bp)

    with app.app_context():
        db.create_all()

    return app
