# Project Documentation

## Purpose

This directory contains the project documentation for the Hospital Management System. Documentation is organized by governance, planning, data architecture, security and infrastructure, and operations manuals. See `docs/DOCUMENTATION_AUDIT.md` for an audit and the proposed restructuring plan. The generated table of contents is `docs/99_Index/TOC.md`.

## Information Architecture

### `00_Governance`

- `Documentation_Backlog.md`: status of documentation completion.
- `Project_Session_Log.md`: historical record of project work sessions.
- `Reference_Sources.md`: authoritative sources used to support technical and regulatory decisions.

### `01_Planning`

- `Architecture_Overview.md`: high-level system architecture.
- `Functional_Requirements.md`: detailed functional scope and requirements.
- `Non_Functional_Requirements.md`: performance, security, and quality requirements.
- `System_Context_Diagram.md`: system boundaries and external interfaces.
- `Tech_Stack.md`: approved technology baseline and selection rationale.

### `02_Data_Architecture`

- `Access_Control_Matrix.md`: RBAC baseline for data and module access.
- `Data_Dictionary.md`: concise definition of the principal data structures.
- `Database_Standards.md`: design standards and conventions.
- `Relational_Model.md`: logical model of the system entities and relationships.

### `03_Security_and_Infrastructure`

- `Data_Protection_and_GDPR_Compliance.md`: privacy and compliance baseline.
- `Deployment_Architecture.md`: deployment strategies and environments.
- `High_Availability_and_Backup_Strategy.md`: resilience and recovery planning.
- `Network_Architecture.md`: network design and connectivity.
- `TLS_and_mTLS_Configuration.md`: transport security baseline.
- `Secrets_Management.md` (missing): referenced guidance for secret handling is not present and will be added as part of the restructuring plan.

### `04_Operations_and_Manuals`

- `Administrator_Manual.md`: administrative operations and user management.
- `Backup_and_Restore_Runbook.md`: backup and recovery procedures.
- `Incident_Response_Procedure.md`: incident handling and response.
- `Installation_Guide.md`: setup and installation instructions.
- `User_Manual.md`: end-user workflows and operations.

## Naming Convention

- Folders use ordered prefixes to preserve reading sequence.
- Files use descriptive PascalCase names with underscores for readability.
- Each document should include purpose, status, and related-document references where useful.

## How to contribute

- When you add or update a document, update `docs/00_Governance/Documentation_Backlog.md` with status and reviewer assignment.
- Prefer creating a focused document per concern rather than mixing concerns.
- Use the `Document Control` table at the top of each file and keep the `Status` and `Last Updated` fields current.
- For editorial changes, open a pull request with a short summary of the edits and the affected documents.

## Maintenance Guidelines

- Prefer one document per concern.
- Avoid mixing strategic planning with step-by-step procedures.
- Add new documents to the relevant section instead of expanding unrelated files.
- Update `Documentation_Backlog.md` when a missing document is identified or created.
