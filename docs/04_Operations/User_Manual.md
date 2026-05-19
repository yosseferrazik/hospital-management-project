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
8. [Dummy Data](#8-dummy-data)
9. [Change Password & Logout](#9-change-password--logout)

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
| Dummy Data          | Generate and clean sample records safely         | ✓         |
| Users               | Account management (ADMIN only)                  | —         |
| Audit Logs          | Database change log viewer (ADMIN only)          | —         |

The footer shows your **username**, **role**, and action buttons.

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

## 8. Dummy Data

Generate or delete sample data for testing purposes:

- Select a table and specify the number of records
- Click **Generate** to create sample records
- Click **Clean All Dummy Data** to remove all generated records

---

## 9. Change Password & Logout

### 9.1 Change Password

Available to **all users** from the sidebar footer:

1. Click **Change Password**.
2. Enter your **current password**.
3. Enter your **new password**.
4. Confirm the new password.
5. Click OK. A confirmation message appears on success.

### 9.2 Logout

Click **Logout** in the sidebar footer. A confirmation dialog appears — click **Yes** to return to the login screen. Your session is cleared.
