# Test Data Generation

## Overview

We used the **Faker** library (Spanish locale `es_ES`) to generate realistic dummy data for testing performance and validating the application. The generator is in `server/src/app/services/dummy_service.py` and can be triggered from the desktop application's "Dummy Data" menu.

## Data volumes

Following the project requirements:

| Entity | Target count |
|--------|-------------|
| Patients | 50,000 |
| Visits | 100,000+ (2× patient count) |
| Doctors | 100 |
| Nurses | 200 |
| General staff | 50 |
| Administrators / reception | 50 |
| Surgeries | ~25,000 |
| Admissions | ~25,000 |
| Prescriptions | Linked to visits |

## How it works

1. **Support data** (specialties, medications, floors, rooms, operating theaters, medical devices) is seeded first
2. **Staff** is generated: doctors with specialties, nurses with assigned doctors or floors, general staff
3. **Patients** are generated with realistic Spanish names, addresses, phone numbers
4. **Visits** are distributed across the last 60 days (and a few in the future for scheduled appointments), with specialty-specific diagnoses
5. **Surgeries, admissions, prescriptions, pharmacy dispensations, radiology exams** are generated proportionally

## Cyrillic data

About 5% of patients and staff have names in Cyrillic alphabet (generated with Faker `ru_RU` locale) to meet the hospital's requirement for Eastern European patient support.

## Performance considerations

Generating 50,000 patients and 100,000+ visits was slow at first (took ~20 minutes). We optimised by:
- Using batch inserts with `flush()` every 20 records and `commit()` every 400
- Pre-computing diagnosis pools per specialty
- Using random sampling instead of sequential iteration where possible

## Cleanup

A `DummyRegistry` table tracks all generated records. The "Cleanup dummy data" option in the desktop app deletes everything in reverse dependency order and clears the registry.

## How to run

From the desktop app:
1. Log in as admin
2. Open **Dummy Data** from the sidebar
3. Enter patient count (max 50,000)
4. Click **Generate**
