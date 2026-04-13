![Hospital](https://imagenes.elpais.com/resizer/v2/AFAITZ3H6DI4FMKGYEDGKNPBNM.jpg?auth=bf9cdc39c32a763812ec3172ab6d8ca422787358ebb01637b93f2f17246b4b51&width=1960&height=1103&smart=true "Hospital")
# 🏥 Hospital Management System | ASIX Intermodular Project
> This repository contains the complete intermodular project for the **ASIX program (Institut Sa Palomera)**. The project integrates Database Design (PostgreSQL), Programming (Python), and Infrastructure Management.

## 🔍 Project Overview & Objectives
Due to significant population growth in the areas of Blanes and Lloret, the **Hospital de Blanes** is currently facing the challenge of transitioning from an obsolete paper-based management system to a modern digital infrastructure. This project aims to design and implement a comprehensive software solution to streamline medical, administrative, and logistical operations.

The primary mission of this system is to replace manual record-keeping with a secure, high-performance digital environment that ensures data integrity and improves healthcare delivery.

### 🔑 Key Strategic Goals:
* **Comprehensive Resource Management:** Digitalize the registration and oversight of all hospital staff (medical, nursing, administrative, and maintenance) and patient records to ensure seamless coordination.
* **Operational Efficiency:** Optimize clinical workflows by automating surgical scheduling, managing operating room inventories, and linking medical teams to specific patients or hospital floors.
* **Data Security & Privacy:** Establish a robust security framework to protect sensitive medical information through advanced encryption, data masking, and strict access control, ensuring compliance with privacy standards.
* **High Availability & Reliability:** Build a resilient architecture capable of 24/7 operation, featuring automated backup systems and redundant data structures to prevent any service interruption.
* **Global Interoperability:** Enable seamless data exchange with external health authorities by standardizing medical reports for automated billing and legal reporting.
* **Advanced Analytics:** Transform raw clinical data into actionable insights through integrated reporting modules and executive dashboards for real-time monitoring of hospital performance.

## 📂 Project Structure & Index
This repository is organized into specific modules to ensure clarity and professional standards. Click on the links to navigate:

### 📑 [Documentation](./docs/)
* **[01_Planning](./docs/01_Planning/)**: Project proposal, Gantt charts, and daily session logs.
* **[02_Database_Design](./docs/02_Database_Design/)**: ER diagrams, Relational model, and Security matrix.
* **[03_Infrastructure](./docs/03_Infrastructure/)**: SSL setup, High Availability (Replication), and Backup strategy.
* **[04_Manuals](./docs/04_Manuals/)**: Technical installation guide and User manual.
* **[References](./docs/References.md)**: Bibliography and web resources used.

### 💻 [Source Code](./src/)
* **[Code Documentation](./src/README.md)**: General documentation and features in the source code.
* **[Main Entry](./src/main.py)**: Principal execution file.
* **[Modules](./src/)**: Logic for authentication, database connection, and UI.
* **[Requirements](./requirements.txt)**: List of Python dependencies for portability.

### 🗄️ [SQL Scripts](./sql/)
* **[Schema](./sql/schema.sql)**: Database structure and tables.
* **[Security](./sql/security.sql)**: Roles, users, and permission grants.
* **[Data](./sql/dummy_data.sql)**: Initial testing data.


## 📄 Documentation Guide
```
docs/
├── 01_Planning/
│   ├── Planning.md                    # WBS, Timeline, and Task Table
│   ├── Tech_Stack.md                  # Software & Hardware choices
│   └── Session_Log.md                 # The daily log of hours and activities
│
├── 02_Database_Design/
│   ├── ER_Diagram.png                 # Entity-Relationship diagram
│   ├── Relational_Model.pdf           # Table schemas and normalization 
│   ├── Data_Dictionary.pdf            # Details on fields, types, and constraints 
│   └── Security_Matrix.pdf            # RBAC Roles and Permissions table 
│
├── 03_Infrastructure/
│   ├── SSL_Configuration.pdf          # Steps for PostgreSQL encryption 
│   ├── Replication_Architecture.pdf   # Master-Slave diagram and logic 
│   ├── Backup_Strategy.pdf            # Backup scripts and cloud sync guide 
│   └── GDPR_Compliance.pdf            # Data privacy and masking documentation 
│
├── 04_Manuals/
│   ├── Installation_Guide.pdf         # Tech guide (venv, requirements, db setup) 
│   └── User_Manual.pdf                # Visual guide for the interface
│
└── References.md                      # Bibliography and web resources (Mandatory)
```

## 👥 Authors
* **Yossef Errazik** - [[Link to Profile](https://github.com/yosseferrazik)]

