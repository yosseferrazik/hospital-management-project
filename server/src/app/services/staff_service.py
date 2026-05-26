"""Staff service — CRUD, type-specific creation, and nurse assignment."""

from app.models import db, Staff, MedicalStaff, NursingStaff, GeneralStaff
from app.services.base import parse_date, get_all, get_by_id, update_record, delete_record


def get_staff():
    """Return all staff records."""
    return get_all(Staff)


def get_staff_member(staff_id):
    """Return a single staff record by ID."""
    return get_by_id(Staff, staff_id)


def update_staff(staff_id, data):
    """Update base staff fields."""
    staff = get_by_id(Staff, staff_id)
    return update_record(staff,
        national_id=data["national_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        birth_date=parse_date(data["birth_date"], "%Y-%m-%d"),
        phone=data.get("phone"),
        ssn=data.get("ssn"),
        email=data.get("email"),
        address=data.get("address"),
        staff_type=data["staff_type"],
    )


def delete_staff(staff_id):
    """Delete a staff record."""
    staff = get_by_id(Staff, staff_id)
    return delete_record(staff)


def _commit():
    """Commit the current DB session, rolling back on failure."""
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def create_medical_staff(data):
    """Create a Staff record + associated MedicalStaff row."""
    staff = Staff(
        national_id=data["national_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        birth_date=parse_date(data["birth_date"], "%Y-%m-%d"),
        phone=data.get("phone"),
        ssn=data.get("ssn"),
        email=data.get("email"),
        address=data.get("address"),
        staff_type="MEDICAL",
    )
    db.session.add(staff)
    db.session.flush()
    medical = MedicalStaff(
        staff_id=staff.staff_id,
        specialty_id=data["specialty_id"],
        license_number=data["license_number"],
        curriculum=data.get("curriculum"),
    )
    db.session.add(medical)
    _commit()
    return staff


def create_nursing_staff(data):
    """Create a Staff record + associated NursingStaff row."""
    staff = Staff(
        national_id=data["national_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        birth_date=parse_date(data["birth_date"], "%Y-%m-%d"),
        phone=data.get("phone"),
        ssn=data.get("ssn"),
        email=data.get("email"),
        address=data.get("address"),
        staff_type="NURSING",
    )
    db.session.add(staff)
    db.session.flush()
    nursing = NursingStaff(
        staff_id=staff.staff_id,
        nursing_license=data["nursing_license"],
        assigned_doctor_id=data.get("assigned_doctor_id"),
        assigned_floor_id=data.get("assigned_floor_id"),
        certifications=data.get("certifications"),
    )
    db.session.add(nursing)
    _commit()
    return staff


def create_general_staff(data):
    """Create a Staff record + associated GeneralStaff row."""
    staff = Staff(
        national_id=data["national_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        birth_date=parse_date(data["birth_date"], "%Y-%m-%d"),
        phone=data.get("phone"),
        ssn=data.get("ssn"),
        email=data.get("email"),
        address=data.get("address"),
        staff_type="GENERAL",
    )
    db.session.add(staff)
    db.session.flush()
    general = GeneralStaff(staff_id=staff.staff_id, job_type=data["job_type"])
    db.session.add(general)
    _commit()
    return staff


def assign_nursing_to_doctor(nurse_id, doctor_id):
    """Assign a nurse to a specific doctor (removes floor assignment)."""
    nurse = get_by_id(NursingStaff, nurse_id)
    if not nurse:
        raise ValueError("Nurse not found")
    nurse.assigned_doctor_id = doctor_id
    nurse.assigned_floor_id = None
    _commit()
    return nurse


def assign_nursing_to_floor(nurse_id, floor_id):
    """Assign a nurse to a specific floor (removes doctor assignment)."""
    nurse = get_by_id(NursingStaff, nurse_id)
    if not nurse:
        raise ValueError("Nurse not found")
    nurse.assigned_floor_id = floor_id
    nurse.assigned_doctor_id = None
    _commit()
    return nurse
