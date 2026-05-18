# Database Standards

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 1.0          |
| Last Updated   | 2026-05-04   |

## Purpose

Provide database design, naming, integrity, and maintenance standards to keep the HMS schema consistent and maintainable.

## Scope

These standards apply to:

- Tables
- Columns
- Primary and foreign keys
- Constraints
- Indexes
- Audit-related structures
- SQL schema scripts
- Future schema evolution
- 
## General Principles

- The PostgreSQL database is the system of record for hospital operational data.
- Database design must preserve referential integrity and domain consistency.
- Clinical and administrative data should remain clearly separated by domain.
- Sensitive data structures must support auditability and access control.
- Schema growth must favor clarity and predictability over shorthand or ad hoc naming.

## Naming Standards

### Tables

- Use uppercase snake case for table names.
- Prefer plural nouns for entity tables.
- Use descriptive business names instead of abbreviations when possible.
- Use dedicated junction table names for many-to-many relationships.

Examples:

- `PATIENTS`
- `APP_USERS`
- `MEDICAL_STAFF_SPECIALTIES`
- `SURGERY_ASSISTANTS`

### Columns

- Use lowercase snake case for column names.
- Primary key columns should follow the `<entity>_id` pattern.
- Foreign key columns should use the same name as the referenced primary key.
- Boolean columns should read naturally as true/false states.
- Timestamp and date columns should be explicit about meaning.

Examples:

- `patient_id`
- `assigned_floor_id`
- `is_active`
- `created_at`
- `visit_timestamp`

### Constraints and Indexes

- Use explicit, descriptive names when custom naming is required.
- Prefix indexes with `idx_`.
- Prefix unique constraints with `uq_` when explicitly named.
- Prefix check constraints with `chk_` when explicitly named.
- Prefix foreign keys with `fk_` when explicit naming is introduced in future migrations.

Examples:

- `idx_patients_last_name`
- `uq_staff_specialty`
- `chk_surgery_time_range`

## Table Design Standards

### Primary Keys

- Every business table must have a primary key.
- Use surrogate integer keys for primary identifiers.
- `SERIAL` is acceptable for the current project scope.
- Junction tables may use either a surrogate key plus uniqueness constraint or a composite primary key when justified by the relationship.

Current examples:

- `PATIENTS.patient_id`
- `APP_USERS.user_id`
- `SURGERY_ASSISTANTS (surgery_id, nurse_id)`

### Foreign Keys

- All relationship-bearing columns must be defined with foreign key constraints.
- Delete behavior must be explicitly chosen based on business semantics.
- Use `ON DELETE CASCADE` only when child rows have no meaning without the parent.
- Use `ON DELETE RESTRICT` when data removal should be blocked to protect historical integrity.
- Use `ON DELETE SET NULL` when the relationship is optional and the child row remains valid without the parent.

Current patterns:

- `CASCADE`: dependent children such as `DISPENSATION_ITEMS`
- `RESTRICT`: clinically or operationally sensitive references such as `SURGERIES -> OPERATING_THEATERS`
- `SET NULL`: optional assignments such as `NURSING_STAFF.assigned_floor_id`

### Required vs Optional Columns

- Mark mandatory business fields as `NOT NULL`.
- Optional data should remain nullable unless a safe default is semantically correct.
- Avoid assigning defaults that hide missing business information.

Examples:

- `username` is required
- `actual_discharge_date` is optional
- `is_active` can safely default to `TRUE`

## Data Type Standards

### Identifiers

- Use integer-based identifiers for internal relational keys.
- Use `VARCHAR` for external identifiers such as national IDs, licenses, and usernames.

### Textual Data

- Use `VARCHAR(n)` for bounded text with clear size expectations.
- Use `TEXT` for unbounded descriptive or narrative content.

Examples:

- `VARCHAR(100)` for `first_name`
- `TEXT` for `notes`, `curriculum`, `radiologist_report`

### Date and Time

- Use `DATE` for date-only fields.
- Use `TIME` for time-only fields.
- Use `TIMESTAMP` for event records and audit fields.
- Defaults such as `CURRENT_TIMESTAMP` should be used for creation or event moments, not for business dates that must be intentionally provided.

### Numeric and Financial Data

- Use `INTEGER` for counters and discrete quantities.
- Use `DECIMAL(p, s)` for financial amounts.
- Always add non-negative checks to monetary or quantity fields where appropriate.

Examples:

- `quantity INTEGER CHECK (quantity > 0)`
- `total_cost DECIMAL(10, 2) CHECK (total_cost >= 0)`

### Enumerated Business Values

- Use `CHECK` constraints for controlled value lists in the current schema style.
- Controlled values must be uppercase and semantically stable.
- If value sets grow significantly, consider moving them to reference tables in future iterations.

Examples:

- `staff_type IN ('MEDICAL', 'NURSING', 'GENERAL')`
- `status IN ('REQUESTED', 'SCHEDULED', 'COMPLETED', 'CANCELLED')`

## Constraint Standards

### Uniqueness

- Use `UNIQUE` constraints for natural identifiers or business keys that must not repeat.
- Apply uniqueness only when duplication is truly invalid at the business level.

Examples:

- `STAFF.national_id`
- `APP_USERS.username`
- `MEDICAL_STAFF.license_number`

### Check Constraints

- Use `CHECK` constraints to enforce local domain rules close to the data.
- Keep check expressions readable and business-relevant.

Examples:

- `quantity > 0`
- `end_time > start_time`
- `actual_discharge_date >= DATE(admission_date) OR actual_discharge_date IS NULL`

### Referential Integrity

- Foreign keys must be present for all modeled relationships.
- Application logic must not replace database-enforced referential integrity.

## Indexing Standards

- Create indexes for foreign keys used in joins.
- Create indexes for frequently filtered business columns.
- Create indexes for status, timestamp, and date fields used in operational queries.
- Avoid redundant indexes on columns already covered by primary keys or unique indexes unless query behavior justifies them.
- Index names should clearly state table and column intent.

Current examples:

- `idx_visits_patient_id`
- `idx_appointments_date`
- `idx_audit_logs_timestamp`

## Audit and Security Standards

- Sensitive operational actions must be traceable through dedicated audit structures.
- Audit tables must preserve time, actor, action type, and target context.
- Security-relevant fields such as password hashes must never be stored in plaintext.
- Access-related tables must support role-based authorization.
- Sensitive derived authentication artifacts outside the main schema must be documented and reviewed separately.

Current audit example:

- `AUDIT_LOGS` stores user, action type, time, target table, and before/after data fields.

## Documentation Standards for Database Objects

- All business tables should include `COMMENT ON TABLE` metadata.
- Future schema extensions should add comments for especially sensitive or non-obvious columns.
- Database documentation must remain aligned with:
  - `docs/02_Data_Architecture/Relational_Model.md`
  - `docs/02_Data_Architecture/Data_Dictionary.md`
  - `docs/02_Data_Architecture/Access_Control_Matrix.md`

## Script Organization Standards

- Keep schema definition scripts separate from security, data seeding, and operational scripts.
- Use section headers in SQL files for readability.
- Order DDL scripts so referenced parent tables are created before child tables.
- Place indexes after table creation unless a migration tool requires another pattern.
- Keep documentation comments near the end of the schema script or in a dedicated metadata section.

Current expected separation:

- `scripts/sql/schema.sql`: structure and indexes
- `scripts/sql/security.sql`: roles, privileges, and security-related SQL

## Schema Evolution Standards

- New tables must follow established naming, key, and documentation conventions.
- New relationships must explicitly define delete behavior.
- New status or role-like controlled values must be justified and kept consistent across code and database layers.
- Schema changes should preserve backward traceability with documentation updates.
- Future production-oriented evolution should adopt a migration tool rather than relying only on `db.create_all()`.

## Design Patterns Used in the Current Schema

| Pattern                         | Current Usage                                                      |
|:------------------------------- |:------------------------------------------------------------------ |
| Base entity with subtype tables | `STAFF` with `MEDICAL_STAFF`, `NURSING_STAFF`, and `GENERAL_STAFF` |
| Junction table for many-to-many | `MEDICAL_STAFF_SPECIALTIES`, `SURGERY_ASSISTANTS`                  |
| Audit table                     | `AUDIT_LOGS`                                                       |
| Catalog/reference table         | `MEDICAL_SPECIALTIES`, `MEDICATIONS`, `FLOORS`                     |
| Header-detail structure         | `PHARMACY_DISPENSATIONS` and `DISPENSATION_ITEMS`                  |

## Standards for Future Additions

When adding a new table, the minimum checklist is:

- Define a primary key.
- Define all foreign keys with explicit delete behavior.
- Mark mandatory columns as `NOT NULL`.
- Add `UNIQUE` constraints where required by business rules.
- Add `CHECK` constraints for bounded domain values.
- Add indexes for foreign keys and expected query filters.
- Add a table comment.
- Update the relational model and data dictionary documents.

## Known Improvement Areas

- Explicit naming of all constraints can be improved in future schema revisions.
- `SERIAL` may later be replaced with `GENERATED ... AS IDENTITY` for newer PostgreSQL conventions.
- Column-level comments are not yet systematically applied.
- Schema migrations are not yet managed through a formal migration workflow.

