# Data Dictionary

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 2.1          |
| Last Updated   | 2026-05-06   |

## Purpose

Describe the principal data structures and provide implementation-oriented field and constraint guidance that complements the relational model.

## Conventions

- Primary keys are represented as integer surrogate keys.
- Foreign keys reference the parent entity by its identifier.
- Detailed physical data types may evolve during implementation.
- Sensitive fields must be protected according to the security documentation.

## Entity Summary

### `FLOORS`

| Field          | Description                               |
|:-------------- |:----------------------------------------- |
| `floor_id`     | Unique identifier for the hospital floor. |
| `floor_number` | Human-readable floor number.              |

### `ROOMS`

| Field         | Description                      |
|:------------- |:-------------------------------- |
| `room_id`     | Unique identifier for the room.  |
| `room_number` | Operational room code or number. |
| `floor_id`    | Reference to the parent floor.   |

### `OPERATING_THEATERS`

| Field          | Description                                        |
|:-------------- |:-------------------------------------------------- |
| `theater_id`   | Unique identifier for the operating theater.       |
| `theater_code` | Operational code used for scheduling and tracking. |
| `floor_id`     | Reference to the parent floor.                     |

### `MEDICAL_DEVICES`

| Field         | Description                               |
|:------------- |:----------------------------------------- |
| `device_id`   | Unique identifier for the device record.  |
| `device_type` | Device category or equipment type.        |
| `theater_id`  | Theater where the device is assigned.     |
| `quantity`    | Available quantity for the device record. |

### `STAFF`

| Field                       | Description                                         |
|:--------------------------- |:--------------------------------------------------- |
| `staff_id`                  | Unique identifier for the staff member.             |
| `national_id`               | Government-issued identifier.                       |
| `first_name`, `last_name`   | Staff legal name.                                   |
| `birth_date`                | Date of birth.                                      |
| `phone`, `email`, `address` | Contact details.                                    |
| `ssn`                       | Social security or equivalent affiliation number.   |
| `hire_date`                 | Employment start date.                              |
| `staff_type`                | Staff classification: medical, nursing, or general. |

### `MEDICAL_STAFF`

| Field            | Description                         |
|:---------------- |:----------------------------------- |
| `staff_id`       | Reference to the base staff record. |
| `specialty_id`   | Primary specialty.                  |
| `license_number` | Professional license identifier.    |
| `curriculum`     | Professional background summary.    |

### `NURSING_STAFF`

| Field                | Description                               |
|:-------------------- |:----------------------------------------- |
| `staff_id`           | Reference to the base staff record.       |
| `nursing_license`    | Professional nursing license.             |
| `assigned_doctor_id` | Supervising doctor, if applicable.        |
| `assigned_floor_id`  | Primary floor assignment.                 |
| `certifications`     | Additional certifications or credentials. |

### `GENERAL_STAFF`

| Field      | Description                              |
|:---------- |:---------------------------------------- |
| `staff_id` | Reference to the base staff record.      |
| `job_type` | Operational or administrative role name. |

### `MEDICAL_SPECIALTIES`

| Field          | Description                            |
|:-------------- |:-------------------------------------- |
| `specialty_id` | Unique identifier for the specialty.   |
| `name`         | Specialty name.                        |
| `description`  | Descriptive notes about the specialty. |

### `MEDICAL_STAFF_SPECIALTIES`

| Field                        | Description                                    |
|:---------------------------- |:---------------------------------------------- |
| `medical_staff_specialty_id` | Surrogate identifier for the relationship row. |
| `staff_id`                   | Reference to a doctor.                         |
| `specialty_id`               | Reference to a specialty.                      |

### `PATIENTS`

| Field                                               | Description                               |
|:--------------------------------------------------- |:----------------------------------------- |
| `patient_id`                                        | Unique patient identifier.                |
| `national_id`                                       | Government-issued identifier.             |
| `first_name`, `last_name`                           | Patient legal name.                       |
| `birth_date`                                        | Date of birth.                            |
| `gender`                                            | Gender classification used by the system. |
| `phone`, `email`, `address`                         | Contact details.                          |
| `emergency_contact_name`, `emergency_contact_phone` | Emergency contact information.            |
| `blood_type`                                        | Blood group if registered.                |
| `allergies`                                         | Known allergy information.                |

### `VISITS`

| Field             | Description                          |
|:----------------- |:------------------------------------ |
| `visit_id`        | Unique identifier for the encounter. |
| `patient_id`      | Reference to the patient.            |
| `doctor_id`       | Reference to the attending doctor.   |
| `visit_timestamp` | Encounter date and time.             |
| `diagnosis`       | Clinical diagnosis notes.            |
| `notes`           | Additional encounter observations.   |

### `SCHEDULED_APPOINTMENTS`

| Field                                  | Description                     |
|:-------------------------------------- |:------------------------------- |
| `appointment_id`                       | Unique appointment identifier.  |
| `visit_id`                             | Related visit record.           |
| `appointment_date`, `appointment_time` | Scheduled slot.                 |
| `status`                               | Operational appointment status. |

### `MEDICATIONS`

| Field             | Description                     |
|:----------------- |:------------------------------- |
| `medication_id`   | Unique medication identifier.   |
| `medication_name` | Medication name.                |
| `description`     | Reference notes or indications. |

### `PRESCRIPTIONS`

| Field                 | Description                     |
|:--------------------- |:------------------------------- |
| `prescription_id`     | Unique prescription identifier. |
| `visit_id`            | Related patient encounter.      |
| `medication_id`       | Prescribed medication.          |
| `dosage`, `frequency` | Administration instructions.    |
| `duration_days`       | Intended duration of treatment. |
| `start_date`          | Prescription start date.        |

### `ADMISSIONS`

| Field                     | Description                        |
|:------------------------- |:---------------------------------- |
| `admission_id`            | Unique admission identifier.       |
| `patient_id`              | Reference to the admitted patient. |
| `room_id`                 | Assigned room.                     |
| `admission_date`          | Start of inpatient stay.           |
| `expected_discharge_date` | Planned discharge date.            |
| `actual_discharge_date`   | Actual discharge date.             |

### `SURGERIES`

| Field                                    | Description                 |
|:---------------------------------------- |:--------------------------- |
| `surgery_id`                             | Unique surgery identifier.  |
| `patient_id`                             | Patient undergoing surgery. |
| `theater_id`                             | Assigned operating theater. |
| `primary_surgeon_id`                     | Lead surgeon.               |
| `surgery_date`, `start_time`, `end_time` | Scheduling data.            |
| `procedure_type`                         | Procedure classification.   |
| `notes`                                  | Surgery-specific notes.     |

### `SURGERY_ASSISTANTS`

| Field        | Description                          |
|:------------ |:------------------------------------ |
| `surgery_id` | Related surgery.                     |
| `nurse_id`   | Participating nursing staff member.  |
| `role`       | Assistant role during the procedure. |

### `PHARMACY_DISPENSATIONS`

| Field             | Description                     |
|:----------------- |:------------------------------- |
| `dispensation_id` | Dispensation header identifier. |
| `admission_id`    | Related admission.              |
| `dispensed_at`    | Timestamp of dispensation.      |
| `total_cost`      | Total dispensation cost.        |
| `notes`           | Supporting notes.               |

### `DISPENSATION_ITEMS`

| Field             | Description                        |
|:----------------- |:---------------------------------- |
| `item_id`         | Unique line-item identifier.       |
| `dispensation_id` | Parent dispensation header.        |
| `medication_id`   | Medication dispensed.              |
| `quantity`        | Units dispensed.                   |
| `unit_price`      | Price per unit at dispensing time. |

### `RADIOLOGY_EXAMS`

| Field                          | Description                     |
|:------------------------------ |:------------------------------- |
| `exam_id`                      | Unique exam identifier.         |
| `patient_id`                   | Related patient.                |
| `requesting_doctor_id`         | Physician who ordered the exam. |
| `exam_type`                    | Imaging exam category.          |
| `requested_at`, `performed_at` | Workflow timestamps.            |
| `result_image_url`             | Reference to imaging output.    |
| `radiologist_report`           | Clinical interpretation.        |
| `status`                       | Current workflow status.        |

### `APP_USERS`

| Field                      | Description                   |
|:-------------------------- |:----------------------------- |
| `user_id`                  | Unique user identifier.       |
| `username`                 | Login name.                   |
| `password_hash`            | Stored password hash.         |
| `staff_id`                 | Linked staff member.          |
| `role`                     | Assigned RBAC role.           |
| `is_active`                | Account state.                |
| `last_login`, `created_at` | Account lifecycle timestamps. |

### `AUDIT_LOGS`

| Field                     | Description                      |
|:------------------------- |:-------------------------------- |
| `log_id`                  | Unique audit record identifier.  |
| `user_id`                 | User associated with the action. |
| `action_timestamp`        | When the action occurred.        |
| `action_type`             | Type of audited action.          |
| `table_name`, `record_id` | Target entity metadata.          |
| `old_data`, `new_data`    | Serialized change snapshots.     |
| `ip_address`              | Origin metadata when available.  |
| `notes`                   | Additional audit context.        |
