# Functional Requirements

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 1.0          |
| Last Updated   | 2026-05-04   |

## Purpose

Define the implemented functional requirements and expected operational behavior of the Hospital Management System.

## Scope

The functional scope covers:

- User authentication and registration
- Comprehensive staff, patient, and resource management
- Clinical operations: surgeries, visits, admissions, prescriptions, radiology
- Pharmacy management: medications, dispensations
- Infrastructure management: floors, rooms, operating theaters, medical devices
- Operational queries and reporting
- Dashboard with real-time statistics
- Resource browser for CRUD operations on all entities
- Dummy-data generation and cleanup for development use
- Full REST API with 20+ routes supporting CRUD for 25+ entities

This document focuses on functional behavior. Security, performance, and infrastructure constraints are documented separately.

## Primary Actors

| Actor         | Description                                                                    |
|:------------- |:------------------------------------------------------------------------------ |
| Administrator | Internal user responsible for managing users and operational records.          |
| Doctor        | Clinical user involved in patient care and operational queries.                |
| Nurse         | Clinical support user involved in assignments and operational workflows.       |
| Receptionist  | Administrative user involved in registration and scheduling-related workflows. |
| Support Staff | Non-clinical user with limited operational access.                             |

## Functional Domains

| Domain                    | Description                                                                |
|:------------------------- |:-------------------------------------------------------------------------- |
| Authentication            | Access to the application through login and session handling.              |
| User Account Management   | Registration of application users linked to hospital staff records.        |
| Staff Management          | Registration and CRUD of medical, nursing, and general staff members.      |
| Patient Management        | Registration and CRUD of patient demographic and clinical data.            |
| Nursing Assignment        | Assignment of nursing staff to a doctor or to a hospital floor.            |
| Clinical Operations       | Management of surgeries, visits, admissions, and radiology exams.          |
| Pharmacy Management       | Management of medications, prescriptions, and dispensations.               |
| Infrastructure Management | Management of floors, rooms, operating theaters, and medical devices.      |
| Operational Queries       | Consultation of surgeries, visits, and other entities by date or criteria. |
| Dashboard                 | Real-time statistics and overview of hospital operations.                  |
| Resource Browser          | Generic CRUD interface for all system entities.                            |
| Test Data Utilities       | Generation and cleanup of development dummy records.                       |

## Functional Requirements

### Authentication

| ID     | Requirement                                                                                                     |
|:------ |:--------------------------------------------------------------------------------------------------------------- |
| FR-001 | The system shall allow a user to log in using a username and password.                                          |
| FR-002 | The system shall validate login credentials against the registered application user records.                    |
| FR-003 | The system shall deny access when the username or password is invalid.                                          |
| FR-004 | The system shall issue an access token after successful authentication.                                         |
| FR-005 | The client application shall store the authenticated session in memory for the duration of the desktop session. |
| FR-006 | The system shall allow the user to log out and clear the current in-memory session.                             |

### User Account Management

| ID     | Requirement                                                                                    |
|:------ |:---------------------------------------------------------------------------------------------- |
| FR-007 | The system shall allow the creation of an application user account.                            |
| FR-008 | The system shall require `username`, `password`, `staff_id`, and `role` for user registration. |
| FR-009 | The system shall reject registration when the username already exists.                         |
| FR-010 | The system shall reject registration when the referenced `staff_id` does not exist.            |
| FR-011 | The system shall store the registered password in hashed form.                                 |
| FR-012 | The system shall associate each application user account with exactly one staff record.        |

### Staff Management

| ID     | Requirement                                                                                 |
|:------ |:------------------------------------------------------------------------------------------- |
| FR-013 | The system shall allow the registration of medical staff.                                   |
| FR-014 | The system shall allow the registration of nursing staff.                                   |
| FR-015 | The system shall allow the registration of general staff.                                   |
| FR-016 | The system shall require identification and core personal data for each staff registration. |
| FR-017 | The system shall capture role-specific information for each staff type.                     |
| FR-018 | The system shall persist medical staff with specialty and license information.              |
| FR-019 | The system shall persist nursing staff with nursing license and certification information.  |
| FR-020 | The system shall persist general staff with job-type information.                           |
| FR-021 | The system shall return the generated `staff_id` after successful registration.             |

### Patient Management

| ID     | Requirement                                                                                                         |
|:------ |:------------------------------------------------------------------------------------------------------------------- |
| FR-022 | The system shall allow the registration of patients.                                                                |
| FR-023 | The system shall require `national_id`, `first_name`, and `last_name` when registering a patient.                   |
| FR-024 | The system shall allow the capture of patient demographic, contact, emergency contact, and clinical-summary fields. |
| FR-025 | The system shall return the generated `patient_id` after successful registration.                                   |

### Nursing Assignment

| ID     | Requirement                                                                          |
|:------ |:------------------------------------------------------------------------------------ |
| FR-026 | The system shall allow assignment of a nurse to a doctor.                            |
| FR-027 | The system shall allow assignment of a nurse to a floor.                             |
| FR-028 | The system shall require a valid `nurse_id` for any nursing assignment operation.    |
| FR-029 | The system shall require either a `doctor_id` or a `floor_id` for assignment.        |
| FR-030 | The system shall clear the alternative assignment type when a nurse is reassigned.   |
| FR-031 | The system shall reject the assignment request when the nurse record does not exist. |

### Operational Queries

| ID     | Requirement                                                                                                     |
|:------ |:--------------------------------------------------------------------------------------------------------------- |
| FR-032 | The system shall allow users to query surgeries by date.                                                        |
| FR-033 | The system shall allow users to query scheduled visits by date.                                                 |
| FR-034 | The system shall require a date parameter in `YYYY-MM-DD` format for date-based query operations.               |
| FR-035 | The system shall return surgery results in a format suitable for tabular display in the desktop client.         |
| FR-036 | The system shall return scheduled visit results in a format suitable for tabular display in the desktop client. |

### Test Data Utilities

| ID     | Requirement                                                                                             |
|:------ |:------------------------------------------------------------------------------------------------------- |
| FR-037 | The system shall allow authorized users to trigger dummy-data generation.                               |
| FR-038 | The system shall allow authorized users to clean previously generated dummy data.                       |
| FR-039 | The client application shall display a confirmation message before starting bulk dummy-data generation. |

### Clinical Operations

| ID     | Requirement                                                        |
|:------ |:------------------------------------------------------------------ |
| FR-043 | The system shall support full CRUD operations for surgeries.       |
| FR-044 | The system shall support full CRUD operations for visits.          |
| FR-045 | The system shall support full CRUD operations for admissions.      |
| FR-046 | The system shall support full CRUD operations for radiology exams. |
| FR-047 | The system shall manage surgery assistants and their assignments.  |

### Pharmacy Management

| ID     | Requirement                                                               |
|:------ |:------------------------------------------------------------------------- |
| FR-048 | The system shall support full CRUD operations for medications.            |
| FR-049 | The system shall support full CRUD operations for prescriptions.          |
| FR-050 | The system shall support full CRUD operations for pharmacy dispensations. |
| FR-051 | The system shall manage dispensation items linked to prescriptions.       |

### Infrastructure Management

| ID     | Requirement                                                            |
|:------ |:---------------------------------------------------------------------- |
| FR-052 | The system shall support full CRUD operations for floors.              |
| FR-053 | The system shall support full CRUD operations for rooms.               |
| FR-054 | The system shall support full CRUD operations for operating theaters.  |
| FR-055 | The system shall support full CRUD operations for medical devices.     |
| FR-056 | The system shall support full CRUD operations for medical specialties. |

### Dashboard

| ID     | Requirement                                                                           |
|:------ |:------------------------------------------------------------------------------------- |
| FR-057 | The system shall display real-time statistics for patients, staff, rooms, and visits. |
| FR-058 | The system shall show today's surgeries and scheduled visits.                         |

### Resource Browser

| ID     | Requirement                                                               |
|:------ |:------------------------------------------------------------------------- |
| FR-059 | The system shall provide a generic CRUD interface for all entities.       |
| FR-060 | The system shall allow selection of entity type for browsing and editing. |

## User Interface Requirements

| ID     | Requirement                                                                                           |
|:------ |:----------------------------------------------------------------------------------------------------- |
| FR-061 | The client shall provide a login screen as the application entry point.                               |
| FR-062 | The client shall provide a registration screen for creating new application users.                    |
| FR-063 | The client shall provide a main menu after successful login.                                          |
| FR-064 | The client shall provide separate maintenance forms for doctors, nurses, general staff, and patients. |
| FR-065 | The client shall provide a dedicated interface for nursing assignment.                                |
| FR-066 | The client shall provide date-based consultation screens for surgeries and visits.                    |
| FR-067 | The client shall provide a dashboard with real-time statistics and today's operations.                |
| FR-068 | The client shall provide a resource browser for CRUD operations on all entities.                      |
| FR-069 | The client shall provide test data generation and cleanup interfaces.                                 |
| FR-070 | The client shall display success and error feedback messages for user actions.                        |

## Business Rules

| ID     | Rule                                                                                             |
|:------ |:------------------------------------------------------------------------------------------------ |
| BR-001 | An application user cannot be registered unless the corresponding staff record already exists.   |
| BR-002 | Password confirmation must match before a user account can be created from the client interface. |
| BR-003 | A nurse assignment must target either a doctor or a floor, but not neither.                      |
| BR-004 | Protected operational routes require a valid authenticated session.                              |
| BR-005 | Mandatory identity fields must be present before staff or patient registration is submitted.     |

## Current Out of Scope

The following capabilities are not currently implemented in the functional scope:

- Role-based route authorization enforcement (tokens issued but not checked)
- Password recovery workflow
- Audit logging
- High availability and backup implementation
- TLS/mTLS runtime configuration
- Billing, inventory, and advanced laboratory modules
- Data export from the main menu
- Advanced reporting and analytics

## Traceability to Implemented Modules

| Functional Area           | Main Files                                                                                                                                        |
|:------------------------- |:------------------------------------------------------------------------------------------------------------------------------------------------- |
| Authentication            | `client/views/login_view.py`, `client/views/register_view.py`, `server/app/routes/auth.py`, `server/app/services/auth_service.py`                 |
| Staff management          | `client/views/maintenance_view.py`, `server/app/routes/maintenance.py`, `server/app/services/staff_service.py`                                    |
| Patient management        | `client/views/maintenance_view.py`, `server/app/services/patient_service.py`                                                                      |
| Clinical operations       | `server/app/routes/surgery.py`, `server/app/routes/visit.py`, `server/app/routes/admission.py`, `server/app/routes/radiology_exam.py`             |
| Pharmacy management       | `server/app/routes/medication.py`, `server/app/routes/prescription.py`, `server/app/routes/pharmacy_dispensation.py`                              |
| Infrastructure management | `server/app/routes/floor.py`, `server/app/routes/room.py`, `server/app/routes/operating_theater.py`, `server/app/routes/medical_device.py`        |
| Operational queries       | `client/views/surgeries_view.py`, `client/views/visits_view.py`, `server/app/services/surgery_service.py`, `server/app/services/visit_service.py` |
| Dashboard                 | `client/views/dashboard_view.py`                                                                                                                  |
| Resource browser          | `client/views/resource_browser.py`                                                                                                                |
| Dummy-data utilities      | `client/views/test_data_view.py`, `server/app/routes/dummy.py`, `server/app/services/dummy_service.py`                                            |

