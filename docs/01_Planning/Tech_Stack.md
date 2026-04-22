# 🛠️ Technology Stack
> This document details the technologies selected for the HMS (Hospital Management System), justifying their use based on the project requirements of security, scalability, high availability, and resource efficiency.

## Programming Languages
### Python v3.12+
* **Role:** Core backend logic and desktop application layer.
* **Justification:**
* * **Productivity:** Rapid development with a mature ecosystem for data-driven applications.
  * **Maintainability:** Readable syntax that supports structured and scalable codebases.
  * **Ecosystem:** Strong support for database connectivity, security libraries, and testing tools.
  * **Deployment:** Easily containerized and managed via virtual environments (`venv`).
    
## Database
### PostgreSQL v18.3
* **Role:** Primary relational database system for all clinical and administrative data.
* **Justification:**
  * **Reliability:** Proven enterprise-grade stability for critical systems.
  * **Scalability:** Supports replication and high-availability architectures.
  * **Security:** Advanced features such as role-based access control, encryption, and auditing.
  * **Compliance:** Compatible with GDPR requirements through secure configuration and data handling practices.
  * **Internationalization:** UTF-8 encoding with appropriate locale configuration to support multilingual datasets, including Cyrillic characters.

## Application Frameworks & Libraries
### Backend & Data Layer
* **Flask**
  Lightweight web framework used to expose internal APIs and service endpoints when required.
* **psycopg2**
  PostgreSQL adapter for Python enabling secure and efficient database communication.
* **python-dotenv**
  Manages environment variables and sensitive configuration outside source code.

### Utilities & Support Libraries
* **Faker**
  Generates synthetic datasets for testing and simulation purposes.
* **hashlib**
  Provides cryptographic hashing for secure handling of sensitive data (e.g., password hashing mechanisms).
* **requests**
  HTTP client library used for external API communication.

### User Interface
* **tkinter**
  Standard Python GUI toolkit used for desktop interface development.

## Infrastructure & DevOps
* **Git & GitHub**
  Version control system used for collaboration, tracking changes, and project history.
* **Docker**
  Containerization platform used to ensure consistent environments across development and deployment, including database and application services.
* **Python venv**
  Isolated environment management to ensure dependency consistency.
* **Power BI Desktop**
  Business intelligence tool connected to PostgreSQL via ODBC for real-time analytics and reporting.

## Development & Export Tools
* **Visual Studio Code (VS Code)**
  Primary development environment for coding and debugging.
* **pgAdmin / DBeaver**
  Database administration and schema management tools.
* **Data Export Modules**
  Native Python libraries (`json`, `xml.etree.ElementTree`) used for structured data export and external system integration.

## Architecture Overview
The system follows a **layered architecture** model:

* **Presentation Layer:** Desktop GUI (tkinter)
* **Application Layer:** Business logic (Python + Flask services)
* **Data Layer:** PostgreSQL database

This separation ensures maintainability, scalability, and clear responsibility distribution between components.

## Security Architecture
Security is implemented across all system layers:

* **Transport Security:** All communications are encrypted using TLS/SSL.
* **Authentication:** Role-based access control (RBAC) defines permissions for Doctors, Administrators, and Patients.
* **Data Protection:** Sensitive information is protected through hashing and database-level masking mechanisms.
* **Configuration Security:** Environment variables are stored outside the codebase and excluded from version control.
* **Resilience:** PostgreSQL replication ensures high availability and fault tolerance.

