# Maintenance Operations

## What you can do

From the **Maintenance** section in the desktop app (5-tab notebook: Doctor, Nursing, General Staff, Patient, Assignments):

| Task | Endpoint | Description |
|------|----------|-------------|
| Register medical staff | `POST /api/maintenance/staff/medical` | Add a doctor |
| Register nursing staff | `POST /api/maintenance/staff/nursing` | Add a nurse |
| Register general staff | `POST /api/maintenance/staff/general` | Add non-medical staff |
| Register new patients | `POST /api/maintenance/patients` | Add a new patient record |
| Assign nurse to doctor/floor | `PUT /api/maintenance/nursing/assign` | Body: `{nurse_id, doctor_id}` or `{nurse_id, floor_id}` |
| View surgeries by date | `GET /api/maintenance/surgeries?date=X` | List surgeries with patient, surgeon, assistants |
| View visits by date | `GET /api/maintenance/visits/scheduled?date=X` | List scheduled visits with patient, doctor, time |
| View medical devices by theater | `GET /api/medical-devices?theater_id=X` | Devices available in an operating theater |

## PL/pgSQL procedures

We created 5 functions/procedures in PostgreSQL:

1. **`check_surgery_overlap()`** — Trigger that prevents booking two surgeries in the same operating theater at the same time
2. **`validate_nurse_assignment()`** — Trigger that checks assigned doctor/floor actually exist
3. **`audit_trigger_function()`** — Generic audit logger for 8 sensitive tables
4. **`get_current_app_user_id()`** — Helper to retrieve the current user from session context
5. **`get_current_staff_id()`** — Helper to retrieve the current staff member
