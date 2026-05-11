# Data Protection and GDPR Compliance

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 2.1          |
| Last Updated   | 2026-05-06   |

## Purpose

Summarize the approach to personal data protection and GDPR-aligned safeguards for the Hospital Management System.

## Compliance Scope

The platform processes highly sensitive clinical and administrative data. As a result, privacy and security controls must be built into the design of the application, database, and infrastructure layers.

## Categories of Protected Data

| Category        | Examples                                       | Risk Level |
|:--------------- |:---------------------------------------------- |:---------- |
| Identity data   | National ID, name, birth date                  | High       |
| Contact data    | Phone, email, address                          | Medium     |
| Clinical data   | Diagnoses, prescriptions, surgeries, allergies | Critical   |
| Employment data | Staff records, licenses, internal roles        | Medium     |
| Audit metadata  | User actions, timestamps, IP addresses         | High       |

## Required Controls

- Strong authentication for internal users.
- Role-based authorization with least-privilege defaults.
- Encrypted communications between application and database layers.
- Auditability for access to sensitive records.
- Restricted handling of backups and exported datasets.
- Controlled storage of credentials and certificates outside source control.

## Organizational Measures

- Define data ownership and access approval responsibilities.
- Maintain training and awareness for users handling sensitive information.
- Document incident response expectations for confidentiality breaches.
- Keep processing activities aligned with legal and academic project scope.

## Technical Measures

| Control Area          | Expected Implementation                                      |
|:--------------------- |:------------------------------------------------------------ |
| Encryption in transit | TLS or mTLS for backend and database connectivity            |
| Access control        | RBAC at application level, reinforced by database privileges |
| Data minimization     | Limit data exposure to role-specific views and workflows     |
| Audit trail           | Capture security-relevant actions in `AUDIT_LOGS`            |
| Backup protection     | Encrypt and restrict backup access                           |
| Secrets handling      | Externalize environment variables and sensitive certificates |

## Data Subject Rights Considerations

The future solution should be prepared to support:

- Access requests

- Rectification workflows

- Erasure or anonymization where legally applicable

- Processing restriction

- Data portability for structured exports
  
  ## Retention Policy (recommended baseline)

- Patient clinical records: retain for 15 years after last activity, unless local law requires longer retention.

- Staff employment records: retain for 7 years after termination.

- Audit logs: retain 2 years in the primary system and archive compressed copies for 7 years.

- Backups: retain rolling daily backups for 14 days, weekly backups for 12 weeks, and monthly snapshots for 12 months (encrypted and stored off-site).

Adjust retention durations to meet local legal requirements and institutional policies. Implement automated purge jobs with safe-guards (soft-delete flag, approval workflow, and irreversible purge only after review).

## Breach Reporting and Escalation (summary)

- Detection: Log and alert anomalous access patterns or bulk data exports.
- Containment: Immediately revoke compromised credentials and isolate affected services.
- Assessment: Determine the scope (records affected, data categories, likely impact).
- Notification: Follow local GDPR timelines — notify supervisory authority within 72 hours if required and inform affected data subjects when there is high risk to their rights.
- Remediation: Apply corrective measures, rotate keys/certificates, and document lessons learned.