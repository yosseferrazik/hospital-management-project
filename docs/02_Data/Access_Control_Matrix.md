# Access Control Matrix

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 2.1          |
| Last Updated   | 2026-05-06   |

## Purpose

Define the RBAC model mapping business roles to data and functional permissions for the HMS.

## Roles

| Role          | Code           | Typical Profile                           | Responsibility Scope                                                    |
|:------------- |:-------------- |:----------------------------------------- |:----------------------------------------------------------------------- |
| Administrator | `ADMIN`        | Systems and platform administrators       | Platform configuration, user administration, and audit review.          |
| Doctor        | `DOCTOR`       | Medical staff                             | Clinical documentation, prescriptions, diagnostics, and care decisions. |
| Nurse         | `NURSE`        | Nursing staff                             | Inpatient operations, patient follow-up, and support workflows.         |
| Receptionist  | `RECEPTIONIST` | Front-desk staff                          | Patient registration and appointment management.                        |
| Staff         | `STAFF`        | Non-clinical or specialized support staff | Controlled access limited to assigned operational responsibilities.     |

## Data Access Matrix

| Domain or Table          | ADMIN | DOCTOR                | NURSE                   | RECEPTIONIST          | STAFF                 | Notes                                                |
|:------------------------ |:-----:|:---------------------:|:-----------------------:|:---------------------:|:---------------------:|:---------------------------------------------------- |
| `PATIENTS`               | Full  | Full                  | Read and limited update | Full                  | Restricted read       | Nurse updates must be limited to operational fields. |
| `VISITS`                 | Full  | Full                  | Read and limited insert | Limited insert        | No access             | Clinical notes remain under doctor control.          |
| `SCHEDULED_APPOINTMENTS` | Full  | Full                  | Read and status update  | Full                  | Restricted read       | Useful for care coordination and scheduling.         |
| `PRESCRIPTIONS`          | Full  | Full                  | Read                    | No access             | No access             | Doctors remain the issuing authority.                |
| `MEDICATIONS`            | Full  | Read                  | Read                    | No access             | Contextual read       | Support staff access depends on pharmacy scope.      |
| `ADMISSIONS`             | Full  | Full                  | Read and update         | No access             | No access             | Supports inpatient workflows.                        |
| `ROOMS` and `FLOORS`     | Full  | Read                  | Read                    | Read                  | Read                  | Reference data.                                      |
| `SURGERIES`              | Full  | Full                  | Read and limited insert | No access             | No access             | Nursing participation is role-specific.              |
| `SURGERY_ASSISTANTS`     | Full  | Full                  | Read and insert         | No access             | No access             | Tracks surgical support roles.                       |
| `RADIOLOGY_EXAMS`        | Full  | Full                  | Read and status update  | No access             | No access             | Protect radiology findings as clinical data.         |
| `PHARMACY_DISPENSATIONS` | Full  | Read                  | Read and insert         | No access             | Scoped full           | Pharmacy extension may be modeled under `STAFF`.     |
| `DISPENSATION_ITEMS`     | Full  | Read                  | Read                    | No access             | Scoped full           | Same scope as pharmacy dispensations.                |
| `STAFF`                  | Full  | Own record            | Own record              | Own record            | Own record            | Self-service access only outside administration.     |
| `APP_USERS`              | Full  | Password self-service | Password self-service   | Password self-service | Password self-service | Account lifecycle remains administrative.            |
| `AUDIT_LOGS`             | Read  | No access             | No access               | No access             | No access             | Audit visibility is restricted.                      |

## Enforcement Model

- Database privileges provide the first control boundary.
- Application authorization enforces business rules and workflow-specific constraints.
- Row-level security may be introduced for patient or floor-specific restrictions.
- Sensitive actions must be traceable through immutable audit records.

## Design Principles

- Enforce least privilege by default.
- Separate operational convenience from clinical authority.
- Restrict write access on high-risk clinical data.
- Preserve a clear path toward finer-grained permissions in future phases.
