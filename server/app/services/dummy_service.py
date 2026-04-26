from faker import Faker
import random
from app.models import (
    db,
    Patient,
    Staff,
    MedicalStaff,
    NursingStaff,
    GeneralStaff,
    Visit,
    Surgery,
    ScheduledAppointment,
    DummyRegistry,
    MedicalSpecialty,
    Floor,
    OperatingTheater,
)
from datetime import datetime, timedelta

fake = Faker()


def generate_dummy_data():
    # Register dummy IDs so they can be cleaned up later
    # 100 doctors, 200 nurses, 100 cleaning staff, 50 admin staff, 50k patients, 100k visits
    # For simplicity, keep this as a smaller but scalable implementation
    # Clean up existing dummy data first?
    pass


def cleanup_dummy():
    # Remove records tracked in dummy_registry
    pass
