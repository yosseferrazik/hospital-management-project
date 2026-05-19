# User Manual

> **Audience:** End users of the Hospital Management System desktop client.
> **Last Updated:** 2026-05-19

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Sidebar Overview](#2-sidebar-overview)
3. [Dashboard](#3-dashboard)
4. [Maintenance](#4-maintenance)
5. [Data Workspace](#5-data-workspace)
6. [Operational Reports](#6-operational-reports)
7. [Statistics](#7-statistics)
8. [Advanced Reports](#8-advanced-reports)
9. [Dummy Data](#9-dummy-data)
10. [Change Password & Logout](#10-change-password--logout)

---

## 1. Getting Started

### 1.1 Login

1. Launch the application (`python desktop/src/main.py`).
2. Enter your **Username** and **Password**.
3. Click **Login**.

> **Note:** Self-registration is not available. Contact your system administrator to create an account.

If your account is disabled, you will see an error message: `"Account is disabled"`. Contact your administrator.

### 1.2 Login Response

Upon successful login, the client stores your username, role, and staff ID. The sidebar adapts to show features available to your role.

---

## 2. Sidebar Overview

The sidebar on the left provides navigation to all modules:

| Module              | Description                                      | All Users |
|:--------------------|:-------------------------------------------------|:----------|
| Dashboard           | Hospital capacity overview and today's agenda    | ✓         |
| Maintenance         | Specialized registration and assignment workflows | ✓         |
| Data Workspace      | CRUD access to operational database resources    | ✓         |
| Operational Reports | Visits and surgeries by date                     | ✓         |
| Statistics          | Hospital operational insights and metrics        | ✓         |
| Advanced Reports    | Multi-section summary report with PDF download   | ✓         |
| Dummy Data          | Generate and clean sample records safely         | ✓         |
| Users               | Account management (ADMIN only)                  | —         |
| Audit Logs          | Database change log viewer (ADMIN only)          | —         |

The header shows the **Sa Palomera Hospital logo** and name.  
The footer shows your **username**, **role**, and action buttons (**Change Password**, **Logout**).

---

## 3. Dashboard

Displays a summary of:

- Current hospital capacity (bed occupancy, room availability)
- Today's scheduled visits and surgeries
- Key alerts or notifications

---

## 4. Maintenance

Workflows for:

- Patient registration and admission
- Surgery scheduling and assignment
- Medical device tracking
- Staff assignment

---

## 5. Data Workspace

Browse, create, update, and delete records across all database tables.

### 5.1 Resource Browser

- **Left panel:** List of resources with a **filter text box** at the top. Type any text to filter rows in real time by any column value (case-insensitive).
- **Right panel:** Detail form for viewing or editing the selected record.

### 5.2 Available Resources

Patients, rooms, floors, staff, medical devices, scheduled appointments, medications, prescriptions, admissions, surgeries, radiology exams, pharmacy dispensations, operating theaters, medical specialties, and more.

---

## 6. Operational Reports

Query visits and surgeries by date range. Results are displayed in a table and can be used for operational planning.

---

## 7. Statistics

View hospital performance metrics, trends, and charts powered by Chart.js (rendered in a web view).

---

## 8. Advanced Reports

Generates a comprehensive multi-section PDF report of hospital activity for a given period.

### 8.1 Usage

1. Navigate to **Advanced Reports** in the sidebar.
2. Optionally set a **From** and **To** date (leave blank for all available data).
3. Click **Load Report** to preview summary data in the panel.
4. Click **Download PDF** to save the report as a PDF file.

### 8.2 PDF Report Contents

The PDF contains three pages:

| Page | Section | Contents |
|:-----|:--------|:---------|
| 1 | Executive Dashboard | KPI cards (patients, staff, occupancy, visits, surgeries, admissions, costs), top diagnoses, surgeries by type |
| 2 | Clinical Activity | Physician workload, prescribed medications, radiology exam summary |
| 3 | Financial & Operations | Pharmacy dispensations, admissions (active/discharged), recent surgeries |

### 8.3 Access Control

| Role     | PDF Download |
|:---------|:-------------|
| ADMIN    | ✓            |
| DOCTOR   | ✓            |
| NURSE    | ✓            |
| STAFF    | —            |
| RECEPTIONIST | —        |

---

## 9. Dummy Data

Generate or delete sample data for testing purposes.

### 9.1 Generate

1. Enter the number of patients (default 20, max 50000).
2. Click **Generate** to create sample records including: patients, staff (doctors, nurses, general), visits, appointments, surgeries with assistants, admissions, prescriptions, pharmacy dispensations with items, and radiology exams.
3. A result log shows the generation progress.

### 9.2 Clean

Click **Clean All Dummy Data** to remove all generated records. This deletes only records tracked by the DummyRegistry — real data is never affected.

> The dummy data is now more realistic: 16 medical specialties with 10 diagnoses each, 25 medications with real dosages, 26 surgical procedures, 24 radiology exam types with clinical findings, and coherent relationships between diagnoses, prescriptions, and doctor specialties.

---

## 10. Change Password & Logout

### 10.1 Change Password

Available to **all users** from the sidebar footer:

1. Click **Change Password**.
2. Enter your **current password**.
3. Enter your **new password**.
4. Confirm the new password.
5. Click OK. A confirmation message appears on success.

### 10.2 Logout

Click **Logout** in the sidebar footer. A confirmation dialog appears — click **Yes** to return to the login screen. Your session is cleared.
