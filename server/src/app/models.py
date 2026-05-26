"""SQLAlchemy database models for the hospital management system."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import INET

"""SQLAlchemy database instance."""
db = SQLAlchemy()


class AppUser(db.Model):
    """Application user account with JWT authentication."""
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Staff(db.Model):
    """Hospital staff member base record."""
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
    hire_date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())
    staff_type = db.Column(db.String(50), nullable=False)


class MedicalSpecialty(db.Model):
    """Medical specialty classification."""
    __tablename__ = "medical_specialties"
    specialty_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    medical_staff = db.relationship(
        "MedicalStaff",
        secondary="medical_staff_specialties",
        back_populates="specialties",
    )


class MedicalStaff(db.Model):
    """Medical doctor or physician staff member."""
    __tablename__ = "medical_staff"
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.staff_id"), primary_key=True)
    specialty_id = db.Column(
        db.Integer, db.ForeignKey("medical_specialties.specialty_id"), nullable=False
    )
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    curriculum = db.Column(db.Text)

    staff = db.relationship("Staff", backref=db.backref("medical_staff", uselist=False, cascade="all, delete-orphan"))

    specialties = db.relationship(
        "MedicalSpecialty",
        secondary="medical_staff_specialties",
        back_populates="medical_staff",
    )


class MedicalStaffSpecialty(db.Model):
    """Many-to-many link between medical staff and specialties."""
    __tablename__ = "medical_staff_specialties"
    medical_staff_specialty_id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(
        db.Integer, db.ForeignKey("medical_staff.staff_id"), nullable=False
    )
    specialty_id = db.Column(
        db.Integer, db.ForeignKey("medical_specialties.specialty_id"), nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint("staff_id", "specialty_id", name="uq_staff_specialty"),
    )


class NursingStaff(db.Model):
    """Nursing staff member record."""
    __tablename__ = "nursing_staff"
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.staff_id"), primary_key=True)
    nursing_license = db.Column(db.String(50), unique=True, nullable=False)
    assigned_doctor_id = db.Column(db.Integer, db.ForeignKey("medical_staff.staff_id"))
    assigned_floor_id = db.Column(db.Integer, db.ForeignKey("floors.floor_id"))
    certifications = db.Column(db.Text)

    staff = db.relationship("Staff", backref=db.backref("nursing_staff", uselist=False, cascade="all, delete-orphan"))


class GeneralStaff(db.Model):
    """Non-medical hospital staff member."""
    __tablename__ = "general_staff"
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.staff_id"), primary_key=True)
    job_type = db.Column(db.String(100), nullable=False)

    staff = db.relationship("Staff", backref=db.backref("general_staff", uselist=False, cascade="all, delete-orphan"))


class Floor(db.Model):
    """Hospital floor level."""
    __tablename__ = "floors"
    floor_id = db.Column(db.Integer, primary_key=True)
    floor_number = db.Column(db.Integer, nullable=False, unique=True)


class Room(db.Model):
    """Patient room within a floor."""
    __tablename__ = "rooms"
    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), nullable=False)
    floor_id = db.Column(db.Integer, db.ForeignKey("floors.floor_id"), nullable=False)

    floor = db.relationship("Floor", backref="rooms")


class OperatingTheater(db.Model):
    """Surgical operating theater room."""
    __tablename__ = "operating_theaters"
    theater_id = db.Column(db.Integer, primary_key=True)
    theater_code = db.Column(db.String(20), unique=True, nullable=False)
    floor_id = db.Column(db.Integer, db.ForeignKey("floors.floor_id"), nullable=False)

    floor = db.relationship("Floor", backref="theaters")


class MedicalDevice(db.Model):
    """Medical equipment assigned to an operating theater."""
    __tablename__ = "medical_devices"
    device_id = db.Column(db.Integer, primary_key=True)
    device_type = db.Column(db.String(100), nullable=False)
    theater_id = db.Column(
        db.Integer, db.ForeignKey("operating_theaters.theater_id"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False, default=1)

    theater = db.relationship("OperatingTheater", backref="devices")


class Patient(db.Model):
    """Hospital patient personal and medical record."""
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
    health_card = db.Column(db.String(50))


class Visit(db.Model):
    """Patient clinical visit record."""
    __tablename__ = "visits"
    visit_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.patient_id"), nullable=False
    )
    doctor_id = db.Column(
        db.Integer, db.ForeignKey("medical_staff.staff_id"), nullable=False
    )
    visit_timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    diagnosis = db.Column(db.Text)
    notes = db.Column(db.Text)

    patient = db.relationship("Patient", backref=db.backref("visits", passive_deletes=True))
    doctor = db.relationship("MedicalStaff", backref="visits")


class ScheduledAppointment(db.Model):
    """Scheduled patient appointment linked to a visit."""
    __tablename__ = "scheduled_appointments"
    appointment_id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(
        db.Integer, db.ForeignKey("visits.visit_id"), unique=True, nullable=False
    )
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), default="SCHEDULED")

    visit = db.relationship("Visit", backref="appointment")


class Surgery(db.Model):
    """Surgical procedure record."""
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

    patient = db.relationship("Patient", backref=db.backref("surgeries", passive_deletes=True))
    theater = db.relationship("OperatingTheater", backref="surgeries")
    primary_surgeon = db.relationship("MedicalStaff", backref="lead_surgeries")


class SurgeryAssistant(db.Model):
    """Nurse assisting in a surgery procedure."""
    __tablename__ = "surgery_assistants"
    surgery_id = db.Column(
        db.Integer, db.ForeignKey("surgeries.surgery_id"), primary_key=True
    )
    nurse_id = db.Column(
        db.Integer, db.ForeignKey("nursing_staff.staff_id"), primary_key=True
    )
    role = db.Column(db.String(100), nullable=False)

    surgery = db.relationship("Surgery", backref=db.backref("assistants", cascade="all, delete-orphan"))
    nurse = db.relationship("NursingStaff", backref=db.backref("assisted_surgeries", cascade="all, delete-orphan"))


class Medication(db.Model):
    """Medication catalog entry."""
    __tablename__ = "medications"
    medication_id = db.Column(db.Integer, primary_key=True)
    medication_name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text)


class Prescription(db.Model):
    """Medication prescription issued during a visit."""
    __tablename__ = "prescriptions"
    prescription_id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey("visits.visit_id"), nullable=False)
    medication_id = db.Column(
        db.Integer, db.ForeignKey("medications.medication_id"), nullable=False
    )
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    duration_days = db.Column(db.Integer)
    start_date = db.Column(db.Date, default=lambda: datetime.now(timezone.utc).date())

    visit = db.relationship("Visit", backref="prescriptions")
    medication = db.relationship("Medication", backref="prescriptions")


class Admission(db.Model):
    """Patient hospitalization admission record."""
    __tablename__ = "admissions"
    admission_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.patient_id"), nullable=False
    )
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.room_id"), nullable=False)
    admission_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expected_discharge_date = db.Column(db.Date)
    actual_discharge_date = db.Column(db.Date)

    patient = db.relationship("Patient", backref=db.backref("admissions", passive_deletes=True))
    room = db.relationship("Room", backref="admissions")


class PharmacyDispensation(db.Model):
    """Pharmacy medication dispensation batch."""
    __tablename__ = "pharmacy_dispensations"
    dispensation_id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(
        db.Integer, db.ForeignKey("admissions.admission_id"), nullable=False
    )
    dispensed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    total_cost = db.Column(db.Numeric(10, 2), default=0)
    notes = db.Column(db.Text)

    admission = db.relationship("Admission", backref="dispensations")


class DispensationItem(db.Model):
    """Individual medication item within a dispensation."""
    __tablename__ = "dispensation_items"
    item_id = db.Column(db.Integer, primary_key=True)
    dispensation_id = db.Column(
        db.Integer,
        db.ForeignKey("pharmacy_dispensations.dispensation_id"),
        nullable=False,
    )
    medication_id = db.Column(
        db.Integer, db.ForeignKey("medications.medication_id"), nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    dispensation = db.relationship("PharmacyDispensation", backref="items")
    medication = db.relationship("Medication", backref="dispensation_items")


class RadiologyExam(db.Model):
    """Radiology imaging exam request and results."""
    __tablename__ = "radiology_exams"
    exam_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patients.patient_id"), nullable=False
    )
    requesting_doctor_id = db.Column(
        db.Integer, db.ForeignKey("medical_staff.staff_id"), nullable=False
    )
    exam_type = db.Column(db.String(100), nullable=False)
    requested_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    performed_at = db.Column(db.DateTime)
    result_image_url = db.Column(db.Text)
    radiologist_report = db.Column(db.Text)
    status = db.Column(db.String(50), default="REQUESTED")

    patient = db.relationship("Patient", backref=db.backref("radiology_exams", passive_deletes=True))
    requesting_doctor = db.relationship("MedicalStaff", backref="requested_exams")


class AuditLog(db.Model):
    """System audit trail for data changes."""
    __tablename__ = "audit_logs"
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("app_users.user_id"))
    action_timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    action_type = db.Column(db.String(50), nullable=False)
    table_name = db.Column(db.String(100))
    record_id = db.Column(db.Integer)
    old_data = db.Column(db.Text)
    new_data = db.Column(db.Text)
    ip_address = db.Column(INET)
    notes = db.Column(db.Text)

    user = db.relationship("AppUser", backref="audit_logs")


class DummyRegistry(db.Model):
    """Placeholder registry for dummy data tracking."""
    __tablename__ = "dummy_registry"
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
