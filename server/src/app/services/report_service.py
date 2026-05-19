from datetime import datetime, date, timedelta, time
from collections import defaultdict

from app.models import db, Patient, Staff, MedicalStaff, NursingStaff, Visit, ScheduledAppointment
from app.models import Surgery, SurgeryAssistant, Admission, Room, Floor, MedicalSpecialty
from app.models import Prescription, Medication, PharmacyDispensation, DispensationItem
from app.models import RadiologyExam, OperatingTheater


def _date_range(start_str, end_str):
    today = date.today()
    start = datetime.strptime(start_str, "%Y-%m-%d") if start_str else datetime.combine(today - timedelta(days=30), time.min)
    end = datetime.strptime(end_str, "%Y-%m-%d") if end_str else datetime.combine(today, time.max)
    return start, end


def visits_report(start_date=None, end_date=None, specialty=None, doctor_id=None):
    start, end = _date_range(start_date, end_date)
    q = (
        db.session.query(
            Visit.visit_id,
            Visit.visit_timestamp,
            Visit.diagnosis,
            Visit.notes,
            Patient.patient_id.label("patient_id"),
            Patient.first_name.label("patient_first_name"),
            Patient.last_name.label("patient_last_name"),
            Staff.first_name.label("doctor_first_name"),
            Staff.last_name.label("doctor_last_name"),
            MedicalSpecialty.name.label("specialty"),
        )
        .join(Patient, Patient.patient_id == Visit.patient_id)
        .join(MedicalStaff, MedicalStaff.staff_id == Visit.doctor_id)
        .join(Staff, Staff.staff_id == MedicalStaff.staff_id)
        .join(MedicalSpecialty, MedicalSpecialty.specialty_id == MedicalStaff.specialty_id)
        .filter(Visit.visit_timestamp >= start)
        .filter(Visit.visit_timestamp <= end)
    )
    if specialty:
        q = q.filter(MedicalSpecialty.name == specialty)
    if doctor_id:
        q = q.filter(Visit.doctor_id == doctor_id)
    q = q.order_by(Visit.visit_timestamp.desc())

    rows = q.all()
    records = []
    for r in rows:
        records.append({
            "visit_id": r.visit_id,
            "date": r.visit_timestamp.strftime("%Y-%m-%d %H:%M") if r.visit_timestamp else "",
            "patient": f"{r.patient_first_name} {r.patient_last_name}",
            "patient_id": r.patient_id,
            "doctor": f"{r.doctor_first_name} {r.doctor_last_name}",
            "specialty": r.specialty,
            "diagnosis": r.diagnosis or "",
            "notes": r.notes or "",
        })
    return {
        "total": len(records),
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
        "records": records,
    }


def surgeries_report(start_date=None, end_date=None, procedure_type=None, surgeon_id=None):
    start, end = _date_range(start_date, end_date)
    q = (
        db.session.query(
            Surgery.surgery_id,
            Surgery.surgery_date,
            Surgery.start_time,
            Surgery.end_time,
            Surgery.procedure_type,
            Surgery.notes,
            Patient.first_name.label("patient_first_name"),
            Patient.last_name.label("patient_last_name"),
            Staff.first_name.label("surgeon_first_name"),
            Staff.last_name.label("surgeon_last_name"),
            OperatingTheater.theater_code,
            Floor.floor_number,
        )
        .join(Patient, Patient.patient_id == Surgery.patient_id)
        .join(MedicalStaff, MedicalStaff.staff_id == Surgery.primary_surgeon_id)
        .join(Staff, Staff.staff_id == MedicalStaff.staff_id)
        .join(OperatingTheater, OperatingTheater.theater_id == Surgery.theater_id)
        .join(Floor, Floor.floor_id == OperatingTheater.floor_id)
        .filter(Surgery.surgery_date >= start.date())
        .filter(Surgery.surgery_date <= end.date())
    )
    if procedure_type:
        q = q.filter(Surgery.procedure_type.ilike(f"%{procedure_type}%"))
    if surgeon_id:
        q = q.filter(Surgery.primary_surgeon_id == surgeon_id)
    q = q.order_by(Surgery.surgery_date.desc())

    rows = q.all()
    records = []
    for r in rows:
        duration = ""
        if r.start_time and r.end_time:
            s = datetime.combine(date.today(), r.start_time)
            e = datetime.combine(date.today(), r.end_time)
            delta = (e - s).seconds // 60
            duration = f"{delta} min"
        records.append({
            "surgery_id": r.surgery_id,
            "date": r.surgery_date.strftime("%Y-%m-%d") if r.surgery_date else "",
            "procedure": r.procedure_type,
            "patient": f"{r.patient_first_name} {r.patient_last_name}",
            "surgeon": f"{r.surgeon_first_name} {r.surgeon_last_name}",
            "theater": r.theater_code,
            "floor": r.floor_number,
            "start": str(r.start_time)[:5] if r.start_time else "",
            "end": str(r.end_time)[:5] if r.end_time else "",
            "duration": duration,
            "notes": r.notes or "",
        })
    return {
        "total": len(records),
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
        "records": records,
    }


def admissions_report(start_date=None, end_date=None, floor_id=None):
    start, end = _date_range(start_date, end_date)
    q = (
        db.session.query(
            Admission.admission_id,
            Admission.admission_date,
            Admission.expected_discharge_date,
            Admission.actual_discharge_date,
            Patient.first_name.label("patient_first_name"),
            Patient.last_name.label("patient_last_name"),
            Room.room_number,
            Floor.floor_number,
            Floor.floor_id,
        )
        .join(Patient, Patient.patient_id == Admission.patient_id)
        .join(Room, Room.room_id == Admission.room_id)
        .join(Floor, Floor.floor_id == Room.floor_id)
        .filter(Admission.admission_date >= start)
        .filter(Admission.admission_date <= end)
    )
    if floor_id:
        q = q.filter(Floor.floor_id == floor_id)
    q = q.order_by(Admission.admission_date.desc())

    rows = q.all()
    records = []
    for r in rows:
        stay_days = None
        if r.admission_date and r.actual_discharge_date:
            stay_days = (r.actual_discharge_date - r.admission_date.date()).days
        elif r.admission_date:
            stay_days = (date.today() - r.admission_date.date()).days
        records.append({
            "admission_id": r.admission_id,
            "admission_date": r.admission_date.strftime("%Y-%m-%d") if r.admission_date else "",
            "expected_discharge": str(r.expected_discharge_date) if r.expected_discharge_date else "",
            "actual_discharge": str(r.actual_discharge_date) if r.actual_discharge_date else "",
            "patient": f"{r.patient_first_name} {r.patient_last_name}",
            "room": r.room_number,
            "floor": r.floor_number,
            "stay_days": stay_days,
        })
    return {
        "total": len(records),
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
        "records": records,
    }


def medications_report(start_date=None, end_date=None):
    start, end = _date_range(start_date, end_date)
    rows = (
        db.session.query(
            Medication.medication_name,
            db.func.count(Prescription.prescription_id).label("prescription_count"),
            db.func.count(db.distinct(Prescription.visit_id)).label("visit_count"),
        )
        .join(Prescription, Prescription.medication_id == Medication.medication_id)
        .join(Visit, Visit.visit_id == Prescription.visit_id)
        .filter(Visit.visit_timestamp >= start)
        .filter(Visit.visit_timestamp <= end)
        .group_by(Medication.medication_name)
        .order_by(db.desc("prescription_count"))
        .all()
    )
    records = [
        {
            "medication": r.medication_name,
            "prescriptions": r.prescription_count,
            "visits": r.visit_count,
        }
        for r in rows
    ]
    return {
        "total": len(records),
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
        "records": records,
    }


def financial_report(start_date=None, end_date=None):
    start, end = _date_range(start_date, end_date)
    rows = (
        db.session.query(
            PharmacyDispensation.dispensation_id,
            PharmacyDispensation.dispensed_at,
            PharmacyDispensation.total_cost,
            PharmacyDispensation.notes,
            Patient.first_name.label("patient_first_name"),
            Patient.last_name.label("patient_last_name"),
        )
        .join(Admission, Admission.admission_id == PharmacyDispensation.admission_id)
        .join(Patient, Patient.patient_id == Admission.patient_id)
        .filter(PharmacyDispensation.dispensed_at >= start)
        .filter(PharmacyDispensation.dispensed_at <= end)
        .order_by(PharmacyDispensation.dispensed_at.desc())
        .all()
    )
    records = []
    total_cost = 0
    for r in rows:
        cost = float(r.total_cost) if r.total_cost else 0
        total_cost += cost
        records.append({
            "dispensation_id": r.dispensation_id,
            "date": r.dispensed_at.strftime("%Y-%m-%d") if r.dispensed_at else "",
            "patient": f"{r.patient_first_name} {r.patient_last_name}",
            "total_cost": cost,
            "notes": r.notes or "",
        })
    return {
        "total": len(records),
        "total_cost": round(total_cost, 2),
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
        "records": records,
    }


def radiology_report(start_date=None, end_date=None, status=None):
    start, end = _date_range(start_date, end_date)
    q = (
        db.session.query(
            RadiologyExam.exam_id,
            RadiologyExam.exam_type,
            RadiologyExam.requested_at,
            RadiologyExam.performed_at,
            RadiologyExam.status,
            RadiologyExam.radiologist_report,
            Patient.first_name.label("patient_first_name"),
            Patient.last_name.label("patient_last_name"),
            Staff.first_name.label("doctor_first_name"),
            Staff.last_name.label("doctor_last_name"),
        )
        .join(Patient, Patient.patient_id == RadiologyExam.patient_id)
        .join(MedicalStaff, MedicalStaff.staff_id == RadiologyExam.requesting_doctor_id)
        .join(Staff, Staff.staff_id == MedicalStaff.staff_id)
        .filter(RadiologyExam.requested_at >= start)
        .filter(RadiologyExam.requested_at <= end)
    )
    if status:
        q = q.filter(RadiologyExam.status == status)
    q = q.order_by(RadiologyExam.requested_at.desc())

    rows = q.all()
    records = []
    for r in rows:
        records.append({
            "exam_id": r.exam_id,
            "exam_type": r.exam_type,
            "requested_at": r.requested_at.strftime("%Y-%m-%d %H:%M") if r.requested_at else "",
            "performed_at": r.performed_at.strftime("%Y-%m-%d %H:%M") if r.performed_at else "",
            "status": r.status,
            "patient": f"{r.patient_first_name} {r.patient_last_name}",
            "requesting_doctor": f"{r.doctor_first_name} {r.doctor_last_name}",
            "has_report": bool(r.radiologist_report),
        })
    return {
        "total": len(records),
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
        "records": records,
    }


def doctor_workload_report(start_date=None, end_date=None):
    start, end = _date_range(start_date, end_date)
    visit_subq = (
        db.session.query(
            Visit.doctor_id,
            db.func.count(Visit.visit_id).label("visit_count"),
            db.func.count(db.distinct(Visit.patient_id)).label("patients_in_visits"),
        )
        .filter(Visit.visit_timestamp >= start, Visit.visit_timestamp <= end)
        .group_by(Visit.doctor_id)
        .subquery()
    )
    surgery_subq = (
        db.session.query(
            Surgery.primary_surgeon_id,
            db.func.count(Surgery.surgery_id).label("surgery_count"),
        )
        .filter(Surgery.surgery_date >= start.date(), Surgery.surgery_date <= end.date())
        .group_by(Surgery.primary_surgeon_id)
        .subquery()
    )
    rows = (
        db.session.query(
            Staff.first_name,
            Staff.last_name,
            MedicalSpecialty.name.label("specialty"),
            db.func.coalesce(visit_subq.c.visit_count, 0).label("visit_count"),
            db.func.coalesce(surgery_subq.c.surgery_count, 0).label("surgery_count"),
            db.func.coalesce(visit_subq.c.patients_in_visits, 0).label("patient_count"),
        )
        .join(MedicalStaff, MedicalStaff.staff_id == Staff.staff_id)
        .join(MedicalSpecialty, MedicalSpecialty.specialty_id == MedicalStaff.specialty_id)
        .outerjoin(visit_subq, visit_subq.c.doctor_id == MedicalStaff.staff_id)
        .outerjoin(surgery_subq, surgery_subq.c.primary_surgeon_id == MedicalStaff.staff_id)
        .order_by(db.text("visit_count DESC"))
        .all()
    )
    records = [
        {
            "doctor": f"{r.first_name} {r.last_name}",
            "specialty": r.specialty,
            "visits": r.visit_count,
            "surgeries": r.surgery_count,
            "patients": r.patient_count,
        }
        for r in rows
    ]
    return {
        "total": len(records),
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
        "records": records,
    }


def summary_report(start_date=None, end_date=None):
    start, end = _date_range(start_date, end_date)
    total_patients = Patient.query.count()
    total_staff = Staff.query.count()
    total_doctors = MedicalStaff.query.count()
    total_nurses = NursingStaff.query.count()

    visits_in_range = Visit.query.filter(Visit.visit_timestamp >= start, Visit.visit_timestamp <= end).count()
    surgeries_in_range = Surgery.query.filter(Surgery.surgery_date >= start.date(), Surgery.surgery_date <= end.date()).count()
    admissions_in_range = Admission.query.filter(Admission.admission_date >= start, Admission.admission_date <= end).count()

    active_admissions = Admission.query.filter(Admission.actual_discharge_date == None).count()
    total_rooms = Room.query.count()

    top_diagnoses_rows = (
        db.session.query(
            Visit.diagnosis,
            db.func.count(Visit.visit_id).label("count"),
        )
        .filter(Visit.visit_timestamp >= start)
        .filter(Visit.visit_timestamp <= end)
        .filter(Visit.diagnosis != None)
        .filter(Visit.diagnosis != "")
        .group_by(Visit.diagnosis)
        .order_by(db.desc("count"))
        .limit(10)
        .all()
    )
    top_diagnoses = [{"diagnosis": r.diagnosis, "count": r.count} for r in top_diagnoses_rows]

    surgeries_by_type_rows = (
        db.session.query(
            Surgery.procedure_type,
            db.func.count(Surgery.surgery_id).label("count"),
        )
        .filter(Surgery.surgery_date >= start.date())
        .filter(Surgery.surgery_date <= end.date())
        .group_by(Surgery.procedure_type)
        .order_by(db.desc("count"))
        .all()
    )
    surgeries_by_type = [{"procedure": r.procedure_type, "count": r.count} for r in surgeries_by_type_rows]

    return {
        "period": {"start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")},
        "totals": {
            "patients": total_patients,
            "staff": total_staff,
            "doctors": total_doctors,
            "nurses": total_nurses,
        },
        "activity": {
            "visits": visits_in_range,
            "surgeries": surgeries_in_range,
            "admissions": admissions_in_range,
        },
        "occupancy": {
            "active_admissions": active_admissions,
            "total_rooms": total_rooms,
            "occupancy_rate": round((active_admissions / total_rooms * 100) if total_rooms else 0, 1),
        },
        "top_diagnoses": top_diagnoses,
        "surgeries_by_type": surgeries_by_type,
    }
