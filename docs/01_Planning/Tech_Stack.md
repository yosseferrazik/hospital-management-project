# 🛠️ Technology Stack Suggestion
> This document details the technologies and hardware specifications selected for the HMS, justifying their use based on the project requirements of security, scalability, high availability, and resource efficiency.

## Core Technologies

### 🐘 Database: PostgreSQL 18
* **Role:** Primary Relational Database Management System (RDBMS).
* **Justification:** * **Robustness:** Provides enterprise-grade reliability for sensitive medical data.
    * **High Availability:** Native streaming replication for Master-Slave setups to ensure 24/7 hospital operations.
    * **Compliance:** Built-in features for Data Masking and encryption to meet GDPR standards.
    * **Internationalization:** Configured with **UTF-8 Encoding** and specific `LC_COLLATE` to support **Cyrillic characters**, addressing the demographic needs of the region (Eastern European population).

### 🐍 Programming: Python 3.12+
* **Role:** Backend logic, Database connectivity, and Graphical User Interface (GUI).
* **Justification:**
    * **Portability:** Easy deployment using Virtual Environments (`venv`) as required by project guidelines.
    * **Maintainability:** Facilitates clean, commented code for each function and procedure.

## Hardware Specifications (Optimized for Low Resources)
To comply with the hospital's requirement for a system that runs on limited resources, the following infrastructure is proposed:

| Component | Specification | Purpose |
|:---|:---|:---|
| **Server Nodes (x2)** | 2 Cores CPU / 4GB RAM / 20GB SSD | Master and Slave nodes for DB Replication and Backend. |
| **Client Stations** | 1 Core CPU / 2GB RAM | Thin clients running the Python Tkinter application. |
| **Networking** | 1 Gbps LAN | Low-latency connection for real-time DB synchronization. |
| **Virtualization** | **Docker Compose** | Used to orchestrate the nodes and ensure the environment is portable and reproducible on any hospital hardware. |

## Key Libraries & Dependencies

| Library | Purpose | Justification |
|:---|:---|:---|
| `psycopg2-binary` | DB Adapter | Standard PostgreSQL adapter; supports SSL and secure connections. |
| `python-dotenv` | Configuration | Manages environment variables to keep credentials out of the source code. |
| `Faker` | Data Generation | Generates 50k+ realistic records for testing (supports multiple locales for Cyrillic data). |
| `cryptography` | Security | Used for managing secure access files and sensitive data hashing. |
| **`tkinter`** | **GUI (Desktop)** | **Efficiency:** Extremely lightweight library that consumes minimal RAM, ideal for the hospital's older hardware. No browser overhead required. |
| `tkinter.ttk` | Modern UI | Provides a structured and tabulated look for medical reports and patient lists. |

## Infrastructure & DevOps

* **Version Control:** **Git & GitHub**. Essential for tracking progress through frequent commits.
* **Environment Management:** **Python `venv`**. Ensures all dependencies are isolated and portable via `requirements.txt`.
* **Data Visualization:** **PowerBI Desktop**. Connected via PostgreSQL ODBC for real-time hospital occupancy and daily visit dashboards.

## Development & Export Tools

* **IDE:** **Visual Studio Code (VS Code)** for development and debugging.
* **DB Client:** **pgAdmin 4 / DBeaver** for schema management.
* **Export Formats:** Native Python `json` and `xml.etree` modules will be used to generate the mandatory files for the Social Security API integration.

## Security Architecture Summary
1. **Transport:** All DB traffic is encrypted via **SSL/TLS**.
2. **Storage:** Credentials are stored in a **separate configuration file** (excluded from Git).
3. **Anonymization:** Implementation of **Dynamic Data Masking** at the database level so administrative staff cannot view sensitive clinical diagnosis.
4. **Resilience:** Automatic failover capability through the configured **PostgreSQL Replica**.

---
*Updated: April 9, 2026 - Version 1.1 (Hardware & I18n Update)*