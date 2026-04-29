# 📄Relational Model
> This document details the relational model for our hospital management system, outlining the tables, their attributes, and the relationships between them. The design is based on the ER diagram and follows normalization principles to ensure data integrity and efficiency.

## Tables
### FLOORS
- `floor_id` (PK)
- `floor_number`

### ROOMS
- `room_id` (PK)
- `room_number`
- `floor_id`
  - `ON floor_id REFERENCES FLOORS(floor_id)`

### OPERATING_THEATERS
- `theater_id` (PK)
- `theater_code`
- `floor_id`
  - `ON floor_id REFERENCES FLOORS(floor_id)`

### MEDICAL_DEVICES
- `device_id` (PK)
- `device_type`
- `theater_id`
- `quantity`
  - `ON theater_id REFERENCES OPERATING_THEATERS(theater_id)`

### MEDICAL_SPECIALTIES
- `specialty_id` (PK)
- `name`
- `description`

### MEDICAL_STAFF_SPECIALTIES
- `medical_staff_specialty_id` (PK)
- `staff_id`
- `specialty_id`
  - `ON staff_id REFERENCES STAFF(staff_id)`
  - `ON specialty_id REFERENCES MEDICAL_SPECIALTIES(specialty_id)`

### STAFF
- `staff_id` (PK)
- `national_id`
- `first_name`
- `last_name`
- `birth_date`
- `phone`
- `ssn`
- `email`
- `address`
- `hire_date`
- `staff_type`

### MEDICAL_STAFF
- `staff_id` (PK)
- `specialty_id`
- `license_number`
- `curriculum`
  - `ON staff_id REFERENCES STAFF(staff_id)`
  - `ON specialty_id REFERENCES MEDICAL_SPECIALTIES(specialty_id)`

### NURSING_STAFF
- `staff_id` (PK)
- `nursing_license`
- `assigned_doctor_id`
- `assigned_floor_id`
- `certifications`
  - `ON staff_id REFERENCES STAFF(staff_id)`
  - `ON assigned_doctor_id REFERENCES MEDICAL_STAFF(staff_id)`
  - `ON assigned_floor_id REFERENCES FLOORS(floor_id)`

### GENERAL_STAFF
- `staff_id` (PK)
- `job_type`
  - `ON staff_id REFERENCES STAFF(staff_id)`

### PATIENTS
- `patient_id` (PK)
- `national_id`
- `first_name`
- `last_name`
- `birth_date`
- `gender`
- `phone`
- `email`
- `address`
- `emergency_contact_name`
- `emergency_contact_phone`
- `blood_type`
- `allergies`

### VISITS
- `visit_id` (PK)
- `patient_id`
- `doctor_id`
- `visit_timestamp`
- `diagnosis`
- `notes`
  - `ON patient_id REFERENCES PATIENTS(patient_id)`
  - `ON doctor_id REFERENCES MEDICAL_STAFF(staff_id)`

### SCHEDULED_APPOINTMENTS
- `appointment_id` (PK)
- `visit_id`
- `appointment_date`
- `appointment_time`
- `status`
  - `ON visit_id REFERENCES VISITS(visit_id)`

### MEDICATIONS
- `medication_id` (PK)
- `medication_name`
- `description`

### PRESCRIPTIONS
- `prescription_id` (PK)
- `visit_id`
- `medication_id`
- `dosage`
- `frequency`
- `duration_days`
- `start_date`
  - `ON visit_id REFERENCES VISITS(visit_id)`
  - `ON medication_id REFERENCES MEDICATIONS(medication_id)`

### ADMISSIONS
- `admission_id` (PK)
- `patient_id`
- `room_id`
- `admission_date`
- `expected_discharge_date`
- `actual_discharge_date`
  - `ON patient_id REFERENCES PATIENTS(patient_id)`
  - `ON room_id REFERENCES ROOMS(room_id)`

### SURGERIES
- `surgery_id` (PK)
- `patient_id`
- `theater_id`
- `primary_surgeon_id`
- `surgery_date`
- `start_time`
- `end_time`
- `procedure_type`
- `notes`
  - `ON patient_id REFERENCES PATIENTS(patient_id)`
  - `ON theater_id REFERENCES OPERATING_THEATERS(theater_id)`
  - `ON primary_surgeon_id REFERENCES MEDICAL_STAFF(staff_id)`

### SURGERY_ASSISTANTS
- `surgery_id` (PK)
- `nurse_id` (PK)
- `role`
  - `ON surgery_id REFERENCES SURGERIES(surgery_id)`
  - `ON nurse_id REFERENCES NURSING_STAFF(staff_id)`

### PHARMACY_DISPENSATIONS
- `dispensation_id` (PK)
- `admission_id`
- `dispensed_at`
- `total_cost`
- `notes`
  - `ON admission_id REFERENCES ADMISSIONS(admission_id)`

### DISPENSATION_ITEMS
- `item_id` (PK)
- `dispensation_id`
- `medication_id`
- `quantity`
- `unit_price`
  - `ON dispensation_id REFERENCES PHARMACY_DISPENSATIONS(dispensation_id)`
  - `ON medication_id REFERENCES MEDICATIONS(medication_id)`

### RADIOLOGY_EXAMS
- `exam_id` (PK)
- `patient_id`
- `requesting_doctor_id`
- `exam_type`
- `requested_at`
- `performed_at`
- `result_image_url`
- `radiologist_report`
- `status`
  - `ON patient_id REFERENCES PATIENTS(patient_id)`
  - `ON requesting_doctor_id REFERENCES MEDICAL_STAFF(staff_id)`

### APP_USERS
- `user_id` (PK)
- `username`
- `password_hash`
- `staff_id`
- `role`
- `is_active`
- `last_login`
- `created_at`
  - `ON staff_id REFERENCES STAFF(staff_id)`

### AUDIT_LOGS
- `log_id` (PK)
- `user_id`
- `action_timestamp`
- `action_type`
- `table_name`
- `record_id`
- `old_data`
- `new_data`
- `ip_address`
- `notes`
- `ON user_id REFERENCES APP_USERS(user_id)`
