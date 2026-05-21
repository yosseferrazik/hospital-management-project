# Maintenance Operations

## What you can do

From the **Maintenance** section in the desktop app:

### Required (mandatory for passing)

| Task | Endpoint | Description |
|------|----------|-------------|
| Register new staff | `POST /api/maintenance/staff` | Add doctors, nurses, general staff |
| Register new patients | `POST /api/maintenance/patients` | Add a new patient record |
| Assign nurse to doctor/floor | `PUT /api/maintenance/nurses/{id}` | Set `assigned_doctor_id` or `assigned_floor_id` |
| View surgeries by date | `GET /api/maintenance/surgeries?date=X` | List surgeries with patient, surgeon, assistants |
| View visits by date | `GET /api/maintenance/visits?date=X` | List visits with patient, doctor, time |

### Optional

| Task | Endpoint |
|------|----------|
| View room reservations | `GET /api/rooms/{id}/reservations` |
| View patient history | `GET /api/reports/patient-history/{id}` |
| View doctor schedule | `GET /api/reports/doctor-schedule/{id}` |

### Top (extra credit)

| Task | Endpoint |
|------|----------|
| View medical devices by operating theater | `GET /api/medical-devices?theater_id=X` |

## PL/pgSQL procedures

We created 5 functions/procedures in PostgreSQL:

1. **`check_surgery_overlap()`** — Trigger that prevents booking two surgeries in the same operating theater at the same time
2. **`validate_nurse_assignment()`** — Trigger that checks assigned doctor/floor actually exist
3. **`audit_trigger_function()`** — Generic audit logger for 8 sensitive tables
4. **`get_current_app_user_id()`** — Helper to retrieve the current user from session context
5. **`get_current_staff_id()`** — Helper to retrieve the current staff member
