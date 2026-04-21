# 🔐 Security Matrix: RBAC Roles and Permissions

> This document defines the Role-Based Access Control (RBAC) matrix for the Hospital Management System. It maps the system roles defined in the `APP_USERS` table to their corresponding permissions on database objects and functional modules. The implementation will be enforced at the application layer (Python/Tkinter) with complementary database-level restrictions where applicable.

## 1. Role Definitions

| Role          | `APP_USERS.role` Value | Associated Staff Type(s)                                                                          | Scope of Access                                                                           |
|:--------------|:-----------------------|:--------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------|
| **Administrator** | `ADMIN`                | IT / System Administrators (`GENERAL_STAFF`)                                                       | Full system configuration, user management, audit log review.                             |
| **Doctor**        | `DOCTOR`               | `MEDICAL_STAFF` (surgeons, specialists)                                                            | Patient clinical data, prescriptions, surgery scheduling, lab/radiology orders.           |
| **Nurse**         | `NURSE`               | `NURSING_STAFF`                                                                                    | Patient vitals, admissions/discharges, assisting in surgeries, medication administration. |
| **Receptionist**  | `RECEPTIONIST`         | `GENERAL_STAFF` (front-desk, administrative)                                                       | Patient registration, appointment scheduling, basic demographic updates.                  |
| **Staff**         | `STAFF`               | All other `GENERAL_STAFF` (maintenance, pharmacy techs, billing) – *future extensible base role*   | Limited access specific to their job function (e.g., pharmacy inventory).                 |

## 2. Permission Matrix

The following matrix details **Data Manipulation Language (DML)** permissions (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) on core tables. Additional **functional permissions** (e.g., "Can approve surgery", "Can export reports") will be managed in the application business logic.

| Table / Functional Area                | ADMIN              | DOCTOR             | NURSE              | RECEPTIONIST       | STAFF (Base)       | Notes                                                                                                                              |
|:---------------------------------------|:------------------:|:------------------:|:------------------:|:------------------:|:------------------:|:-----------------------------------------------------------------------------------------------------------------------------------|
| **Patient Demographics**               |                    |                    |                    |                    |                    |                                                                                                                                     |
| `PATIENTS`                             | ALL                | ALL                | SELECT, UPDATE¹    | ALL                | SELECT (limited²)  | ¹ Nurses can update contact info, allergies, blood type. ² Staff may see only name and room number for directory purposes.         |
| **Clinical Encounters**                |                    |                    |                    |                    |                    |                                                                                                                                     |
| `VISITS`                               | ALL                | ALL                | SELECT, INSERT³    | SELECT, INSERT³    | —                  | ³ Insert only for walk-in registration; clinical notes restricted.                                                                 |
| `SCHEDULED_APPOINTMENTS`               | ALL                | ALL                | SELECT, UPDATE⁴    | ALL                | SELECT (limited)   | ⁴ Nurses can update status (e.g., mark as 'COMPLETED' or 'NO_SHOW').                                                               |
| `PRESCRIPTIONS`                        | ALL                | ALL                | SELECT             | —                  | —                  | Only doctors can issue prescriptions.                                                                                              |
| `MEDICATIONS` (catalog)                | ALL                | SELECT             | SELECT             | —                  | SELECT (if pharmacy) | Reference table; modifications by pharmacy staff via admin.                                                                        |
| **Inpatient Management**               |                    |                    |                    |                    |                    |                                                                                                                                     |
| `ADMISSIONS`                           | ALL                | ALL                | SELECT, INSERT, UPDATE⁵ | —                  | —                  | ⁵ Nurses can update `actual_discharge_date`.                                                                                        |
| `ROOMS` / `FLOORS`                     | ALL                | SELECT             | SELECT             | SELECT             | SELECT             | Static reference data.                                                                                                             |
| **Surgical Suite**                     |                    |                    |                    |                    |                    |                                                                                                                                     |
| `SURGERIES`                            | ALL                | ALL                | SELECT, INSERT⁶    | —                  | —                  | ⁶ Nurses can be added as `SURGERY_ASSISTANTS`.                                                                                      |
| `SURGERY_ASSISTANTS`                   | ALL                | ALL                | SELECT, INSERT     | —                  | —                  |                                                                                                                                     |
| `OPERATING_THEATERS` / `MEDICAL_DEVICES` | ALL                | SELECT             | SELECT             | —                  | —                  |                                                                                                                                     |
| **Diagnostic Services**                |                    |                    |                    |                    |                    |                                                                                                                                     |
| `RADIOLOGY_EXAMS`                      | ALL                | ALL (request/view) | SELECT, UPDATE⁷    | —                  | —                  | ⁷ Nurses/techs can update `performed_at` and `status`.                                                                              |
| **Pharmacy**                           |                    |                    |                    |                    |                    |                                                                                                                                     |
| `PHARMACY_DISPENSATIONS`               | ALL                | SELECT             | SELECT, INSERT⁸    | —                  | ALL (pharmacy)     | ⁸ Nurses record administration of meds from dispensation. Pharmacy staff manage inventory/dispensation via `STAFF` role extension. |
| `DISPENSATION_ITEMS`                   | ALL                | SELECT             | SELECT             | —                  | ALL (pharmacy)     |                                                                                                                                     |
| **Staff & User Management**            |                    |                    |                    |                    |                    |                                                                                                                                     |
| `STAFF` (all subtypes)                 | ALL                | SELECT (own)       | SELECT (own)       | SELECT (own)       | SELECT (own)       | `SELECT (own)` means user can view their own personnel record.                                                                      |
| `MEDICAL_SPECIALTIES`                  | ALL                | SELECT             | SELECT             | —                  | —                  |                                                                                                                                     |
| `APP_USERS`                            | ALL                | UPDATE (own pwd)⁹  | UPDATE (own pwd)⁹  | UPDATE (own pwd)⁹  | UPDATE (own pwd)⁹  | ⁹ Password change only via application.                                                                                             |
| `AUDIT_LOGS`                           | SELECT             | —                  | —                  | —                  | —                  | Administrators only.                                                                                                                |

## 3. Implementation Notes for Python/psycopg2

The permissions described above will be implemented through a combination of:

1.  **Database Roles & Privileges:** PostgreSQL `GRANT` statements will be applied to role-specific database users (e.g., `app_doctor`, `app_nurse`) to provide a first layer of defense.
    ```sql
    -- Example: Doctor role grants
    GRANT SELECT, INSERT, UPDATE, DELETE ON patients, visits, prescriptions TO app_doctor;
    GRANT SELECT ON medications, rooms TO app_doctor;
    ```

2.  **Application-Layer Checks:** The Tkinter interface will dynamically enable/disable UI components (buttons, menu items, edit fields) based on the logged-in user's role retrieved from `APP_USERS`. psycopg2 will execute queries using the specific database user's connection to enforce server-side restrictions.

3.  **Row-Level Security (RLS):** For fine-grained access (e.g., "Nurse assigned to floor X can only see patients in floor X rooms"), PostgreSQL RLS policies will be employed. This is managed in the database layer and is transparent to the Python application.

## 4. Audit Trail Compliance

All `INSERT`, `UPDATE`, and `DELETE` operations on tables containing sensitive patient data (`PATIENTS`, `VISITS`, `PRESCRIPTIONS`, `ADMISSIONS`, `SURGERIES`) will trigger an entry in the `AUDIT_LOGS` table via PostgreSQL triggers. The `user_id` from `APP_USERS` will be captured to maintain an immutable record of who performed the action and when.