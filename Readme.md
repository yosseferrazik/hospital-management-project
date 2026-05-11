![Hospital](https://imagenes.elpais.com/resizer/v2/AFAITZ3H6DI4FMKGYEDGKNPBNM.jpg?auth=bf9cdc39c32a763812ec3172ab6d8ca422787358ebb01637b93f2f17246b4b51&width=1960&height=1103&smart=true "Hospital")

# Hospital Sa Palomera

> This repository contains the intermodular project for the **ASIX program (Institut Sa Palomera)**. The project combines database design, Python development, and infrastructure planning for a hospital management platform.

## Project Overview & Objectives

Due to significant population growth in the areas of Blanes and Lloret, **Hospital Sa Palomera** is facing the transition from an obsolete paper-based management model to a modern digital system. This project designs and implements a software solution to support medical, administrative, and operational workflows.

The main purpose of the platform is to replace manual record-keeping with a secure and maintainable digital environment that improves data integrity, operational efficiency, and healthcare delivery.

### Key Strategic Goals

* **Comprehensive Resource Management:** Digitalize the registration and oversight of hospital staff, patients, visits, and surgeries.
* **Operational Efficiency:** Streamline clinical workflows, scheduling, and day-to-day administrative processes.
* **Data Security & Privacy:** Protect sensitive medical information through access control, encryption, and database security measures.
* **High Availability & Reliability:** Define an infrastructure prepared for backup strategies, secure connectivity, and future scaling.
* **Interoperability Readiness:** Keep the project aligned with realistic healthcare integration and reporting needs.
* **Maintainability:** Organize code, SQL scripts, and documentation in a modular way that supports iterative development.

## Project Structure & Index

This repository is organized into focused modules for code, SQL, diagrams, and supporting documentation.

For a consolidated documentation index and audit, see `docs/99_Index/TOC.md` and `docs/DOCUMENTATION_AUDIT.md`.

Operational helper scripts are available in `scripts/ops/` (monitoring and maintenance helpers such as check_replication.sh and check_cert_expiry.sh).

### [Documentation](./docs/)

* **[00_Governance](./docs/00_Governance/)**: Documentation control and project management.
* **[01_Planning](./docs/01_Planning/)**: Planning and technology decisions.
* **[02_Data_Architecture](./docs/02_Data_Architecture/)**: Relational model, data dictionary, and security matrix.
* **[03_Security_and_Infrastructure](./docs/03_Security_and_Infrastructure/)**: Infrastructure, TLS, GDPR, and deployment.
* **[04_Operations_and_Manuals](./docs/04_Operations_and_Manuals/)**: Installation, user, and administrator manuals.

### Application Code

* **[Server](./server/README.md)**: Flask API with 20+ routes, services, authentication (JWT), and database integration.
* **[Client](./client/README.md)**: Tkinter desktop application with 10 views for staff management, patient intake, queries, and resource browsing.

### [SQL Scripts](./sql/)

* **[Schema](./sql/schema.sql)**: Database schema with 25 tables.
* **[Security](./sql/security.sql)**: Roles, grants, and row-level security configuration.

## Documentation Guide

```text
docs/
├── 00_Governance/
│   ├── Documentation_Backlog.md       # Pending documentation items
│   ├── Project_Session_Log.md         # Work log with dated progress
│   └── Reference_Sources.md           # Bibliography and technical sources
│
├── 01_Planning/
│   ├── Architecture_Overview.md       # System architecture
│   ├── Functional_Requirements.md     # Feature specifications
│   ├── Non_Functional_Requirements.md # Performance and security reqs
│   ├── System_Context_Diagram.md      # System boundaries
│   └── Tech_Stack.md                  # Selected technologies and rationale
│
├── 02_Data_Architecture/
│   ├── Access_Control_Matrix.md       # Roles and permissions
│   ├── Data_Dictionary.md             # Fields, types, and constraints
│   ├── Database_Standards.md          # Design standards
│   └── Relational_Model.md            # Relational design and structure
│
├── 03_Security_and_Infrastructure/
│   ├── Data_Protection_and_GDPR_Compliance.md # Privacy compliance
│   ├── Deployment_Architecture.md     # Deployment strategies
│   ├── High_Availability_and_Backup_Strategy.md # HA and backups
│   ├── Network_Architecture.md        # Network design
│   ├── Secrets_Management.md          # Secret handling
│   └── TLS_and_mTLS_Configuration.md  # TLS setup
│
├── 04_Operations_and_Manuals/
│   ├── Administrator_Manual.md        # Admin operations
│   ├── Backup_and_Restore_Runbook.md  # Backup procedures
│   ├── Replication_and_HA_Runbook.md  # Replication and failover procedures
│   ├── Incident_Response_Procedure.md # Incident handling
│   ├── Installation_Guide.md          # Setup instructions
│   └── User_Manual.md                 # End-user guide
│
└── README.md                          # Documentation overview
```

## Current Development Notes

* The project implements a comprehensive hospital management system with full CRUD operations for 25+ entities.
* Backend provides 20+ API routes with JWT authentication and role-based access (tokens issued, enforcement planned).
* Client desktop application includes 10 views for authentication, maintenance, queries, dashboard, and resource management.
* Database schema supports staff inheritance, clinical workflows, pharmacy, and diagnostics.
* Infrastructure documentation is complete; implementation focuses on development environment with plans for HA and TLS.
* Manuals for installation, user operations, and administration are available in docs/04_Operations_and_Manuals/.
* The database name used is **`hospital_management`**.
* Canonical operational runbooks for backups and replication have been consolidated into `docs/04_Operations_and_Manuals/`.
* Operational helper scripts are stored in `scripts/ops/` for monitoring and scheduled checks.

## Authors

* **Yossef Errazik** - [[GitHub Profile](https://github.com/yosseferrazik)]
