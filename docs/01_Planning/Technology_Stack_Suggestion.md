# 🛠️ Technology Stack Suggestion

This document details the technologies selected for the Hospital Management System, justifying their use based on the project requirements of security, scalability, and high availability.

---

## 1. Core Technologies

### 🐘 Database: PostgreSQL 18
* **Role:** Primary Relational Database Management System (RDBMS).
* **Justification:** * **Robustness:** Provides enterprise-grade reliability for sensitive medical data.
    * **Security:** Native support for SSL/TLS, advanced Role-Based Access Control (RBAC), and Row-Level Security (RLS).
    * **High Availability:** Proven streaming replication mechanisms for Master-Slave setups.
    * **Compliance:** Built-in features for Data Masking and encryption to meet GDPR standards.

### 🐍 Programming: Python 3.12+
* **Role:** Backend logic, Database connectivity, and App Interface.
* **Justification:**
    * **Libraries:** Vast ecosystem for database interaction (`psycopg2`) and data generation (`Faker`).
    * **Portability:** Easy deployment using Virtual Environments (`venv`).
    * **Readability:** Facilitates the creation of clean, maintainable, and commented code as required by the project guidelines.

---

## 2. Key Libraries & Dependencies

| Library | Purpose | Justification |
|:---|:---|:---|
| `psycopg2-binary` | DB Adapter | Standard PostgreSQL adapter for Python; supports asynchronous queries and secure connections. |
| `python-dotenv` | Configuration | Manages environment variables to keep credentials out of the source code (Security). |
| `Faker` | Data Generation | Efficiently generates 50k+ realistic records (names, addresses, dates) for testing. |
| `cryptography` | Security | Used for hashing sensitive data and managing secure access files. |
| `tkinter` | Graphical User Interface (GUI) | Standard Python interface for creating windows, forms, and interactive hospital dashboards. |
| `tkinter.messagebox` | User Feedback | To display alerts, errors, and confirmation dialogs for critical actions (e.g., deleting a patient). |
| `tkinter.ttk` | Themed Widgets | Provides a modern look and feel for tables (Treeview) and progress bars. |

---

## 3. Infrastructure & DevOps

* **Version Control:** **Git & GitHub**. Essential for tracking progress through frequent commits and maintaining a history of the project evolution.
* **Environment Management:** **Python `venv`**. Ensures that all dependencies are isolated, avoiding conflicts with system-wide packages and ensuring reproducibility.
* **Data Visualization (Optional):** **PowerBI Desktop**. If implemented, it will connect via PostgreSQL ODBC/DirectQuery to generate medical statistics and hospital occupancy reports.

---

## 4. Development Tools

* **IDE:** **Visual Studio Code (VS Code)** with Python and SQL extensions for linting and debugging.
* **Database Client:** **pgAdmin 4** or **DBeaver** for visual schema management and query testing during development.
* **Documentation:** **Markdown** for repository documentation and **Pandoc/Draw.io** for PDF exports and diagrams.

---

## 5. Security Architecture Summary
To comply with the hospital's strict privacy needs, the stack is configured as follows:
1.  **Transport:** All DB traffic is encrypted via **SSL**.
2.  **Storage:** Credentials are stored in a **separate configuration file** (not hardcoded).
3.  **Anonymization:** Use of **Dynamic Data Masking** at the database level for non-authorized roles.

---
*Note: Im already thinking of library i will use for the UI / UX. I may consider using a web solution.*