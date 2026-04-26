from app.models import db, Staff, MedicalStaff, NursingStaff, GeneralStaff
from datetime import datetime


def create_medical_staff(data):
    staff = Staff(
        national_id=data["national_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        birth_date=datetime.strptime(data["birth_date"], "%Y-%m-%d"),
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
    db.session.commit()
    return staff


def create_nursing_staff(data):
    staff = Staff(
        national_id=data["national_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        birth_date=datetime.strptime(data["birth_date"], "%Y-%m-%d"),
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
    db.session.commit()
    return staff


def create_general_staff(data):
    staff = Staff(
        national_id=data["national_id"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        birth_date=datetime.strptime(data["birth_date"], "%Y-%m-%d"),
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
    db.session.commit()
    return staff


def assign_nursing_to_doctor(nurse_id, doctor_id):
    nurse = NursingStaff.query.get(nurse_id)
    if not nurse:
        raise ValueError("Nurse not found")
    nurse.assigned_doctor_id = doctor_id
    nurse.assigned_floor_id = None
    db.session.commit()
    return nurse


def assign_nursing_to_floor(nurse_id, floor_id):
    nurse = NursingStaff.query.get(nurse_id)
    if not nurse:
        raise ValueError("Nurse not found")
    nurse.assigned_floor_id = floor_id
    nurse.assigned_doctor_id = None
    db.session.commit()
    return nurse
