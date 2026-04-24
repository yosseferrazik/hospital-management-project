from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class AppUser(db.Model):
    __tablename__ = "app_users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    staff_id = db.Column(
        db.Integer, db.ForeignKey("staff.staff_id"), nullable=False, unique=True
    )
    role = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Staff(db.Model):
    __tablename__ = "staff"
    staff_id = db.Column(db.Integer, primary_key=True)
    national_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20))
    ssn = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(255), unique=True)
    address = db.Column(db.Text)
    hire_date = db.Column(db.Date, default=datetime.utcnow)
    staff_type = db.Column(db.String(50), nullable=False)  # MEDICAL, NURSING, GENERAL


class MedicalStaff(db.Model):
    __tablename__ = "medical_staff"
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.staff_id"), primary_key=True)
    specialty_id = db.Column(
        db.Integer, db.ForeignKey("medical_specialties.specialty_id"), nullable=False
    )
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    curriculum = db.Column(db.Text)


class NursingStaff(db.Model):
    __tablename__ = "nursing_staff"
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.staff_id"), primary_key=True)
    nursing_license = db.Column(db.String(50), unique=True, nullable=False)
    assigned_doctor_id = db.Column(db.Integer, db.ForeignKey("medical_staff.staff_id"))
    assigned_floor_id = db.Column(db.Integer, db.ForeignKey("floors.floor_id"))
    certifications = db.Column(db.Text)


class GeneralStaff(db.Model):
    __tablename__ = "general_staff"
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.staff_id"), primary_key=True)
    job_type = db.Column(db.String(100), nullable=False)


class Patient(db.Model):
    __tablename__ = "patients"
    patient_id = db.Column(db.Integer, primary_key=True)
    national_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    address = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(200))
    emergency_contact_phone = db.Column(db.String(20))
    blood_type = db.Column(db.String(5))
    allergies = db.Column(db.Text)


class Surgery(db.Model):
    __tablename__ = "surgeries"
    surgery_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.patient_id"), nullable=False
    )
    theater_id = db.Column(
        db.Integer, db.ForeignKey("operating_theaters.theater_id"), nullable=False
    )
    primary_surgeon_id = db.Column(
        db.Integer, db.ForeignKey("medical_staff.staff_id"), nullable=False
    )
    surgery_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    procedure_type = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text)

    patient = db.relationship("Patient")
    primary_surgeon = db.relationship("MedicalStaff")


class SurgeryAssistant(db.Model):
    __tablename__ = "surgery_assistants"
    surgery_id = db.Column(
        db.Integer, db.ForeignKey("surgeries.surgery_id"), primary_key=True
    )
    nurse_id = db.Column(
        db.Integer, db.ForeignKey("nursing_staff.staff_id"), primary_key=True
    )
    role = db.Column(db.String(100), nullable=False)


class ScheduledAppointment(db.Model):
    __tablename__ = "scheduled_appointments"
    appointment_id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(
        db.Integer, db.ForeignKey("visits.visit_id"), unique=True, nullable=False
    )
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), default="SCHEDULED")


class Visit(db.Model):
    __tablename__ = "visits"
    visit_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.patient_id"), nullable=False
    )
    doctor_id = db.Column(
        db.Integer, db.ForeignKey("medical_staff.staff_id"), nullable=False
    )
    visit_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    diagnosis = db.Column(db.Text)
    notes = db.Column(db.Text)

    patient = db.relationship("Patient")
    doctor = db.relationship("MedicalStaff")


class DummyRegistry(db.Model):
    __tablename__ = "dummy_registry"
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
