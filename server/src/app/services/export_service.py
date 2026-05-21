import json
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from app.models import db, Visit, Patient, MedicalStaff, Staff, MedicalSpecialty, Surgery, Admission, NursingStaff, Room, Floor
from datetime import datetime, date, timedelta


def _visits_query(start_date, end_date):
    return (
        db.session.query(
            Visit.visit_id,
            Visit.visit_timestamp,
            Staff.first_name.label("doctor_first_name"),
            Staff.last_name.label("doctor_last_name"),
            MedicalStaff.license_number,
            Patient.national_id,
            Patient.first_name.label("patient_first_name"),
            Patient.last_name.label("patient_last_name"),
            Patient.health_card,
        )
        .join(MedicalStaff, MedicalStaff.staff_id == Visit.doctor_id)
        .join(Staff, Staff.staff_id == MedicalStaff.staff_id)
        .join(Patient, Patient.patient_id == Visit.patient_id)
        .filter(Visit.visit_timestamp >= start_date)
        .filter(Visit.visit_timestamp < end_date.replace(hour=23, minute=59, second=59))
        .order_by(Visit.visit_timestamp)
        .all()
    )


def _row_to_dict(row):
    ts = row.visit_timestamp
    return {
        "visit_id": row.visit_id,
        "date": ts.strftime("%Y-%m-%d") if hasattr(ts, "strftime") else str(ts),
        "doctor": {
            "name": f"{row.doctor_first_name} {row.doctor_last_name}",
            "license": row.license_number,
        },
        "patient": {
            "dni": row.national_id,
            "first_name": row.patient_first_name,
            "last_name": row.patient_last_name,
            "health_card": row.health_card or "",
        },
    }


def get_visits_data(start_date, end_date):
    rows = _visits_query(start_date, end_date)
    return [_row_to_dict(r) for r in rows]


def generate_json(data):
    return json.dumps({"visits": data}, indent=2, ensure_ascii=False)


def _build_xml_doc(data):
    root = Element("visits")
    for item in data:
        visit_el = SubElement(root, "visit")
        SubElement(visit_el, "visit_id").text = str(item["visit_id"])
        SubElement(visit_el, "date").text = item["date"]
        doctor_el = SubElement(visit_el, "doctor")
        SubElement(doctor_el, "name").text = item["doctor"]["name"]
        SubElement(doctor_el, "license").text = item["doctor"]["license"]
        patient_el = SubElement(visit_el, "patient")
        SubElement(patient_el, "dni").text = item["patient"]["dni"]
        SubElement(patient_el, "first_name").text = item["patient"]["first_name"]
        SubElement(patient_el, "last_name").text = item["patient"]["last_name"]
        SubElement(patient_el, "health_card").text = item["patient"]["health_card"]
    return root


def generate_xml(data):
    rough = tostring(_build_xml_doc(data), encoding="unicode")
    dom = minidom.parseString(rough.encode())
    return dom.toprettyxml(indent="  ")


def _schema_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "schemas")


def validate_json(data_str):
    import jsonschema
    schema_path = os.path.join(_schema_dir(), "visits.schema.json")
    with open(schema_path, encoding="utf-8") as f:
        schema = json.load(f)
    instance = json.loads(data_str)
    jsonschema.validate(instance, schema)


def validate_xml(data_str):
    import xmlschema
    schema_path = os.path.join(_schema_dir(), "visits.xsd")
    schema = xmlschema.XMLSchema(schema_path)
    schema.validate(data_str)


def get_dashboard_stats():
    today = date.today()
    start = datetime(today.year, today.month, today.day)

    visits_today = db.session.query(Visit).filter(Visit.visit_timestamp >= start).count()
    surgeries_today = db.session.query(Surgery).filter(Surgery.surgery_date == today).count()
    active_admissions = db.session.query(Admission).filter(Admission.actual_discharge_date.is_(None)).count()

    total_patients = db.session.query(Patient).count()
    total_staff = db.session.query(Staff).count()
    total_doctors = db.session.query(MedicalStaff).count()
    total_nurses = db.session.query(NursingStaff).count()

    by_specialty_rows = (
        db.session.query(
            MedicalSpecialty.name,
            db.func.count(Visit.visit_id).label("count"),
        )
        .join(MedicalStaff, MedicalStaff.staff_id == Visit.doctor_id)
        .join(MedicalSpecialty, MedicalSpecialty.specialty_id == MedicalStaff.specialty_id)
        .filter(Visit.visit_timestamp >= start)
        .group_by(MedicalSpecialty.name)
        .order_by(db.desc("count"))
        .all()
    )

    trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = datetime(day.year, day.month, day.day)
        day_end = day_start + timedelta(days=1)
        count = db.session.query(Visit).filter(
            Visit.visit_timestamp >= day_start,
            Visit.visit_timestamp < day_end
        ).count()
        trend.append({"date": day.isoformat(), "count": count})

    top_doctors = (
        db.session.query(
            Staff.first_name,
            Staff.last_name,
            db.func.count(Visit.visit_id).label("visit_count"),
        )
        .join(MedicalStaff, MedicalStaff.staff_id == Visit.doctor_id)
        .join(Staff, Staff.staff_id == MedicalStaff.staff_id)
        .filter(Visit.visit_timestamp >= start)
        .group_by(Staff.first_name, Staff.last_name)
        .order_by(db.desc("visit_count"))
        .limit(5)
        .all()
    )

    recent_admissions = (
        db.session.query(
            Patient.first_name,
            Patient.last_name,
            Admission.admission_date,
            Room.room_number,
            Floor.floor_number,
        )
        .join(Admission, Admission.patient_id == Patient.patient_id)
        .join(Room, Room.room_id == Admission.room_id)
        .join(Floor, Floor.floor_id == Room.floor_id)
        .filter(Admission.actual_discharge_date.is_(None))
        .order_by(Admission.admission_date.desc())
        .limit(10)
        .all()
    )

    return {
        "date": today.isoformat(),
        "visits_today": visits_today,
        "surgeries_today": surgeries_today,
        "active_admissions": active_admissions,
        "total_patients": total_patients,
        "total_staff": total_staff,
        "total_doctors": total_doctors,
        "total_nurses": total_nurses,
        "by_specialty": [{"specialty": r.name, "count": r.count} for r in by_specialty_rows],
        "visits_trend": trend,
        "top_doctors": [
            {"name": f"{r.first_name} {r.last_name}", "count": r.visit_count}
            for r in top_doctors
        ],
        "recent_admissions": [
            {
                "patient": f"{r.first_name} {r.last_name}",
                "since": r.admission_date.isoformat(),
                "room": r.room_number,
                "floor": r.floor_number,
            }
            for r in recent_admissions
        ],
    }
