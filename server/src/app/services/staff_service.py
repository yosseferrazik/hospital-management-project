from app.models import db, Staff, MedicalStaff, NursingStaff, GeneralStaff
from app.services.base import parse_date, get_all, get_by_id, update_record, delete_record


def get_staff():
    return get_all(Staff)


def get_staff_member(staff_id):
    return get_by_id(Staff, staff_id)


def update_staff(staff_id, data):
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
    staff = get_by_id(Staff, staff_id)
    return delete_record(staff)


def create_medical_staff(data):
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
    db.session.commit()
    return staff


def create_nursing_staff(data):
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
    db.session.commit()
    return staff


def create_general_staff(data):
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
    db.session.commit()
    return staff


def assign_nursing_to_doctor(nurse_id, doctor_id):
    nurse = get_by_id(NursingStaff, nurse_id)
    if not nurse:
        raise ValueError("Nurse not found")
    nurse.assigned_doctor_id = doctor_id
    nurse.assigned_floor_id = None
    db.session.commit()
    return nurse


def assign_nursing_to_floor(nurse_id, floor_id):
    nurse = get_by_id(NursingStaff, nurse_id)
    if not nurse:
        raise ValueError("Nurse not found")
    nurse.assigned_floor_id = floor_id
    nurse.assigned_doctor_id = None
    db.session.commit()
    return nurse
