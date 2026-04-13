# Relational Model
> This document details the relational model for our hospital management system, outlining the tables, their attributes, and the relationships between them. The design is based on the ER diagram and follows normalization principles to ensure data integrity and efficiency.

## Tables
### FLOORS
- `Floor_id` (PK)
- `Floor_number`

### ROOMS
- `Room_id` (PK)
- `Room_number`
- `Floor_id`
  - `ON Floor_id REFERENCES FLOORS(Floor_id)`

### OPERATING_THEATERS
- `Theater_id` (PK)
- `Theater_code`
- `Floor_id`
  - `ON Floor_id REFERENCES FLOORS(Floor_id)`

### MEDICAL_DEVICES
- `Device_id` (PK)
- `Device_type`
- `Theater_id`
- `Quantity`
  - `ON Theater_id REFERENCES OPERATING_THEATERS(Theater_id)`

### MEDICAL_SPECIALTIES
- `Specialty_id` (PK)
- `Name`
- `Description`

### STAFF
- `Staff_id` (PK)
- `National_id`
- `First_name`
- `Last_name`
- `Birth_date`
- `Phone`
- `Email`
- `Address`
- `Hire_date`
- `Staff_type`

### MEDICAL_STAFF
- `Staff_id` (PK)
- `Specialty_id`
- `License_number`
- `Curriculum`
  - `ON Staff_id REFERENCES STAFF(Staff_id)`
  - `ON Specialty_id REFERENCES MEDICAL_SPECIALTIES(Specialty_id)`

### NURSING_STAFF
- `Staff_id` (PK)
- `Nursing_license`
- `Assigned_doctor_id`
- `Is_floor_nurse`
- `Certifications`
  - `ON Staff_id REFERENCES STAFF(Staff_id)`
  - `ON Assigned_doctor_id REFERENCES MEDICAL_STAFF(Staff_id)`

### GENERAL_STAFF
- `Staff_id` (PK)
- `Job_type`
  - `ON Staff_id REFERENCES STAFF(Staff_id)`

### PATIENTS
- `Patient_id` (PK)
- `National_id`
- `First_name`
- `Last_name`
- `Birth_date`
- `Gender`
- `Phone`
- `Email`
- `Address`
- `Emergency_contact_name`
- `Emergency_contact_phone`
- `Blood_type`
- `Allergies`

### VISITS
- `Visit_id` (PK)
- `Patient_id`
- `Doctor_id`
- `Visit_timestamp`
- `Diagnosis`
- `Notes`
  - `ON Patient_id REFERENCES PATIENTS(Patient_id)`
  - `ON Doctor_id REFERENCES MEDICAL_STAFF(Staff_id)`

### SCHEDULED_APPOINTMENTS
- `Appointment_id` (PK)
- `Visit_id`
- `Appointment_date`
- `Appointment_time`
- `Status`
  - `ON Visit_id REFERENCES VISITS(Visit_id)`

### PRESCRIPTIONS
- `Prescription_id` (PK)
- `Visit_id`
- `Medication_name`
- `Dosage`
- `Frequency`
- `Duration_days`
- `Start_date`
  - `ON Visit_id REFERENCES VISITS(Visit_id)`

### ADMISSIONS
- `Admission_id` (PK)
- `Patient_id`
- `Room_id`
- `Admission_date`
- `Expected_discharge_date`
- `Actual_discharge_date`
  - `ON Patient_id REFERENCES PATIENTS(Patient_id)`
  - `ON Room_id REFERENCES ROOMS(Room_id)`

### SURGERIES
- `Surgery_id` (PK)
- `Patient_id`
- `Theater_id`
- `Primary_surgeon_id`
- `Surgery_date`
- `Start_time`
- `End_time`
- `Procedure_type`
- `Notes`
  - `ON Patient_id REFERENCES PATIENTS(Patient_id)`
  - `ON Theater_id REFERENCES OPERATING_THEATERS(Theater_id)`
  - `ON Primary_surgeon_id REFERENCES MEDICAL_STAFF(Staff_id)`

### SURGERY_ASSISTANTS
- `Surgery_id` (PK)
- `Nurse_id` (PK)
- `Role`
  - `ON Surgery_id REFERENCES SURGERIES(Surgery_id)`
  - `ON Nurse_id REFERENCES NURSING_STAFF(Staff_id)`

### PHARMACY_DISPENSATIONS
- `Dispensation_id` (PK)
- `Admission_id`
- `Dispensed_at`
- `Total_cost`
- `Notes`
  - `ON Admission_id REFERENCES ADMISSIONS(Admission_id)`

### DISPENSATION_ITEMS
- `Item_id` (PK)
- `Dispensation_id`
- `Medication_name`
- `Quantity`
- `Unit_price`
  - `ON Dispensation_id REFERENCES PHARMACY_DISPENSATIONS(Dispensation_id)`

### RADIOLOGY_EXAMS
- `Exam_id` (PK)
- `Patient_id`
- `Requesting_doctor_id`
- `Exam_type`
- `Requested_at`
- `Performed_at`
- `Result_image_url`
- `Radiologist_report`
- `Status`
  - `ON Patient_id REFERENCES PATIENTS(Patient_id)`
  - `ON Requesting_doctor_id REFERENCES MEDICAL_STAFF(Staff_id)`

### APP_USERS
- `User_id` (PK)
- `Username`
- `Password_hash`
- `Staff_id`
- `Role`
- `Is_active`
- `Last_login`
- `Created_at`
  - `ON Staff_id REFERENCES STAFF(Staff_id)`

### AUDIT_LOGS
- `Log_id` (PK)
- `User_id`
- `Action_timestamp`
- `Action_type`
- `Table_name`
- `Record_id`
- `Old_data`
- `New_data`
- `Ip_address`
- `Notes`
  - `ON User_id REFERENCES APP_USERS(User_id)`