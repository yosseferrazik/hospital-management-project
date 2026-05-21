# Security and Compliance

## Database roles (RBAC)

We created 5 PostgreSQL roles with granular table/column permissions defined in `scripts/sql/security.sql`:

| Role | Connection limit | What they can do |
|------|-----------------|------------------|
| `app_admin` | 5 | Full access to everything |
| `app_doctor` | 50 | CRUD on patients, visits, prescriptions, surgeries |
| `app_nurse` | 100 | Read/write limited fields on patients, manage admissions on their floor |
| `app_receptionist` | 10 | CRUD on patients, schedule appointments |
| `app_staff` | 30 | Read-only: patient name + room (via `patient_directory` view) |

## Row-Level Security (RLS)

Enabled on `PATIENTS` and `ADMISSIONS`:

- **Nurses** only see patients currently admitted to rooms on their assigned floor
- **Doctors and admins** see everything
- **General staff** only see names and room numbers via a restricted view

This was tricky to set up because the session variables (`app.current_user_id`, `app.current_staff_id`) need to be set at application level before any query runs. We set them in the Flask login handler using `SET_CONFIG`.

## SSL configuration

PostgreSQL is configured with SSL using self-signed certificates generated with OpenSSL. The certificate expires in 1 year and we have a script (`scripts/ops/check_cert_expiry.sh`) that checks if renewal is needed. The `pg_hba.conf` requires `hostssl` for all remote connections.

Certificate generation and detailed TLS configuration are documented in [high_availability.md](./high_availability.md) (TLS/SSL section) and [installation_guide.md](../04_deployment/installation_guide.md) (section 3, certificate generation).

## Data masking

We use column-level grants to restrict sensitive data:

| Role | Can see |
|------|---------|
| Doctors | Full patient records |
| Nurses | Limited columns (phone, email, address, allergies — but not national_id) |
| General staff | Only name + current room (via `patient_directory` view) |

For production, we would add the `anon` PostgreSQL extension for proper dynamic masking, but within the scope of this project the column grants + RLS were sufficient.

## AGPD compliance

We prepared a separate document for the Spanish Data Protection Agency covering:

- Data categories and risk levels (see table below)
- Applied security measures (RBAC, SSL, RLS, audit, encryption)
- Data subject rights (ARSULIPO)
- Retention policies

Full document: [`agpd_compliance.md`](./agpd_compliance.md)

## Data classification

| Category | Examples | Risk |
|----------|----------|------|
| Clinical data | Diagnoses, surgeries, prescriptions | **Critical** |
| Identity data | DNI/NIE, name, birth date, health card | **High** |
| Contact data | Phone, email, address | Medium |
| Employment | Staff records, licenses | Medium |
| Audit metadata | User actions, timestamps, IPs | High |

## Audit logging

8 database triggers automatically log all INSERT/UPDATE/DELETE operations on sensitive tables (`PATIENTS`, `VISITS`, `PRESCRIPTIONS`, `ADMISSIONS`, `SURGERIES`, `RADIOLOGY_EXAMS`, `PHARMACY_DISPENSATIONS`, `SCHEDULED_APPOINTMENTS`) into the `AUDIT_LOGS` table. Each entry records: user, timestamp, action type, table name, record ID, old data (JSON), and new data (JSON).

## What went wrong at first

- We initially forgot to set `SECURITY DEFINER` on the audit helper functions, which caused permission errors when triggers fired
- The nurse RLS policy was too restrictive at first — nurses couldn't see patients they had previously treated. We had to add the condition for currently admitted patients only
