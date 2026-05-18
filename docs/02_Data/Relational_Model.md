# Relational Model

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 2.1          |
| Last Updated   | 2026-05-06   |

## Purpose

This document describes the logical relational model of the Hospital Management System. It identifies the core entities, the main attributes, and the relationships required to support clinical, administrative, and audit workflows.

## Domain Areas

- Facility management
- Staff and identity management
- Patient and encounter management
- Inpatient and surgery workflows
- Pharmacy and radiology operations
- Application security and auditing

## Core Entities

### Facility Management

| Entity               | Key Attributes                                       | Main Relationships                                              |
|:-------------------- |:---------------------------------------------------- |:--------------------------------------------------------------- |
| `FLOORS`             | `floor_id`, `floor_number`                           | Parent of `ROOMS`, `OPERATING_THEATERS`, and floor assignments. |
| `ROOMS`              | `room_id`, `room_number`, `floor_id`                 | Referenced by `ADMISSIONS`.                                     |
| `OPERATING_THEATERS` | `theater_id`, `theater_code`, `floor_id`             | Referenced by `SURGERIES` and `MEDICAL_DEVICES`.                |
| `MEDICAL_DEVICES`    | `device_id`, `device_type`, `theater_id`, `quantity` | Inventory per operating theater.                                |

### Staff and Identity Management

| Entity                      | Key Attributes                               | Main Relationships                                                     |
|:--------------------------- |:-------------------------------------------- |:---------------------------------------------------------------------- |
| `STAFF`                     | `staff_id`, personal data, `staff_type`      | Parent entity for all staff subclasses and user accounts.              |
| `MEDICAL_STAFF`             | `staff_id`, `specialty_id`, `license_number` | Doctor profile linked to `VISITS`, `SURGERIES`, and `RADIOLOGY_EXAMS`. |
| `NURSING_STAFF`             | `staff_id`, `nursing_license`, assignments   | Nursing profile linked to inpatient and surgery workflows.             |
| `GENERAL_STAFF`             | `staff_id`, `job_type`                       | Administrative or support roles.                                       |
| `MEDICAL_SPECIALTIES`       | `specialty_id`, `name`                       | Catalog of clinical specialties.                                       |
| `MEDICAL_STAFF_SPECIALTIES` | `staff_id`, `specialty_id`                   | Many-to-many relationship between medical staff and specialties.       |
| `APP_USERS`                 | `user_id`, `username`, `staff_id`, `role`    | Authentication and authorization layer for staff.                      |

### Patient and Care Management

| Entity                   | Key Attributes                                            | Main Relationships                                     |
|:------------------------ |:--------------------------------------------------------- |:------------------------------------------------------ |
| `PATIENTS`               | `patient_id`, demographics, emergency contacts, allergies | Parent of multiple clinical workflows.                 |
| `VISITS`                 | `visit_id`, `patient_id`, `doctor_id`, clinical notes     | Parent of appointments and prescriptions.              |
| `SCHEDULED_APPOINTMENTS` | `appointment_id`, `visit_id`, schedule, status            | One-to-one with `VISITS` in the current model.         |
| `PRESCRIPTIONS`          | `prescription_id`, `visit_id`, `medication_id`, dosage    | Connects encounters and medications.                   |
| `MEDICATIONS`            | `medication_id`, `medication_name`                        | Reference catalog for prescriptions and dispensations. |

### Inpatient, Surgery, and Diagnostics

| Entity                   | Key Attributes                                                 | Main Relationships                                   |
|:------------------------ |:-------------------------------------------------------------- |:---------------------------------------------------- |
| `ADMISSIONS`             | `admission_id`, `patient_id`, `room_id`, discharge dates       | Parent of pharmacy dispensations.                    |
| `SURGERIES`              | `surgery_id`, `patient_id`, `theater_id`, `primary_surgeon_id` | Parent of `SURGERY_ASSISTANTS`.                      |
| `SURGERY_ASSISTANTS`     | `surgery_id`, `nurse_id`, `role`                               | Junction table for nurse participation in surgeries. |
| `PHARMACY_DISPENSATIONS` | `dispensation_id`, `admission_id`, `dispensed_at`              | Parent of `DISPENSATION_ITEMS`.                      |
| `DISPENSATION_ITEMS`     | `item_id`, `dispensation_id`, `medication_id`                  | Line-item detail for pharmacy activity.              |
| `RADIOLOGY_EXAMS`        | `exam_id`, `patient_id`, `requesting_doctor_id`, `status`      | Stores imaging workflow metadata and reports.        |

### Security and Audit

| Entity       | Key Attributes                                         | Main Relationships                               |
|:------------ |:------------------------------------------------------ |:------------------------------------------------ |
| `AUDIT_LOGS` | `log_id`, `user_id`, `action_type`, `action_timestamp` | Immutable traceability for sensitive operations. |

## Relationship Summary

| Relationship                                     | Type                             |
|:------------------------------------------------ |:-------------------------------- |
| `FLOORS` to `ROOMS`                              | One-to-many                      |
| `FLOORS` to `OPERATING_THEATERS`                 | One-to-many                      |
| `STAFF` to subtype tables                        | One-to-one                       |
| `STAFF` to `APP_USERS`                           | One-to-one                       |
| `PATIENTS` to `VISITS`                           | One-to-many                      |
| `PATIENTS` to `ADMISSIONS`                       | One-to-many                      |
| `PATIENTS` to `SURGERIES`                        | One-to-many                      |
| `PATIENTS` to `RADIOLOGY_EXAMS`                  | One-to-many                      |
| `VISITS` to `PRESCRIPTIONS`                      | One-to-many                      |
| `VISITS` to `SCHEDULED_APPOINTMENTS`             | One-to-one in the current design |
| `ADMISSIONS` to `PHARMACY_DISPENSATIONS`         | One-to-many                      |
| `PHARMACY_DISPENSATIONS` to `DISPENSATION_ITEMS` | One-to-many                      |
| `SURGERIES` to `SURGERY_ASSISTANTS`              | One-to-many                      |
| `MEDICAL_STAFF` to `MEDICAL_SPECIALTIES`         | Many-to-many via junction table  |

## Modeling Notes

- Clinical and administrative data are intentionally separated by business domain.
- Staff inheritance is modeled through subtype tables to keep the base staff entity normalized.
- Auditability is treated as a first-class requirement, not an implementation detail.
- The model is prepared for future expansion into billing, laboratory, inventory, and interoperability modules.
