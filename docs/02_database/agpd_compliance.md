# AGPD Compliance Document

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 1.0          |
| Last Updated   | 2026-05-19   |

## 1. Data Controller

| Field                  | Data                                    |
|:---------------------- |:--------------------------------------- |
| Entity                 | Hospital de Blanes                      |
| Address                | Blanes, Girona                          |
| Processing purpose     | Hospital management (visits, admissions, surgeries, prescriptions) |
| Legal basis            | LOPDGDD 3/2018 + GDPR (EU) 2016/679     |

## 2. Personal Data Categories and Risk Level

### 2.1 HIGH risk data (require reinforced measures)

| Category                     | DB tables           | Examples                                 |
|:---------------------------- |:------------------- |:---------------------------------------- |
| Health data (diagnoses)      | VISITS              | Diagnosis, clinical notes                 |
| Health data (surgeries)      | SURGERIES           | Procedure, surgical notes                 |
| Health data (prescriptions)  | PRESCRIPTIONS       | Medication, dosage, frequency             |
| Health data (tests)          | RADIOLOGY_EXAMS     | Radiology report, images                  |
| Genetic / biometric data     | PATIENTS            | Blood type, allergies                     |

### 2.2 MEDIUM risk data

| Category                     | DB tables           | Examples                                 |
|:---------------------------- |:------------------- |:---------------------------------------- |
| Identity data                | PATIENTS, STAFF     | DNI/NIE, first name, surname, birth date  |
| Contact data                 | PATIENTS, STAFF     | Phone, email, address                     |
| Employment data              | STAFF               | Position, shift, certifications           |
| Financial data               | PHARMACY_DISPENSATIONS | Total amount, unit price              |

### 2.3 LOW risk data

| Category                 | DB tables           | Examples                             |
|:------------------------ |:------------------- |:------------------------------------ |
| Internal user data       | APP_USERS           | Username, role (no password)         |
| Audit metadata           | AUDIT_LOGS          | Timestamps, action type, IP (anonymisable) |

## 3. Applied Security Measures

### 3.1 Technical measures

| Measure                    | Implementation                                                         |
|:-------------------------- |:--------------------------------------------------------------------- |
| **Access control (RBAC)**  | 5 DB roles (`app_admin`, `app_doctor`, `app_nurse`, `app_receptionist`, `app_staff`) with granular table and column permissions (`scripts/sql/security.sql`) |
| **Strong authentication**  | Passwords hashed with bcrypt + JWT tokens per session                   |
| **Encryption in transit**  | TLS configured for PostgreSQL; optional mTLS for the API               |
| **Row-level security**     | RLS policies on PATIENTS and ADMISSIONS to restrict visibility based on role and user |
| **Data minimisation**      | `patient_directory` view for `app_staff` (name + room); column grants limit access |
| **Access auditing**        | 8 `AFTER INSERT/UPDATE/DELETE` triggers that automatically log to AUDIT_LOGS: table, user, action, timestamp, before/after values |
| **Concurrency control**    | `check_surgery_overlap()` trigger prevents double-booking of operating theaters |
| **Encrypted backups**      | `backup_database.py` script with daily copies, 5-day local retention + replication to standby |
| **Secure communications**  | PostgreSQL with mandatory SSL; certificates renewed automatically (`check_cert_expiry.sh`) |
| **Secret isolation**       | Environment variables for DB credentials, JWT secret, and external API; `.env` files excluded from repository |

### 3.2 Organisational measures

| Measure                     | Description                                                            |
|:-------------------------- |:-------------------------------------------------------------------- |
| **User training**           | User and administrator manuals available                             |
| **Breach procedure**        | Document with detection, containment, assessment and notification phases |
| **Activity log**            | Session log with development traceability                            |
| **Version control**         | Git repository with versioned deployments                            |

## 4. Residual Risks and Additional Measures

| Risk                          | Additional measure planned                                           |
|:----------------------------- |:------------------------------------------------------------------- |
| Access by unauthorised staff  | RLS + column-level grants + audit logging on all accesses           |
| Communication interception    | TLS on all external connections                                     |
| Data loss                     | Daily backups + hot standby (streaming replication)                 |
| Personal data breach          | Notification plan to AGPD within 72h per GDPR Art. 33              |
| SQL injection                 | ORM (SQLAlchemy) with parameterised queries                         |

## 5. ARSULIPO Rights Exercise (LOPDGDD / GDPR)

The system supports the following rights:

| Right               | Mechanism                                                        |
|:------------------- |:--------------------------------------------------------------- |
| Access              | Patient history queries (`/api/reports/patient-history`)         |
| Rectification       | Patient data CRUD from the maintenance module                    |
| Erasure             | Logical deletion with `is_active`; irreversible erasure pending approval |
| Restriction         | Possible through restricted roles and RLS                        |
| Portability         | XML/JSON export with schema (`visits.xsd` / `visits.schema.json`) |
| Objection           | Recordable via administrative request                            |

## 6. Retention Policy

| Data type                | Retention                                              |
|:------------------------ |:---------------------------------------------------- |
| Clinical history         | 15 years from last activity                           |
| Employment records       | 7 years after departure                               |
| Audit logs               | 2 years in primary + 7 years compressed               |
| Backups                  | 5 rotating daily + 12 weekly + 12 monthly             |

## 7. Declaration of Conformity

This document has been prepared following the guidelines of **LOPDGDD 3/2018** and **GDPR (EU) 2016/679**. The implemented security measures cover the project requirements for Hospital de Blanes, pending external audit for actual production use.
