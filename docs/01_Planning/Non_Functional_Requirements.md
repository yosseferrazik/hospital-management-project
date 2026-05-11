# Non-Functional Requirements

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 1.0          |
| Last Updated   | 2026-05-04   |

## Purpose

Specify the non-functional quality attributes, operational constraints, and engineering standards that support the HMS functional scope.

## Scope

This document covers the following non-functional areas:

- Security
- Privacy and regulatory alignment
- Availability and recovery
- Performance
- Reliability and data integrity
- Maintainability
- Scalability
- Usability
- Compatibility
- Observability and auditability

## Non-Functional Requirements

### Security

| ID      | Requirement                                                                                                                             |
|:------- |:--------------------------------------------------------------------------------------------------------------------------------------- |
| NFR-001 | The system shall require authentication before allowing access to protected operational features.                                       |
| NFR-002 | The system shall store user passwords in hashed form and shall not store plaintext passwords in the database.                           |
| NFR-003 | The system shall use token-based authentication for protected API routes.                                                               |
| NFR-004 | The system shall externalize sensitive runtime configuration such as database connection strings, encryption keys, and JWT secrets.     |
| NFR-005 | The solution shall prevent sensitive credentials and certificate material from being hardcoded in source files.                         |
| NFR-006 | The target deployment architecture shall support encrypted communications between system components through TLS or mTLS where required. |

### Privacy and Compliance

| ID      | Requirement                                                                                                                                                          |
|:------- |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NFR-007 | The system shall be designed to support GDPR-aligned handling of personal and clinical data.                                                                         |
| NFR-008 | The system shall apply least-privilege access principles to protected data and operational workflows.                                                                |
| NFR-009 | The system shall minimize unnecessary exposure of sensitive patient and staff data in the user interface and service responses.                                      |
| NFR-010 | The system shall support future implementation of data subject rights workflows, including access, rectification, portability, and erasure where legally applicable. |

### Availability and Recovery

| ID      | Requirement                                                                                                    |
|:------- |:-------------------------------------------------------------------------------------------------------------- |
| NFR-011 | The target solution shall support daily database backup procedures.                                            |
| NFR-012 | The target solution shall support restoration of the full database from backup.                                |
| NFR-013 | The target solution shall preserve backup copies outside the main runtime environment.                         |
| NFR-014 | The planned infrastructure shall support future failover or standby recovery mechanisms for the database tier. |

### Performance

| ID      | Requirement                                                                                                                                   |
|:------- |:--------------------------------------------------------------------------------------------------------------------------------------------- |
| NFR-015 | The desktop client shall provide a responsive user experience for normal maintenance operations under local or lab deployment conditions.     |
| NFR-016 | The API shall return standard maintenance-operation responses within an acceptable interactive time for normal academic-project usage.        |
| NFR-017 | Date-based operational queries shall be suitable for interactive consultation from the desktop client.                                        |
| NFR-018 | Bulk dummy-data generation may run longer than standard user actions, but the operation shall complete without compromising data consistency. |

### Reliability and Data Integrity

| ID      | Requirement                                                                                                             |
|:------- |:----------------------------------------------------------------------------------------------------------------------- |
| NFR-019 | The database layer shall remain the system of record for hospital operational data.                                     |
| NFR-020 | The system shall preserve referential integrity between related domain entities.                                        |
| NFR-021 | The system shall reject invalid protected requests when authentication context is missing or invalid.                   |
| NFR-022 | The system shall return explicit success or error responses for client-triggered operations.                            |
| NFR-023 | The system shall use structured persistence models so that domain entities remain consistent across application layers. |

### Maintainability

| ID      | Requirement                                                                                                            |
|:------- |:---------------------------------------------------------------------------------------------------------------------- |
| NFR-024 | The codebase shall maintain separation between presentation, routing, service logic, and persistence concerns.         |
| NFR-025 | The backend shall keep business logic outside route handlers whenever practical.                                       |
| NFR-026 | Project documentation shall be maintained as a structured and versioned part of the repository.                        |
| NFR-027 | The system design shall allow new modules or workflows to be added without requiring a complete architectural rewrite. |
| NFR-028 | Configuration values shall be changeable per environment without modifying business logic source files.                |

### Scalability

| ID      | Requirement                                                                                                                              |
|:------- |:---------------------------------------------------------------------------------------------------------------------------------------- |
| NFR-029 | The architecture shall support growth from local development usage toward multi-service deployment patterns.                             |
| NFR-030 | The persistence model shall support expansion into additional hospital domains such as admissions, prescriptions, billing, or inventory. |
| NFR-031 | The backend architecture shall support the introduction of more granular authorization rules in future iterations.                       |
| NFR-032 | The infrastructure design shall support future horizontal redundancy for application services.                                           |

### Usability

| ID      | Requirement                                                                                              |
|:------- |:-------------------------------------------------------------------------------------------------------- |
| NFR-033 | The client application shall provide a clear desktop navigation flow from login to operational features. |
| NFR-034 | The client application shall provide immediate visual feedback for successful and failed user actions.   |
| NFR-035 | Input forms shall clearly indicate the primary fields required to complete registration workflows.       |
| NFR-036 | Operational query screens shall present results in a readable tabular format for end users.              |

### Compatibility and Portability

| ID      | Requirement                                                                                              |
|:------- |:-------------------------------------------------------------------------------------------------------- |
| NFR-037 | The system shall operate within a Python-based runtime for both client and server components.            |
| NFR-038 | The backend shall remain compatible with PostgreSQL as its primary relational database engine.           |
| NFR-039 | The desktop client shall remain compatible with environments where `tkinter` is available.               |
| NFR-040 | The application shall support local development and lab execution using environment-based configuration. |

### Observability and Auditability

| ID      | Requirement                                                                                                                    |
|:------- |:------------------------------------------------------------------------------------------------------------------------------ |
| NFR-041 | The solution shall support traceability of sensitive operations through audit-oriented data structures and logging mechanisms. |
| NFR-042 | The architecture shall support future expansion of audit logging for protected clinical and administrative actions.            |
| NFR-043 | The system shall preserve enough operational feedback to diagnose common request failures during development and testing.      |

## Quality Targets

The following targets reflect intended quality expectations for the current project stage:

| Area                      | Target                                                                             |
|:------------------------- |:---------------------------------------------------------------------------------- |
| Authentication protection | All maintenance and dummy-data routes require authenticated access                 |
| Configuration management  | Secrets and connection settings loaded from environment variables                  |
| Backup frequency          | Daily backup strategy in the target design                                         |
| Client responsiveness     | Interactive actions should feel immediate under normal local/lab usage             |
| Documentation quality     | Core planning, architecture, security, and data documents maintained in repository |

## Current Constraints and Gaps

The following non-functional limitations are known at the current stage:

- Route-level authorization is not yet fully role-aware.
- Transport security is documented but not yet enforced in the current local runtime flow.
- Database migrations are not yet managed through a dedicated migration tool.
- The client API base URL is still hardcoded.
- The encrypted local credential file adds operational complexity that should be reviewed.

## Traceability to Existing Documentation

| Topic                  | Supporting Documents                                                           |
|:---------------------- |:------------------------------------------------------------------------------ |
| Functional scope       | `docs/01_Planning/Functional_Requirements.md`                                  |
| Architecture           | `docs/01_Planning/Architecture_Overview.md`                                    |
| Technology baseline    | `docs/01_Planning/Tech_Stack.md`                                               |
| Access control         | `docs/02_Data_Architecture/Access_Control_Matrix.md`                           |
| Privacy and compliance | `docs/03_Security_and_Infrastructure/Data_Protection_and_GDPR_Compliance.md`   |
| Transport security     | `docs/03_Security_and_Infrastructure/TLS_and_mTLS_Configuration.md`            |
| Recovery planning      | `docs/03_Security_and_Infrastructure/High_Availability_and_Backup_Strategy.md` |
