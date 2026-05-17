from datetime import datetime, timezone

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
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


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    JWTManager(app)
    CORS(app)

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

    with app.app_context():
        db.create_all()

    return app
