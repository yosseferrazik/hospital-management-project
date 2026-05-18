import json
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from app.models import db, Visit, Patient, MedicalStaff, Staff, MedicalSpecialty
from datetime import datetime, date


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
    total = db.session.query(Visit).filter(Visit.visit_timestamp >= start).count()
    rows = (
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
    return {
        "date": today.isoformat(),
        "total_visits": total,
        "by_specialty": [{"specialty": r.name, "count": r.count} for r in rows],
    }
