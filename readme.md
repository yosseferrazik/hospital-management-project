# 🏥 Hospital Management System | ASIX Intermodular Project

This repository contains the complete intermodular project for the **ASIX program (Institut Sa Palomera)**. The project integrates Database Design (PostgreSQL), Programming (Python), and Infrastructure Management.

---

## 📂 Project Structure & Index

This repository is organized into specific modules to ensure clarity and professional standards. Click on the links to navigate:

### 📑 [Documentation](./docs/)
* **[01_Planning](./docs/01_Planning/)**: Project proposal, Gantt charts, and daily session logs.
* **[02_Database_Design](./docs/02_Database_Design/)**: ER diagrams, Relational model, and Security matrix.
* **[03_Infrastructure](./docs/03_Infrastructure/)**: SSL setup, High Availability (Replication), and Backup strategy.
* **[04_Manuals](./docs/04_Manuals/)**: Technical installation guide and User manual.
* **[References](./docs/References.md)**: Bibliography and web resources used.

### 💻 [Source Code](./src/)
* **[Main Entry](./src/main.py)**: Principal execution file.
* **[Modules](./src/)**: Logic for authentication, database connection, and UI.
* **[Requirements](./requirements.txt)**: List of Python dependencies for portability.

### 🗄️ [SQL Scripts](./sql/)
* **[Schema](./sql/schema.sql)**: Database structure and tables.
* **[Security](./sql/security.sql)**: Roles, users, and permission grants.
* **[Data](./sql/dummy_data.sql)**: Initial testing data.

---

## ⚙️ Installation & Setup

To ensure the project runs correctly, follow these steps to set up the **Virtual Environment (venv)**:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yosseferrazik/hospital-management-project.git
   cd hospital-management-project
   ```

2. **Setup the Virtual Environment:**
   ```bash
   # Create the environment
   python -m venv venv

   # Activate it (Windows)
   .\venv\Scripts\activate
   # Activate it (Linux/Mac)
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔒 Security Requirements
According to the project specifications:
* **Credentials:** Database login details are stored in a separate file (`src/access_config.txt`) and are not hardcoded.
* **SSL:** All database connections are encrypted.
* **Masking:** Sensitive patient data is protected via Data Masking.

---

## 👥 Authors
* **Yossef Errazik** - [[Link to Profile](https://github.com/yosseferrazik)]

---
