import random
from datetime import datetime, timedelta

from faker import Faker

from app.models import (
    Admission,
    DispensationItem,
    DummyRegistry,
    Floor,
    GeneralStaff,
    MedicalDevice,
    MedicalSpecialty,
    MedicalStaff,
    Medication,
    NursingStaff,
    OperatingTheater,
    Patient,
    PharmacyDispensation,
    Prescription,
    RadiologyExam,
    Room,
    ScheduledAppointment,
    Staff,
    Surgery,
    SurgeryAssistant,
    Visit,
    db,
)

fake = Faker("es_ES")


def _register(table_name, record_id):
    db.session.add(DummyRegistry(table_name=table_name, record_id=record_id))


def _random_birth_date(min_age=22, max_age=85):
    age = random.randint(min_age, max_age)
    return datetime.utcnow().date() - timedelta(days=age * 365 + random.randint(0, 300))


def _unique_email(prefix):
    return f"{prefix}.{fake.unique.lexify(text='??????')}@example.test"


def _ensure_support_data():
    specialties = MedicalSpecialty.query.all()
    if not specialties:
        for name in ["Cardiology", "Neurology", "Traumatology", "Pediatrics"]:
            specialty = MedicalSpecialty(name=name, description=fake.sentence(nb_words=8))
            db.session.add(specialty)
            db.session.flush()
            _register("medical_specialties", specialty.specialty_id)
        db.session.commit()
        specialties = MedicalSpecialty.query.all()

    floors = Floor.query.all()
    if not floors:
        for number in range(1, 5):
            floor = Floor(floor_number=number)
            db.session.add(floor)
            db.session.flush()
            _register("floors", floor.floor_id)
        db.session.commit()
        floors = Floor.query.all()

    rooms = Room.query.all()
    if not rooms:
        for floor in floors:
            for idx in range(1, 5):
                room = Room(room_number=f"{floor.floor_number}0{idx}", floor_id=floor.floor_id)
                db.session.add(room)
                db.session.flush()
                _register("rooms", room.room_id)
        db.session.commit()
        rooms = Room.query.all()

    theaters = OperatingTheater.query.all()
    if not theaters:
        for floor in floors[:2]:
            theater = OperatingTheater(theater_code=f"OT-{floor.floor_number}", floor_id=floor.floor_id)
            db.session.add(theater)
            db.session.flush()
            _register("operating_theaters", theater.theater_id)
        db.session.commit()
        theaters = OperatingTheater.query.all()

    devices = MedicalDevice.query.all()
    if not devices:
        for theater in theaters:
            for device_name in ["Monitor", "Ventilator"]:
                device = MedicalDevice(device_type=device_name, theater_id=theater.theater_id, quantity=random.randint(1, 5))
                db.session.add(device)
                db.session.flush()
                _register("medical_devices", device.device_id)
        db.session.commit()

    medications = Medication.query.all()
    if not medications:
        for name in ["Paracetamol", "Ibuprofen", "Amoxicillin", "Omeprazole", "Atorvastatin"]:
            medication = Medication(medication_name=name, description=fake.sentence(nb_words=6))
            db.session.add(medication)
            db.session.flush()
            _register("medications", medication.medication_id)
        db.session.commit()
        medications = Medication.query.all()

    return specialties, floors, Room.query.all(), OperatingTheater.query.all(), Medication.query.all()


def _create_staff_batch(specialties):
    doctors = []
    nurses = []
    general_staff_members = []

    for index in range(5):
        staff = Staff(
            national_id=fake.unique.numerify(text="#########"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            birth_date=_random_birth_date(),
            phone=fake.phone_number(),
            ssn=fake.unique.numerify(text="#########"),
            email=_unique_email("doctor"),
            address=fake.address(),
            staff_type="MEDICAL",
        )
        db.session.add(staff)
        db.session.flush()
        _register("staff", staff.staff_id)
        doctor = MedicalStaff(
            staff_id=staff.staff_id,
            specialty_id=random.choice(specialties).specialty_id,
            license_number=f"DOC-{fake.unique.numerify(text='######')}",
            curriculum=fake.text(max_nb_chars=120),
        )
        db.session.add(doctor)
        db.session.flush()
        _register("medical_staff", doctor.staff_id)
        doctors.append(doctor)

    for index in range(8):
        staff = Staff(
            national_id=fake.unique.numerify(text="#########"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            birth_date=_random_birth_date(),
            phone=fake.phone_number(),
            ssn=fake.unique.numerify(text="#########"),
            email=_unique_email("nurse"),
            address=fake.address(),
            staff_type="NURSING",
        )
        db.session.add(staff)
        db.session.flush()
        _register("staff", staff.staff_id)
        nurse = NursingStaff(
            staff_id=staff.staff_id,
            nursing_license=f"NUR-{fake.unique.numerify(text='######')}",
            certifications=fake.sentence(nb_words=5),
        )
        db.session.add(nurse)
        db.session.flush()
        _register("nursing_staff", nurse.staff_id)
        nurses.append(nurse)

    for _index in range(4):
        staff = Staff(
            national_id=fake.unique.numerify(text="#########"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            birth_date=_random_birth_date(),
            phone=fake.phone_number(),
            ssn=fake.unique.numerify(text="#########"),
            email=_unique_email("staff"),
            address=fake.address(),
            staff_type="GENERAL",
        )
        db.session.add(staff)
        db.session.flush()
        _register("staff", staff.staff_id)
        general = GeneralStaff(staff_id=staff.staff_id, job_type=random.choice(["Reception", "Maintenance", "Cleaning", "Admin"]))
        db.session.add(general)
        db.session.flush()
        _register("general_staff", general.staff_id)
        general_staff_members.append(general)

    db.session.commit()
    return doctors, nurses, general_staff_members


def _create_patients():
    patients = []
    for _index in range(14):
        patient = Patient(
            national_id=fake.unique.numerify(text="#########"),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            birth_date=_random_birth_date(1, 90),
            gender=random.choice(["MALE", "FEMALE", "OTHER"]),
            phone=fake.phone_number(),
            email=_unique_email("patient"),
            address=fake.address(),
            emergency_contact_name=fake.name(),
            emergency_contact_phone=fake.phone_number(),
            blood_type=random.choice(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
            allergies=random.choice(["", "Penicillin", "Latex", "Dust"]),
        )
        db.session.add(patient)
        db.session.flush()
        _register("patients", patient.patient_id)
        patients.append(patient)
    db.session.commit()
    return patients


def generate_dummy_data():
    cleanup_dummy()

    specialties, floors, rooms, theaters, medications = _ensure_support_data()
    doctors, nurses, _general = _create_staff_batch(specialties)
    patients = _create_patients()

    visits = []
    for _index in range(16):
        visit_time = fake.date_time_between(start_date="-20d", end_date="+5d")
        visit = Visit(
            patient_id=random.choice(patients).patient_id,
            doctor_id=random.choice(doctors).staff_id,
            visit_timestamp=visit_time,
            diagnosis=fake.sentence(nb_words=6),
            notes=fake.text(max_nb_chars=80),
        )
        db.session.add(visit)
        db.session.flush()
        _register("visits", visit.visit_id)
        visits.append(visit)
    db.session.commit()

    for visit in visits[:10]:
        appointment = ScheduledAppointment(
            visit_id=visit.visit_id,
            appointment_date=(visit.visit_timestamp.date() + timedelta(days=random.randint(0, 3))),
            appointment_time=(datetime.min + timedelta(hours=random.randint(8, 17), minutes=random.choice([0, 15, 30, 45]))).time(),
            status=random.choice(["SCHEDULED", "COMPLETED", "CANCELLED", "NO_SHOW"]),
        )
        db.session.add(appointment)
        db.session.flush()
        _register("scheduled_appointments", appointment.appointment_id)
    db.session.commit()

    surgeries = []
    for _index in range(6):
        start_hour = random.randint(8, 15)
        surgery = Surgery(
            patient_id=random.choice(patients).patient_id,
            theater_id=random.choice(theaters).theater_id,
            primary_surgeon_id=random.choice(doctors).staff_id,
            surgery_date=(datetime.utcnow().date() + timedelta(days=random.randint(0, 5))),
            start_time=(datetime.min + timedelta(hours=start_hour)).time(),
            end_time=(datetime.min + timedelta(hours=start_hour + 2)).time(),
            procedure_type=random.choice(["Appendectomy", "Bypass", "Hip Replacement", "Knee Arthroscopy"]),
            notes=fake.sentence(nb_words=10),
        )
        db.session.add(surgery)
        db.session.flush()
        _register("surgeries", surgery.surgery_id)
        surgeries.append(surgery)
    db.session.commit()

    for surgery in surgeries:
        for nurse in random.sample(nurses, k=min(2, len(nurses))):
            assistant = SurgeryAssistant(surgery_id=surgery.surgery_id, nurse_id=nurse.staff_id, role=random.choice(["Scrub", "Circulating"]))
            db.session.add(assistant)
            db.session.flush()
            _register("surgery_assistants", surgery.surgery_id)
    db.session.commit()

    admissions = []
    for patient in patients[:6]:
        admission = Admission(
            patient_id=patient.patient_id,
            room_id=random.choice(rooms).room_id,
            admission_date=fake.date_time_between(start_date="-10d", end_date="now"),
            expected_discharge_date=(datetime.utcnow().date() + timedelta(days=random.randint(2, 10))),
        )
        db.session.add(admission)
        db.session.flush()
        _register("admissions", admission.admission_id)
        admissions.append(admission)
    db.session.commit()

    for visit in visits[:12]:
        prescription = Prescription(
            visit_id=visit.visit_id,
            medication_id=random.choice(medications).medication_id,
            dosage=random.choice(["250mg", "500mg", "1g"]),
            frequency=random.choice(["Every 8h", "Daily", "Twice a day"]),
            duration_days=random.randint(3, 14),
            start_date=datetime.utcnow().date(),
        )
        db.session.add(prescription)
        db.session.flush()
        _register("prescriptions", prescription.prescription_id)
    db.session.commit()

    for admission in admissions:
        dispensation = PharmacyDispensation(
            admission_id=admission.admission_id,
            dispensed_at=fake.date_time_between(start_date="-5d", end_date="now"),
            total_cost=round(random.uniform(20, 250), 2),
            notes=fake.sentence(nb_words=7),
        )
        db.session.add(dispensation)
        db.session.flush()
        _register("pharmacy_dispensations", dispensation.dispensation_id)

        item = DispensationItem(
            dispensation_id=dispensation.dispensation_id,
            medication_id=random.choice(medications).medication_id,
            quantity=random.randint(1, 4),
            unit_price=round(random.uniform(4, 35), 2),
        )
        db.session.add(item)
        db.session.flush()
        _register("dispensation_items", item.item_id)
    db.session.commit()

    for patient in patients[:8]:
        exam = RadiologyExam(
            patient_id=patient.patient_id,
            requesting_doctor_id=random.choice(doctors).staff_id,
            exam_type=random.choice(["X-Ray", "MRI", "CT", "Ultrasound"]),
            requested_at=fake.date_time_between(start_date="-7d", end_date="now"),
            performed_at=fake.date_time_between(start_date="-6d", end_date="now"),
            result_image_url=f"https://example.test/results/{fake.uuid4()}",
            radiologist_report=fake.text(max_nb_chars=140),
            status=random.choice(["REQUESTED", "SCHEDULED", "COMPLETED", "CANCELLED"]),
        )
        db.session.add(exam)
        db.session.flush()
        _register("radiology_exams", exam.exam_id)
    db.session.commit()


def cleanup_dummy():
    registry_rows = DummyRegistry.query.order_by(DummyRegistry.id.desc()).all()
    if not registry_rows:
        return

    grouped = {}
    for row in registry_rows:
        grouped.setdefault(row.table_name, set()).add(row.record_id)

    for surgery_id in grouped.get("surgery_assistants", set()):
        SurgeryAssistant.query.filter_by(surgery_id=surgery_id).delete()

    for item_id in grouped.get("dispensation_items", set()):
        DispensationItem.query.filter_by(item_id=item_id).delete()

    for dispensation_id in grouped.get("pharmacy_dispensations", set()):
        PharmacyDispensation.query.filter_by(dispensation_id=dispensation_id).delete()

    for prescription_id in grouped.get("prescriptions", set()):
        Prescription.query.filter_by(prescription_id=prescription_id).delete()

    for appointment_id in grouped.get("scheduled_appointments", set()):
        ScheduledAppointment.query.filter_by(appointment_id=appointment_id).delete()

    for exam_id in grouped.get("radiology_exams", set()):
        RadiologyExam.query.filter_by(exam_id=exam_id).delete()

    for surgery_id in grouped.get("surgeries", set()):
        Surgery.query.filter_by(surgery_id=surgery_id).delete()

    for visit_id in grouped.get("visits", set()):
        Visit.query.filter_by(visit_id=visit_id).delete()

    for admission_id in grouped.get("admissions", set()):
        Admission.query.filter_by(admission_id=admission_id).delete()

    for device_id in grouped.get("medical_devices", set()):
        MedicalDevice.query.filter_by(device_id=device_id).delete()

    for theater_id in grouped.get("operating_theaters", set()):
        OperatingTheater.query.filter_by(theater_id=theater_id).delete()

    for room_id in grouped.get("rooms", set()):
        Room.query.filter_by(room_id=room_id).delete()

    for staff_id in grouped.get("medical_staff", set()):
        MedicalStaff.query.filter_by(staff_id=staff_id).delete()

    for staff_id in grouped.get("nursing_staff", set()):
        NursingStaff.query.filter_by(staff_id=staff_id).delete()

    for staff_id in grouped.get("general_staff", set()):
        GeneralStaff.query.filter_by(staff_id=staff_id).delete()

    for patient_id in grouped.get("patients", set()):
        Patient.query.filter_by(patient_id=patient_id).delete()

    for staff_id in grouped.get("staff", set()):
        Staff.query.filter_by(staff_id=staff_id).delete()

    for medication_id in grouped.get("medications", set()):
        Medication.query.filter_by(medication_id=medication_id).delete()

    for specialty_id in grouped.get("medical_specialties", set()):
        MedicalSpecialty.query.filter_by(specialty_id=specialty_id).delete()

    for floor_id in grouped.get("floors", set()):
        Floor.query.filter_by(floor_id=floor_id).delete()

    DummyRegistry.query.delete()
    db.session.commit()
