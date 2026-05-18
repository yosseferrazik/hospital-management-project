from app.models import Admission
from app.services.base import parse_date, create_record, get_all, get_by_id, update_record, delete_record


def create_admission(data):
    return create_record(Admission,
        patient_id=data["patient_id"],
        room_id=data["room_id"],
        admission_date=parse_date(data.get("admission_date"), "%Y-%m-%d %H:%M:%S"),
        expected_discharge_date=parse_date(data.get("expected_discharge_date"), "%Y-%m-%d"),
        actual_discharge_date=parse_date(data.get("actual_discharge_date"), "%Y-%m-%d"),
    )


def get_admissions():
    return get_all(Admission)


def get_admission(admission_id):
    return get_by_id(Admission, admission_id)


def update_admission(admission_id, data):
    admission = get_by_id(Admission, admission_id)
    return update_record(admission,
        patient_id=data["patient_id"],
        room_id=data["room_id"],
        admission_date=parse_date(data.get("admission_date"), "%Y-%m-%d %H:%M:%S"),
        expected_discharge_date=parse_date(data.get("expected_discharge_date"), "%Y-%m-%d"),
        actual_discharge_date=parse_date(data.get("actual_discharge_date"), "%Y-%m-%d"),
    )


def delete_admission(admission_id):
    admission = get_by_id(Admission, admission_id)
    return delete_record(admission)
