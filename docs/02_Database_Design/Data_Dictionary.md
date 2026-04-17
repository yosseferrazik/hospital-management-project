# 📊 Data Dictionary
> This document provides a comprehensive description of all tables, columns, data types, constraints, and relationships within the Hospital Management database schema.

## Table of Contents
1. [FLOORS](#floors)
2. [ROOMS](#rooms)
3. [OPERATING_THEATERS](#operating_theaters)
4. [MEDICAL_DEVICES](#medical_devices)
5. [MEDICAL_SPECIALTIES](#medical_specialties)
6. [STAFF](#staff)
7. [MEDICAL_STAFF](#medical_staff)
8. [NURSING_STAFF](#nursing_staff)
9. [GENERAL_STAFF](#general_staff)
10. [MEDICAL_STAFF_SPECIALTIES](#medical_staff_specialties)
11. [PATIENTS](#patients)
12. [VISITS](#visits)
13. [SCHEDULED_APPOINTMENTS](#scheduled_appointments)
14. [MEDICATIONS](#medications)
15. [PRESCRIPTIONS](#prescriptions)
16. [ADMISSIONS](#admissions)
17. [SURGERIES](#surgeries)
18. [SURGERY_ASSISTANTS](#surgery_assistants)
19. [PHARMACY_DISPENSATIONS](#pharmacy_dispensations)
20. [DISPENSATION_ITEMS](#dispensation_items)
21. [RADIOLOGY_EXAMS](#radiology_exams)
22. [APP_USERS](#app_users)
23. [AUDIT_LOGS](#audit_logs)

---

## FLOORS
**Description:** Building floor information. Contains the physical floors within the hospital facility.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| floor_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each floor |
| floor_number | INTEGER | NOT NULL, UNIQUE | - | Floor number designation (e.g., 1, 2, 3) |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_floors_floor_number | floor_number | BTREE | Optimizes lookups by floor number |

**Referenced By:**
- `ROOMS(floor_id)` - ON DELETE RESTRICT
- `OPERATING_THEATERS(floor_id)` - ON DELETE RESTRICT
- `NURSING_STAFF(assigned_floor_id)` - ON DELETE SET NULL

---

## ROOMS
**Description:** Patient rooms located on floors. Each room belongs to a specific floor.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| room_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each room |
| room_number | VARCHAR(20) | NOT NULL | - | Room number or code designation |
| floor_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to the floor where room is located |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| floor_id | FLOORS(floor_id) | RESTRICT |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_rooms_floor_id | floor_id | BTREE | Optimizes joins with FLOORS table |
| idx_rooms_room_number | room_number | BTREE | Optimizes room number searches |

**Referenced By:**
- `ADMISSIONS(room_id)` - ON DELETE RESTRICT

---

## OPERATING_THEATERS
**Description:** Surgical operation theaters. Dedicated rooms for performing surgical procedures.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| theater_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each operating theater |
| theater_code | VARCHAR(20) | NOT NULL, UNIQUE | - | Unique code identifying the theater (e.g., "OR-01") |
| floor_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to the floor where theater is located |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| floor_id | FLOORS(floor_id) | RESTRICT |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_op_theaters_floor_id | floor_id | BTREE | Optimizes joins with FLOORS table |
| idx_op_theaters_code | theater_code | BTREE | Optimizes theater code lookups |

**Referenced By:**
- `MEDICAL_DEVICES(theater_id)` - ON DELETE CASCADE
- `SURGERIES(theater_id)` - ON DELETE RESTRICT

---

## MEDICAL_DEVICES
**Description:** Medical devices assigned to operating theaters. Tracks equipment inventory within surgical suites.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| device_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each medical device |
| device_type | VARCHAR(100) | NOT NULL | - | Type/category of medical device |
| theater_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to the operating theater housing device |
| quantity | INTEGER | NOT NULL, CHECK (quantity > 0) | 1 | Number of units of this device type in theater |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| theater_id | OPERATING_THEATERS(theater_id) | CASCADE |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_medical_devices_theater_id | theater_id | BTREE | Optimizes joins with OPERATING_THEATERS table |
| idx_medical_devices_type | device_type | BTREE | Optimizes device type searches |

---

## MEDICAL_SPECIALTIES
**Description:** Medical specialties definitions. Master catalog of all medical specialties recognized in the system.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| specialty_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each medical specialty |
| name | VARCHAR(100) | NOT NULL, UNIQUE | - | Name of the medical specialty (e.g., "Cardiology") |
| description | TEXT | - | NULL | Detailed description of the specialty |

**Referenced By:**
- `MEDICAL_STAFF(specialty_id)` - ON DELETE RESTRICT
- `MEDICAL_STAFF_SPECIALTIES(specialty_id)` - ON DELETE CASCADE

---

## STAFF
**Description:** Base table for all hospital staff. Contains core personal and employment information applicable to all staff types.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| staff_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each staff member |
| national_id | VARCHAR(50) | NOT NULL, UNIQUE | - | Government-issued national identification number |
| first_name | VARCHAR(100) | NOT NULL | - | Staff member's first/given name |
| last_name | VARCHAR(100) | NOT NULL | - | Staff member's last/family name |
| birth_date | DATE | NOT NULL | - | Date of birth |
| phone | VARCHAR(20) | - | NULL | Contact phone number |
| ssn | VARCHAR(20) | UNIQUE | NULL | Social Security Number (region-specific) |
| email | VARCHAR(255) | UNIQUE | NULL | Professional email address |
| address | TEXT | - | NULL | Residential or mailing address |
| hire_date | DATE | NOT NULL | CURRENT_DATE | Date when staff member was hired |
| staff_type | VARCHAR(50) | NOT NULL, CHECK (staff_type IN ('MEDICAL', 'NURSING', 'GENERAL')) | - | Category of staff (determines subtype table) |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_staff_national_id | national_id | BTREE | Optimizes national ID lookups |
| idx_staff_last_name | last_name | BTREE | Optimizes name-based searches |
| idx_staff_email | email | BTREE | Optimizes email lookups |
| idx_staff_hire_date | hire_date | BTREE | Optimizes hire date filtering |
| idx_staff_staff_type | staff_type | BTREE | Optimizes staff type filtering |

**Referenced By:**
- `MEDICAL_STAFF(staff_id)` - ON DELETE CASCADE
- `NURSING_STAFF(staff_id)` - ON DELETE CASCADE
- `GENERAL_STAFF(staff_id)` - ON DELETE CASCADE
- `MEDICAL_STAFF_SPECIALTIES(staff_id)` - ON DELETE CASCADE
- `APP_USERS(staff_id)` - ON DELETE CASCADE

---

## MEDICAL_STAFF
**Description:** Medical staff (doctors, surgeons) extending STAFF. Contains information specific to licensed medical practitioners.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| staff_id | INTEGER | PRIMARY KEY, FOREIGN KEY | - | Reference to base STAFF record |
| specialty_id | INTEGER | NOT NULL, FOREIGN KEY | - | Primary medical specialty |
| license_number | VARCHAR(50) | NOT NULL, UNIQUE | - | Professional medical license number |
| curriculum | TEXT | - | NULL | Curriculum vitae / professional background |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| staff_id | STAFF(staff_id) | CASCADE |
| specialty_id | MEDICAL_SPECIALTIES(specialty_id) | RESTRICT |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_medical_staff_specialty | specialty_id | BTREE | Optimizes joins with MEDICAL_SPECIALTIES |
| idx_medical_staff_license | license_number | BTREE | Optimizes license number lookups |

**Referenced By:**
- `NURSING_STAFF(assigned_doctor_id)` - ON DELETE SET NULL
- `VISITS(doctor_id)` - ON DELETE RESTRICT
- `SURGERIES(primary_surgeon_id)` - ON DELETE RESTRICT
- `RADIOLOGY_EXAMS(requesting_doctor_id)` - ON DELETE RESTRICT

---

## NURSING_STAFF
**Description:** Nursing staff extending STAFF. Contains information specific to licensed nursing professionals.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| staff_id | INTEGER | PRIMARY KEY, FOREIGN KEY | - | Reference to base STAFF record |
| nursing_license | VARCHAR(50) | NOT NULL, UNIQUE | - | Professional nursing license number |
| assigned_doctor_id | INTEGER | FOREIGN KEY | NULL | Supervising physician assignment |
| assigned_floor_id | INTEGER | FOREIGN KEY | NULL | Primary floor assignment |
| certifications | TEXT | - | NULL | Additional nursing certifications held |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| staff_id | STAFF(staff_id) | CASCADE |
| assigned_doctor_id | MEDICAL_STAFF(staff_id) | SET NULL |
| assigned_floor_id | FLOORS(floor_id) | SET NULL |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_nursing_staff_assigned_doctor | assigned_doctor_id | BTREE | Optimizes doctor-nurse relationship queries |
| idx_nursing_staff_assigned_floor | assigned_floor_id | BTREE | Optimizes floor assignment queries |
| idx_nursing_staff_license | nursing_license | BTREE | Optimizes license number lookups |

**Referenced By:**
- `SURGERY_ASSISTANTS(nurse_id)` - ON DELETE RESTRICT

---

## GENERAL_STAFF
**Description:** General staff (administrative, support) extending STAFF. Contains information specific to non-clinical hospital personnel.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| staff_id | INTEGER | PRIMARY KEY, FOREIGN KEY | - | Reference to base STAFF record |
| job_type | VARCHAR(100) | NOT NULL | - | Specific job classification (e.g., "Administrative Assistant") |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| staff_id | STAFF(staff_id) | CASCADE |

---

## MEDICAL_STAFF_SPECIALTIES
**Description:** Junction table for many-to-many relationship between medical staff and specialties. Allows doctors to have multiple specialties.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| medical_staff_specialty_id | SERIAL | PRIMARY KEY | Auto-increment | Surrogate primary key |
| staff_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to medical staff member |
| specialty_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to medical specialty |

**Constraints:**
| Constraint Name | Type | Column(s) | Description |
|:---|:---|:---|:---|
| medical_staff_specialties_staff_id_specialty_id_key | UNIQUE | (staff_id, specialty_id) | Prevents duplicate specialty assignments |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| staff_id | STAFF(staff_id) | CASCADE |
| specialty_id | MEDICAL_SPECIALTIES(specialty_id) | CASCADE |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_staff_specialties_staff_id | staff_id | BTREE | Optimizes staff-based lookups |
| idx_staff_specialties_specialty_id | specialty_id | BTREE | Optimizes specialty-based lookups |

---

## PATIENTS
**Description:** Patient information. Contains demographic, contact, and medical history data for all patients.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| patient_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each patient |
| national_id | VARCHAR(50) | NOT NULL, UNIQUE | - | Government-issued national identification number |
| first_name | VARCHAR(100) | NOT NULL | - | Patient's first/given name |
| last_name | VARCHAR(100) | NOT NULL | - | Patient's last/family name |
| birth_date | DATE | NOT NULL | - | Date of birth |
| gender | VARCHAR(10) | CHECK (gender IN ('MALE', 'FEMALE', 'OTHER')) | NULL | Patient's gender identity |
| phone | VARCHAR(20) | - | NULL | Primary contact phone number |
| email | VARCHAR(255) | - | NULL | Email address |
| address | TEXT | - | NULL | Residential address |
| emergency_contact_name | VARCHAR(200) | - | NULL | Name of emergency contact person |
| emergency_contact_phone | VARCHAR(20) | - | NULL | Phone number for emergency contact |
| blood_type | VARCHAR(5) | CHECK (blood_type IN ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')) | NULL | Patient's blood type |
| allergies | TEXT | - | NULL | Known allergies (medications, substances) |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_patients_national_id | national_id | BTREE | Optimizes national ID lookups |
| idx_patients_last_name | last_name | BTREE | Optimizes name-based searches |
| idx_patients_birth_date | birth_date | BTREE | Optimizes age-based filtering |
| idx_patients_blood_type | blood_type | BTREE | Optimizes blood type queries |

**Referenced By:**
- `VISITS(patient_id)` - ON DELETE CASCADE
- `ADMISSIONS(patient_id)` - ON DELETE CASCADE
- `SURGERIES(patient_id)` - ON DELETE CASCADE
- `RADIOLOGY_EXAMS(patient_id)` - ON DELETE CASCADE

---

## VISITS
**Description:** Patient visits and consultations. Records outpatient consultations and clinical encounters.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| visit_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each visit |
| patient_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to patient being seen |
| doctor_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to attending physician |
| visit_timestamp | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | Date and time when visit occurred |
| diagnosis | TEXT | - | NULL | Clinical diagnosis determined during visit |
| notes | TEXT | - | NULL | Additional clinical notes and observations |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| patient_id | PATIENTS(patient_id) | CASCADE |
| doctor_id | MEDICAL_STAFF(staff_id) | RESTRICT |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_visits_patient_id | patient_id | BTREE | Optimizes patient history queries |
| idx_visits_doctor_id | doctor_id | BTREE | Optimizes doctor workload queries |
| idx_visits_timestamp | visit_timestamp | BTREE | Optimizes date-based filtering |

**Referenced By:**
- `SCHEDULED_APPOINTMENTS(visit_id)` - ON DELETE CASCADE
- `PRESCRIPTIONS(visit_id)` - ON DELETE CASCADE

---

## SCHEDULED_APPOINTMENTS
**Description:** Scheduled appointments for visits. Manages future appointment scheduling and status tracking.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| appointment_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each appointment |
| visit_id | INTEGER | NOT NULL, UNIQUE, FOREIGN KEY | - | Reference to associated visit record |
| appointment_date | DATE | NOT NULL | - | Scheduled date of appointment |
| appointment_time | TIME | NOT NULL | - | Scheduled time of appointment |
| status | VARCHAR(50) | NOT NULL, CHECK (status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED', 'NO_SHOW')) | 'SCHEDULED' | Current status of appointment |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| visit_id | VISITS(visit_id) | CASCADE |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_appointments_visit_id | visit_id | BTREE | Optimizes joins with VISITS table |
| idx_appointments_date | appointment_date | BTREE | Optimizes date-based scheduling |
| idx_appointments_status | status | BTREE | Optimizes status filtering |

---

## MEDICATIONS
**Description:** Medication catalog. Master list of all medications available in the hospital pharmacy.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| medication_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each medication |
| medication_name | VARCHAR(200) | NOT NULL, UNIQUE | - | Name of medication (brand or generic) |
| description | TEXT | - | NULL | Description, indications, and notes |

**Referenced By:**
- `PRESCRIPTIONS(medication_id)` - ON DELETE RESTRICT
- `DISPENSATION_ITEMS(medication_id)` - ON DELETE RESTRICT

---

## PRESCRIPTIONS
**Description:** Prescriptions issued during visits. Links medications to specific patient visits with dosing instructions.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| prescription_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each prescription |
| visit_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to visit when prescribed |
| medication_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to prescribed medication |
| dosage | VARCHAR(100) | NOT NULL | - | Dosage amount (e.g., "500mg") |
| frequency | VARCHAR(100) | NOT NULL | - | Dosing frequency (e.g., "Twice daily") |
| duration_days | INTEGER | - | NULL | Number of days medication should be taken |
| start_date | DATE | NOT NULL | CURRENT_DATE | Date when prescription begins |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| visit_id | VISITS(visit_id) | CASCADE |
| medication_id | MEDICATIONS(medication_id) | RESTRICT |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_prescriptions_visit_id | visit_id | BTREE | Optimizes prescription history queries |
| idx_prescriptions_medication_id | medication_id | BTREE | Optimizes medication usage queries |
| idx_prescriptions_start_date | start_date | BTREE | Optimizes date-based filtering |

---

## ADMISSIONS
**Description:** Patient hospital admissions. Records inpatient stays and room assignments.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| admission_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each admission |
| patient_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to admitted patient |
| room_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to assigned room |
| admission_date | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | Date and time of admission |
| expected_discharge_date | DATE | - | NULL | Anticipated discharge date |
| actual_discharge_date | DATE | - | NULL | Actual discharge date (when patient left) |

**Constraints:**
| Constraint Name | Type | Column(s) | Description |
|:---|:---|:---|:---|
| admissions_check | CHECK | actual_discharge_date >= DATE(admission_date) OR actual_discharge_date IS NULL | Ensures discharge date is after admission |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| patient_id | PATIENTS(patient_id) | CASCADE |
| room_id | ROOMS(room_id) | RESTRICT |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_admissions_patient_id | patient_id | BTREE | Optimizes patient admission history |
| idx_admissions_room_id | room_id | BTREE | Optimizes room occupancy queries |
| idx_admissions_admission_date | admission_date | BTREE | Optimizes admission date filtering |
| idx_admissions_discharge_date | actual_discharge_date | BTREE | Optimizes discharge queries |

**Referenced By:**
- `PHARMACY_DISPENSATIONS(admission_id)` - ON DELETE CASCADE

---

## SURGERIES
**Description:** Surgical procedures. Records all surgical operations performed in the hospital.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| surgery_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each surgery |
| patient_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to patient undergoing surgery |
| theater_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to operating theater used |
| primary_surgeon_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to lead surgeon |
| surgery_date | DATE | NOT NULL | - | Date when surgery occurred |
| start_time | TIME | NOT NULL | - | Time when surgery began |
| end_time | TIME | NOT NULL | - | Time when surgery concluded |
| procedure_type | VARCHAR(200) | NOT NULL | - | Type/name of surgical procedure |
| notes | TEXT | - | NULL | Surgical notes and observations |

**Constraints:**
| Constraint Name | Type | Column(s) | Description |
|:---|:---|:---|:---|
| surgeries_check | CHECK | end_time > start_time | Ensures end time is after start time |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| patient_id | PATIENTS(patient_id) | CASCADE |
| theater_id | OPERATING_THEATERS(theater_id) | RESTRICT |
| primary_surgeon_id | MEDICAL_STAFF(staff_id) | RESTRICT |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_surgeries_patient_id | patient_id | BTREE | Optimizes patient surgical history |
| idx_surgeries_theater_id | theater_id | BTREE | Optimizes theater scheduling |
| idx_surgeries_surgeon_id | primary_surgeon_id | BTREE | Optimizes surgeon workload queries |
| idx_surgeries_date | surgery_date | BTREE | Optimizes date-based filtering |

**Referenced By:**
- `SURGERY_ASSISTANTS(surgery_id)` - ON DELETE CASCADE

---

## SURGERY_ASSISTANTS
**Description:** Nursing staff assisting in surgeries. Junction table linking surgeries to assisting nursing personnel.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| surgery_id | INTEGER | PRIMARY KEY, FOREIGN KEY | - | Reference to surgery |
| nurse_id | INTEGER | PRIMARY KEY, FOREIGN KEY | - | Reference to assisting nurse |
| role | VARCHAR(100) | NOT NULL | - | Role performed during surgery (e.g., "Scrub Nurse") |

**Primary Key:** Composite key on `(surgery_id, nurse_id)`

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| surgery_id | SURGERIES(surgery_id) | CASCADE |
| nurse_id | NURSING_STAFF(staff_id) | RESTRICT |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_surgery_assistants_nurse_id | nurse_id | BTREE | Optimizes nurse assignment queries |

---

## PHARMACY_DISPENSATIONS
**Description:** Pharmacy dispensations during admissions. Header records for medications dispensed during inpatient stays.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| dispensation_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each dispensation |
| admission_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to patient admission |
| dispensed_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | Date and time of dispensation |
| total_cost | DECIMAL(10, 2) | NOT NULL, CHECK (total_cost >= 0) | 0 | Total cost of all items dispensed |
| notes | TEXT | - | NULL | Additional notes regarding dispensation |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| admission_id | ADMISSIONS(admission_id) | CASCADE |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_dispensations_admission_id | admission_id | BTREE | Optimizes admission-based queries |
| idx_dispensations_dispensed_at | dispensed_at | BTREE | Optimizes date-based filtering |

**Referenced By:**
- `DISPENSATION_ITEMS(dispensation_id)` - ON DELETE CASCADE

---

## DISPENSATION_ITEMS
**Description:** Individual items in pharmacy dispensations. Line items for medications dispensed in a single transaction.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| item_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each dispensation item |
| dispensation_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to parent dispensation |
| medication_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to dispensed medication |
| quantity | INTEGER | NOT NULL, CHECK (quantity > 0) | - | Number of units dispensed |
| unit_price | DECIMAL(10, 2) | NOT NULL, CHECK (unit_price >= 0) | - | Price per unit at time of dispensation |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| dispensation_id | PHARMACY_DISPENSATIONS(dispensation_id) | CASCADE |
| medication_id | MEDICATIONS(medication_id) | RESTRICT |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_dispensation_items_dispensation_id | dispensation_id | BTREE | Optimizes line item lookups |
| idx_dispensation_items_medication_id | medication_id | BTREE | Optimizes medication usage queries |

---

## RADIOLOGY_EXAMS
**Description:** Radiology examination records. Tracks imaging studies ordered and performed.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| exam_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each radiology exam |
| patient_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to patient undergoing exam |
| requesting_doctor_id | INTEGER | NOT NULL, FOREIGN KEY | - | Reference to physician who ordered exam |
| exam_type | VARCHAR(100) | NOT NULL | - | Type of radiology exam (e.g., "X-Ray", "MRI") |
| requested_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | Date and time when exam was ordered |
| performed_at | TIMESTAMP | - | NULL | Date and time when exam was completed |
| result_image_url | TEXT | - | NULL | URL/path to stored image files |
| radiologist_report | TEXT | - | NULL | Radiologist's interpretation and findings |
| status | VARCHAR(50) | NOT NULL, CHECK (status IN ('REQUESTED', 'SCHEDULED', 'COMPLETED', 'CANCELLED')) | 'REQUESTED' | Current status of examination |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| patient_id | PATIENTS(patient_id) | CASCADE |
| requesting_doctor_id | MEDICAL_STAFF(staff_id) | RESTRICT |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_radiology_patient_id | patient_id | BTREE | Optimizes patient exam history |
| idx_radiology_doctor_id | requesting_doctor_id | BTREE | Optimizes ordering physician queries |
| idx_radiology_status | status | BTREE | Optimizes status filtering |
| idx_radiology_requested_at | requested_at | BTREE | Optimizes date-based filtering |

---

## APP_USERS
**Description:** Application user accounts linked to staff. Manages authentication and authorization for system access.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| user_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each user account |
| username | VARCHAR(100) | NOT NULL, UNIQUE | - | Login username |
| password_hash | VARCHAR(255) | NOT NULL | - | Hashed password for authentication |
| staff_id | INTEGER | NOT NULL, UNIQUE, FOREIGN KEY | - | Reference to associated staff member |
| role | VARCHAR(50) | NOT NULL, CHECK (role IN ('ADMIN', 'DOCTOR', 'NURSE', 'STAFF', 'RECEPTIONIST')) | - | System role determining permissions |
| is_active | BOOLEAN | NOT NULL | TRUE | Whether account is currently active |
| last_login | TIMESTAMP | - | NULL | Timestamp of most recent login |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | When user account was created |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| staff_id | STAFF(staff_id) | CASCADE |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_app_users_username | username | BTREE | Optimizes login lookups |
| idx_app_users_staff_id | staff_id | BTREE | Optimizes staff-user mapping |
| idx_app_users_role | role | BTREE | Optimizes role-based filtering |
| idx_app_users_active | is_active | BTREE | Optimizes active user queries |

**Referenced By:**
- `AUDIT_LOGS(user_id)` - ON DELETE SET NULL

---

## AUDIT_LOGS
**Description:** System audit trail. Tracks all significant actions performed within the system for security and compliance.

| Column Name | Data Type | Constraints | Default | Description |
|:---|:---|:---|:---|:---|
| log_id | SERIAL | PRIMARY KEY | Auto-increment | Unique identifier for each audit entry |
| user_id | INTEGER | FOREIGN KEY | NULL | Reference to user who performed action |
| action_timestamp | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | When action occurred |
| action_type | VARCHAR(50) | NOT NULL, CHECK (action_type IN ('INSERT', 'UPDATE', 'DELETE', 'SELECT', 'LOGIN', 'LOGOUT')) | - | Type of action performed |
| table_name | VARCHAR(100) | - | NULL | Database table affected (if applicable) |
| record_id | INTEGER | - | NULL | ID of record affected (if applicable) |
| old_data | TEXT | - | NULL | JSON representation of data before change |
| new_data | TEXT | - | NULL | JSON representation of data after change |
| ip_address | INET | - | NULL | IP address of client connection |
| notes | TEXT | - | NULL | Additional audit information |

**Foreign Keys:**
| Column | References | On Delete |
|:---|:---|:---|
| user_id | APP_USERS(user_id) | SET NULL |

**Indexes:**
| Index Name | Column(s) | Type | Description |
|:---|:---|:---|:---|
| idx_audit_logs_user_id | user_id | BTREE | Optimizes user activity queries |
| idx_audit_logs_timestamp | action_timestamp | BTREE | Optimizes time-based auditing |
| idx_audit_logs_action_type | action_type | BTREE | Optimizes action type filtering |
| idx_audit_logs_table_name | table_name | BTREE | Optimizes table-specific auditing |

---

## Relationship Summary

### Core Entity Relationships
| Parent Table | Child Table | Relationship Type | On Delete |
|:---|:---|:---|:---|
| FLOORS | ROOMS | One-to-Many | RESTRICT |
| FLOORS | OPERATING_THEATERS | One-to-Many | RESTRICT |
| FLOORS | NURSING_STAFF | One-to-Many | SET NULL |
| OPERATING_THEATERS | MEDICAL_DEVICES | One-to-Many | CASCADE |
| OPERATING_THEATERS | SURGERIES | One-to-Many | RESTRICT |
| STAFF | MEDICAL_STAFF | One-to-One | CASCADE |
| STAFF | NURSING_STAFF | One-to-One | CASCADE |
| STAFF | GENERAL_STAFF | One-to-One | CASCADE |
| STAFF | APP_USERS | One-to-One | CASCADE |
| MEDICAL_SPECIALTIES | MEDICAL_STAFF | One-to-Many | RESTRICT |
| MEDICAL_STAFF | NURSING_STAFF | One-to-Many | SET NULL |
| MEDICAL_STAFF | VISITS | One-to-Many | RESTRICT |
| MEDICAL_STAFF | SURGERIES | One-to-Many | RESTRICT |
| MEDICAL_STAFF | RADIOLOGY_EXAMS | One-to-Many | RESTRICT |
| PATIENTS | VISITS | One-to-Many | CASCADE |
| PATIENTS | ADMISSIONS | One-to-Many | CASCADE |
| PATIENTS | SURGERIES | One-to-Many | CASCADE |
| PATIENTS | RADIOLOGY_EXAMS | One-to-Many | CASCADE |
| VISITS | SCHEDULED_APPOINTMENTS | One-to-One | CASCADE |
| VISITS | PRESCRIPTIONS | One-to-Many | CASCADE |
| ROOMS | ADMISSIONS | One-to-Many | RESTRICT |
| ADMISSIONS | PHARMACY_DISPENSATIONS | One-to-Many | CASCADE |
| MEDICATIONS | PRESCRIPTIONS | One-to-Many | RESTRICT |
| MEDICATIONS | DISPENSATION_ITEMS | One-to-Many | RESTRICT |
| PHARMACY_DISPENSATIONS | DISPENSATION_ITEMS | One-to-Many | CASCADE |
| SURGERIES | SURGERY_ASSISTANTS | One-to-Many | CASCADE |
| NURSING_STAFF | SURGERY_ASSISTANTS | One-to-Many | RESTRICT |
| APP_USERS | AUDIT_LOGS | One-to-Many | SET NULL |

### Many-to-Many Relationships
| Table A | Table B | Junction Table |
|:---|:---|:---|
| STAFF (via MEDICAL_STAFF) | MEDICAL_SPECIALTIES | MEDICAL_STAFF_SPECIALTIES |
| SURGERIES | NURSING_STAFF | SURGERY_ASSISTANTS |

---

*Document Version: 1.0*
*Last Updated: April 14, 2026*
*Database: Hospital Management System - PostgreSQL*