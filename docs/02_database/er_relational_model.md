# ER / Relational Model

## Overview

The database has **24 tables** covering patients, medical staff, visits, surgeries, admissions, pharmacy, radiology, audit logging, and dummy data tracking. The schema is defined in `scripts/sql/schema.sql`.

## Key entities and relationships

```
STAFF ──┬── MEDICAL_STAFF ──┬── MEDICAL_STAFF_SPECIALTIES
        │                   └── MEDICAL_SPECIALTIES
        ├── NURSING_STAFF ──┬── FLOORS (assigned_floor)
        │                   └── MEDICAL_STAFF (assigned_doctor)
        └── GENERAL_STAFF

PATIENTS ──┬── VISITS ──┬── PRESCRIPTIONS ── MEDICATIONS
           │            └── SCHEDULED_APPOINTMENTS
           ├── ADMISSIONS ──┬── ROOMS ── FLOORS
           │                └── PHARMACY_DISPENSATIONS ── DISPENSATION_ITEMS
           ├── SURGERIES ──┬── OPERATING_THEATERS ── MEDICAL_DEVICES
           │               └── SURGERY_ASSISTANTS
           └── RADIOLOGY_EXAMS

DUMMY_REGISTRY (tracks generated test data for cleanup)

APP_USERS ──── STAFF (login mapping)

AUDIT_LOGS (generic audit trail for 8 sensitive tables)
```

## Naming conventions

- Tables: uppercase snake case (`PATIENTS`, `MEDICAL_STAFF_SPECIALTIES`)
- Columns: lowercase snake case (`patient_id`, `created_at`)
- PK: `<entity>_id`
- FK: same name as referenced PK
- Indexes: `idx_<table>_<column>`
- Unique constraints: `uq_<description>`
- Check constraints: `chk_<description>`

## Design patterns used

| Pattern | Example |
|---------|---------|
| Base + subtype | `STAFF` → `MEDICAL_STAFF`, `NURSING_STAFF`, `GENERAL_STAFF` |
| Junction table | `MEDICAL_STAFF_SPECIALTIES`, `SURGERY_ASSISTANTS` |
| Audit table | `AUDIT_LOGS` with before/after row data |
| Reference tables | `MEDICAL_SPECIALTIES`, `MEDICATIONS`, `FLOORS` |
| Header-detail | `PHARMACY_DISPENSATIONS` → `DISPENSATION_ITEMS` |

## Data dictionary (main columns)

### PATIENTS
| Column | Type | Notes |
|--------|------|-------|
| patient_id | SERIAL PK | |
| national_id | VARCHAR(50) | UNIQUE, DNI/NIE |
| first_name, last_name | VARCHAR(100) | Supports Cyrillic (UTF-8) |
| birth_date | DATE | |
| gender | VARCHAR(10) | CHECK 'MALE'/'FEMALE'/'OTHER' |
| phone, email, address | VARCHAR | Contact info |
| emergency_contact_name | VARCHAR(200) | |
| emergency_contact_phone | VARCHAR(20) | |
| blood_type | VARCHAR(5) | A+, A-, B+, B-, O+, O-, AB+, AB- |
| allergies | TEXT | Free text |
| health_card | VARCHAR(50) | UNIQUE |

### STAFF
| Column | Type | Notes |
|--------|------|-------|
| staff_id | SERIAL PK | |
| national_id | VARCHAR(50) | UNIQUE |
| first_name, last_name | VARCHAR(100) | |
| staff_type | VARCHAR(50) | 'MEDICAL', 'NURSING', 'GENERAL' |
| birth_date | DATE | |
| phone, ssn, email, address | VARCHAR | |
| curriculum / license | TEXT | Only for MEDICAL subtype |

### VISITS
| Column | Type | Notes |
|--------|------|-------|
| visit_id | SERIAL PK | |
| patient_id | FK → PATIENTS | |
| doctor_id | FK → MEDICAL_STAFF | |
| visit_timestamp | TIMESTAMP | |
| diagnosis | TEXT | |
| notes | TEXT | |

## Indexes

85+ indexes on all foreign keys and frequently filtered columns (FKs, status, dates, timestamps). See `schema.sql` for the full list.

## What we learned

Getting the subtype relationship right (STAFF → MEDICAL_STAFF / NURSING_STAFF / GENERAL_STAFF) was harder than expected. We used a shared PK strategy where `medical_staff.staff_id` is both PK and FK to `staff.staff_id`, which keeps queries simple.
