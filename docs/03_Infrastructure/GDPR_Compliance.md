# 📋 Security Documentation for APDCAT Audit (GDPR Compliance)

> This document identifies the types of personal data processed by the Hospital Management System of **Hospital Sa Palomera**, classifies them according to the GDPR, and details the technical and organizational security measures implemented to ensure confidentiality, integrity, and availability.

## 1. Data Controller Information

| Field                         | Value                                                                 |
|:------------------------------|:----------------------------------------------------------------------|
| **Data Controller**           | Hospital Sa Palomera                                                  |
| **Tax ID (NIF)**              | F-12345678 (Fictional)                                                |
| **Address**                   | Carrer de la Salut, 15, 08001 Barcelona, Spain                        |
| **Data Protection Officer**   | Yossef Errazik - [dpo@hospital-sapalomera.cat](mailto:dpo@hospital-sapalomera.cat) |
| **System Name**               | Hospital Management System (HMS)                                      |

## 2. Identification and Classification of Personal Data

In accordance with the **General Data Protection Regulation (GDPR) 2016/679** and Spanish **Organic Law 3/2018 (LOPDGDD)** , the data processed by the system is classified as follows.

### 2.1. Patient Data (`PATIENTS` Table)

| Field                                   | Data Type (GDPR)              | Special Category (Art. 9 GDPR)        | Risk Level |
|:----------------------------------------|:------------------------------|:--------------------------------------|:-----------|
| `national_id` (DNI/Passport)            | Identification                | No                                    | High       |
| `first_name`, `last_name`               | Identification                | No                                    | Medium     |
| `birth_date`                            | Identification                | No                                    | Medium     |
| `gender`                                | Personal Characteristics      | No                                    | Low        |
| `phone`, `email`, `address`             | Contact / Location            | No                                    | Medium     |
| `emergency_contact_name`, `..._phone`   | Third-Party Contact Data      | No                                    | Medium     |
| `blood_type`                            | **Health Data**               | **Yes (Art. 9.1)**                    | **High**   |
| `allergies`                             | **Health Data**               | **Yes (Art. 9.1)**                    | **High**   |

### 2.2. Clinical and Healthcare Data

| Table(s)                                | Data Type (GDPR)              | Special Category (Art. 9 GDPR)        | Risk Level |
|:----------------------------------------|:------------------------------|:--------------------------------------|:-----------|
| `VISITS` (`diagnosis`, `notes`)         | **Health Data**               | **Yes (Art. 9.1)**                    | **High**   |
| `PRESCRIPTIONS` (medication, dosage)    | **Health Data**               | **Yes (Art. 9.1)**                    | **High**   |
| `ADMISSIONS` (admissions, discharges)   | **Health Data**               | **Yes (Art. 9.1)**                    | **High**   |
| `SURGERIES` (`procedure_type`, `notes`) | **Health Data**               | **Yes (Art. 9.1)**                    | **High**   |
| `RADIOLOGY_EXAMS` (`exam_type`, report) | **Health Data**               | **Yes (Art. 9.1)**                    | **High**   |

### 2.3. Staff Data (Medical and Non-Medical) (`STAFF` Table)

| Field                                   | Data Type (GDPR)              | Special Category (Art. 9 GDPR)        | Risk Level |
|:----------------------------------------|:------------------------------|:--------------------------------------|:-----------|
| `national_id`, `first_name`, `last_name`| Identification                | No                                    | Medium     |
| `birth_date`                            | Identification                | No                                    | Medium     |
| `phone`, `email`, `address`             | Contact / Location            | No                                    | Medium     |
| `ssn` (Social Security Number)          | Identification (Affiliation)  | No                                    | High       |
| `license_number` (Professional License) | Professional Identification   | No                                    | Medium     |
| `curriculum`, `certifications`          | Career / Training Data        | No                                    | Low        |

### 2.4. Application Users and Audit Data

| Table                                   | Data Type (GDPR)              | Special Category (Art. 9 GDPR)        | Risk Level |
|:----------------------------------------|:------------------------------|:--------------------------------------|:-----------|
| `APP_USERS` (`username`, `last_login`)  | Identification / Monitoring   | No                                    | Medium     |
| `AUDIT_LOGS` (`ip_address`, actions)    | **Traffic / Monitoring Data** | **May reveal health data (context)**  | **High**   |

> **Note on `AUDIT_LOGS`:** Although it stores metadata, the context of the action (`table_name` = `patients`, `surgeries`) and the old/new data snapshots (`old_data`, `new_data`) may contain **special categories of data**. Therefore, this table receives the same level of protection as clinical data.

## 3. Technical Security Measures Applied

The following measures are implemented across the system layers to ensure information security, in accordance with the **Spanish National Security Framework (ENS)** at **HIGH** level and GDPR Articles 25 and 32.

### 3.1. Database Layer (PostgreSQL)

| Measure                                 | Technical Implementation                                                                                                    | Justification / Standard              |
|:----------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|:--------------------------------------|
| **Encryption in Transit (mTLS)**        | Connection between Flask API and PostgreSQL uses TLS 1.2+ with mutual authentication via client/server certificates.        | GDPR Art. 32.1.a (Encryption)         |
| **Role-Based Access Control (RBAC)**    | Database roles (`app_api`) with least privilege. Permissions revoked from `PUBLIC`.                                         | GDPR Art. 25.2 (Minimization)         |
| **Row-Level Security (RLS)**            | RLS policies on `PATIENTS` and `ADMISSIONS` restrict nurse access only to patients in rooms on their assigned floor.        | GDPR Art. 25.1 (Data protection by default) |
| **Comprehensive Auditing**              | Triggers `AFTER INSERT/UPDATE/DELETE` that log all changes to sensitive tables in `AUDIT_LOGS`, including `user_id`.        | GDPR Art. 30 (Records of processing)  |
| **Encryption at Rest**                  | PostgreSQL data volume stored on a virtual disk encrypted at the hypervisor or OS level (LUKS).                             | GDPR Art. 32.1.a (Encryption)         |
| **Password Management**                 | Database passwords stored with `scram-sha-256`. Application passwords in `APP_USERS` hashed using `hashlib` (PBKDF2).       | GDPR Art. 32.1.b (Confidentiality)    |

### 3.2. Application / API Layer (Flask + Gunicorn)

| Measure                                 | Technical Implementation                                                                                                    | Justification / Standard              |
|:----------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|:--------------------------------------|
| **Strong Authentication**               | JSON Web Tokens (JWT) signed with `HS256`, stored only in memory on the client-side (Tkinter app).                         | GDPR Art. 32.1.d (Authentication)     |
| **Granular Authorization (RBAC)**       | Decorators on API endpoints that verify the role (`ADMIN`, `DOCTOR`, `NURSE`, etc.) extracted from the JWT.                 | GDPR Art. 25.2 (Least privilege)      |
| **Input Validation**                    | All requests are validated against strict schemas (Pydantic/Marshmallow) to prevent SQL injection and XSS.                  | GDPR Art. 25.1 (Data protection by default) |
| **Encryption in Transit (Client-API)**  | Flask server behind **Nginx reverse proxy** with SSL/TLS certificate (Let's Encrypt or internal CA).                        | GDPR Art. 32.1.a (Encryption)         |
| **HTTP Security Headers**               | Nginx configured to add `HSTS`, `X-Content-Type-Options`, `X-Frame-Options`, and `CSP` headers.                             | GDPR Art. 32.1.d (Best practices)     |
| **Session Management**                  | PostgreSQL session variables (`app.current_user_id`) set per connection by the API for traceability.                        | GDPR Art. 30 (Audit trail)            |

### 3.3. Infrastructure Layer (VMware + Docker)

| Measure                                 | Technical Implementation                                                                                                    | Justification / Standard              |
|:----------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|:--------------------------------------|
| **Network Isolation**                   | Internal Docker network (`hospital_net`) for container communication. PostgreSQL does not expose ports to the host.         | GDPR Art. 25.2 (Minimization)         |
| **Security Updates**                    | Base Docker images (`python:3.11-slim`, `postgres:16-alpine`) updated weekly.                                               | GDPR Art. 32.1.d (Maintenance)        |
| **Backups**                             | Daily `pg_dump` with 30-day retention, stored encrypted on external NAS storage.                                            | GDPR Art. 32.1.c (Availability)       |
| **Monitoring & Intrusion Detection**    | Centralized container logs. Automated alerts for multiple failed authentication attempts.                                   | GDPR Art. 32.2 (Incident detection)   |

## 4. Organizational Measures

| Measure                                 | Description                                                                                                                | Responsible                           |
|:----------------------------------------|:---------------------------------------------------------------------------------------------------------------------------|:--------------------------------------|
| **Privacy Policy**                      | Documentation provided to patients and staff detailing the processing of their data and their rights.                       | DPO / Management                      |
| **Staff Training**                      | Mandatory annual training session for all system users on data protection and cybersecurity.                                | HR Department                         |
| **Security Incident Management**        | Documented protocol for notifying the APDCAT within 72 hours in case of a data breach (GDPR Art. 33).                       | DPO / Security Officer                |
| **Risk Analysis (DPIA)**                | A **Data Protection Impact Assessment** has been conducted due to the high risk associated with large-scale health data processing (GDPR Art. 35). | DPO                                   |
| **Logical Access Control**              | Procedure for user creation/deletion in `APP_USERS` validated by the department head. Quarterly review of active users.     | System Administrator                  |

## 5. Compliance with Data Subject Rights

The system allows administrators or the DPO to manage requests for the exercise of rights:

| Right                  | System Functionality                                                                                                     |
|:-----------------------|:-------------------------------------------------------------------------------------------------------------------------|
| **Access**             | Export of all patient data (visits, admissions, surgeries, etc.) in a readable format (JSON/PDF).                         |
| **Rectification**      | Editing forms for patient demographic and contact data. Clinical data can only be rectified by a doctor.                  |
| **Erasure**            | Anonymization or pseudo-anonymization of `patient_id` upon "right to be forgotten" requests, maintaining legal/statistical integrity. |
| **Restriction**        | Flagging of a record as "processing restricted," preventing use except for legal claims.                                  |
| **Portability**        | Export of data in a structured, commonly used format (JSON) for transmission to another controller.                       |
| **Objection**          | Blocking of processing for specific purposes (e.g., research) if the patient requests it.                                 |

## 6. Records of Processing Activities (ROPA)

An updated Record of Processing Activities is maintained, which includes:

- **Processing Activity**: Clinical and administrative patient management.
- **Purpose**: Healthcare provision, appointment scheduling, billing, and anonymized research.
- **Legal Basis**: GDPR Art. 9.2.h (Healthcare) and explicit consent for research.
- **Data Sharing**: No data is shared with third parties without explicit consent, except as required by law (Public Health).
- **International Transfers**: None.
- **Retention Period**: Medical records kept for 15 years after patient discharge (Catalan Law 21/2000).

## 7. Annex: Audit Configuration for APDCAT Inspection

To facilitate an APDCAT inspection, the system provides:

- **Real-time Audit View**: Predefined SQL queries to display recent access to the `AUDIT_LOGS` table.
- **User Access Report**: List of all actions performed by a specific `staff_id` within a given period.
- **Patient Traceability Report**: Complete log of who has accessed or modified a specific patient's file (`patient_id`).

__________________________
**Yossef Errazik**
Data Protection Officer (DPO)
Hospital Sa Palomera
Date: April 22, 2026