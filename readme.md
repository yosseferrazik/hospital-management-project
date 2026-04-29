![Hospital](https://imagenes.elpais.com/resizer/v2/AFAITZ3H6DI4FMKGYEDGKNPBNM.jpg?auth=bf9cdc39c32a763812ec3172ab6d8ca422787358ebb01637b93f2f17246b4b51&width=1960&height=1103&smart=true "Hospital")
# Hospital Sa Palomera
> This repository contains the intermodular project for the **ASIX program (Institut Sa Palomera)**. The project combines database design, Python development, and infrastructure planning for a hospital management platform.

## Project Overview & Objectives
Due to significant population growth in the areas of Blanes and Lloret, **Hospital Sa Palomera** is facing the transition from an obsolete paper-based management model to a modern digital system. This project designs and implements a software solution to support medical, administrative, and operational workflows.

The main purpose of the platform is to replace manual record-keeping with a secure and maintainable digital environment that improves data integrity, operational efficiency, and healthcare delivery.

### Key Strategic Goals:
* **Comprehensive Resource Management:** Digitalize the registration and oversight of hospital staff, patients, visits, and surgeries.
* **Operational Efficiency:** Streamline clinical workflows, scheduling, and day-to-day administrative processes.
* **Data Security & Privacy:** Protect sensitive medical information through access control, encryption, and database security measures.
* **High Availability & Reliability:** Define an infrastructure prepared for backup strategies, secure connectivity, and future scaling.
* **Interoperability Readiness:** Keep the project aligned with realistic healthcare integration and reporting needs.
* **Maintainability:** Organize code, SQL scripts, and documentation in a modular way that supports iterative development.

## Project Structure & Index
This repository is organized into focused modules for code, SQL, diagrams, and supporting documentation.

### [Documentation](./docs/)
* **[01_Planning](./docs/01_Planning/)**: Planning and technology decisions.
* **[02_Database_Design](./docs/02_Database_Design/)**: Relational model, data dictionary, and security matrix.
* **[03_Infrastructure](./docs/03_Infrastructure/)**: Infrastructure, TLS, and GDPR-related documentation.
* **[04_Manuals](./docs/04_Manuals/)**: Reserved for installation and user manuals.
* **[Session Logs](./docs/Session_Logs.md)**: Work log with dated project progress.
* **[References](./docs/References.md)**: Bibliography and technical sources used during development.

### Application Code
* **[Server](./server/README.md)**: Flask API, services, routes, authentication flow, and database integration.
* **[Client](./client/README.md)**: Tkinter desktop application used by hospital staff.

### [SQL Scripts](./sql/)
* **[Schema](./sql/schema.sql)**: Database schema definition.
* **[Security](./sql/security.sql)**: Roles, grants, and row-level security configuration.
* **[Dummy Data](./sql/dummy_data.sql)**: Initial sample data.

## Documentation Guide
```text
docs/
├── 01_Planning/
│   └── Tech_Stack.md                 # Selected technologies and rationale
│
├── 02_Database_Design/
│   ├── Relational_Model.md           # Relational design and structure
│   ├── Data_Dictionary.md            # Fields, types, and constraints
│   └── Security_Matrix.md            # Roles and permissions model
│
├── 03_Infrastructure/
│   ├── TLS_Configuration.md          # PostgreSQL TLS and certificate setup
│   └── GDPR_Compliance.md            # Privacy and compliance considerations
│
├── 04_Manuals/                       # Reserved for future manuals
│   └── README.md
│
├── References.md                     # Bibliography and technical sources
└── Session_Logs.md                   # Project work log
```

## Current Development Notes
* The project is still in progress and some modules are being actively reorganized.
* The current codebase is split into a Flask backend and a Tkinter desktop client.
* The database name used by the documentation and helper scripts is **`hospital_management`**.

## Authors
* **Yossef Errazik** - [[GitHub Profile](https://github.com/yosseferrazik)]
