# Administrator Manual

> **Audience:** System administrators managing the Hospital Management System.
> **Last Updated:** 2026-05-19

---

## Table of Contents

1. [User Management](#1-user-management)
2. [Audit Logs](#2-audit-logs)
3. [Password Management](#3-password-management)
4. [Sidebar Navigation](#4-sidebar-navigation)
5. [System Maintenance](#5-system-maintenance)

---

## 1. User Management

Access the **Users** tab in the sidebar (visible only to ADMIN role).

### 1.1 User List (Left Panel)

Displays all registered accounts in a table with columns:

| Column   | Description                          |
|:---------|:-------------------------------------|
| ID       | Internal user identifier             |
| Username | Login name                           |
| Role     | One of: ADMIN, DOCTOR, NURSE, STAFF, RECEPTIONIST |
| Active   | Whether the account can log in (Yes/No) |

Click any row to select a user for management actions.

### 1.2 Create New User (Right Panel — Top)

Fill in the following fields and click **Create User**:

| Field      | Description                              |
|:-----------|:-----------------------------------------|
| Username   | Unique login name                        |
| Password   | Account password                         |
| Role       | Dropdown selection (ADMIN/DOCTOR/NURSE/STAFF/RECEPTIONIST) |
| Staff ID   | Linked staff record identifier           |

All fields are required. On success, the user list refreshes automatically.

### 1.3 Manage Selected User (Right Panel — Bottom)

After selecting a user from the list, two actions are available:

- **Toggle Active** — Enable or disable the account. Disabled accounts receive `"Account is disabled"` on login attempt.
- **Reset Password** — Prompted to enter a new password for the selected user. The user's current password is replaced immediately.

---

## 2. Audit Logs

Access the **Audit Logs** tab in the sidebar (visible only to ADMIN role).

### 2.1 Filters

| Filter   | Type       | Description                           |
|:---------|:-----------|:--------------------------------------|
| Table    | Text input | Filter by table name (e.g., `patients`) |
| Action   | Dropdown   | Filter by action type: INSERT, UPDATE, DELETE |
| User ID  | Text input | Filter by numeric user identifier     |
| From     | Text input | Start date (ISO format, e.g. `2026-01-01`) |
| To       | Text input | End date (ISO format)                 |

Click **Apply** to apply filters, **Clear** to reset all filters, or **Refresh** to reload the current view.

### 2.2 Results Table

| Column    | Description                          |
|:----------|:-------------------------------------|
| ID        | Log entry identifier                 |
| User      | Username who performed the action    |
| Timestamp | Date and time of the action          |
| Action    | INSERT, UPDATE, or DELETE            |
| Table     | Database table affected              |
| Record    | ID of the affected record            |
| Notes     | Additional context or details        |

Records are displayed **most recent first** (sorted by `log_id DESC`).

### 2.3 Pagination

- **20 records per page**
- Navigate with `< Prev` and `Next >` buttons
- Total record count and current page indicator shown in the footer

### 2.4 Diagnostics & Retention

The footer also displays:

- **Total records** in the audit log
- **Retention period** (default: 90 days before automatic cleanup)
- **Diagnostics** button — runs `GET /api/audit-logs/diagnostics` to check:
  - Whether the PostgreSQL audit trigger exists
  - Whether the trigger is active
  - Total log count
  - Sample of recent log entries

### 2.5 Purge Old Logs (ADMIN only)

Click **Purge Old** to delete records older than the retention period. A confirmation dialog appears before deletion. This uses `DELETE /api/audit-logs/cleanup?before=<date>`.

### 2.6 Test Endpoint

`POST /api/audit-logs/test` creates a test audit entry by inserting, updating, then deleting a record in a test table. Returns a JSON summary of the three actions performed.

### 2.7 API Endpoints

| Method | Endpoint | Auth | Description |
|:-------|:---------|:-----|:------------|
| GET | `/api/audit-logs` | No | List logs with optional `table`, `action`, `user_id`, `start_date`, `end_date`, `page`, `per_page` query params |
| GET | `/api/audit-logs/diagnostics` | No | Check trigger status and log count |
| POST | `/api/audit-logs/test` | No | Create a test audit entry |
| GET | `/api/audit-logs/retention` | No | Get current retention setting (days) |
| DELETE | `/api/audit-logs/cleanup` | No | Delete logs older than `before` date |

---

## 3. Password Management

### 3.1 Change Own Password

Available to all users from the sidebar footer. Click **Change Password** and follow the prompts:

1. Enter current password
2. Enter new password
3. Confirm new password

### 3.2 Admin Reset Password

Available from the **Users** tab. Select a user and click **Reset Password** — no old password required.

---

## 4. Sidebar Navigation

- **All users** see: Dashboard, Maintenance, Data Workspace, Operational Reports, Statistics, Advanced Reports, Dummy Data
- **ADMIN only** additionally sees: Users, Audit Logs (separated by a divider)
- **Header** shows: Sa Palomera Hospital logo and name
- **Footer** shows: current username and role, plus **Change Password** and **Logout** buttons side by side

---

## 5. System Maintenance

### 5.1 Server API

- Base URL: `http://<host>:5000/api`
- Health check: `GET /api/health`
- Login: `POST /api/auth/login` — returns `access_token`, `role`, `staff_id`
- All admin auth endpoints require JWT in `Authorization: Bearer <token>` header

### 5.2 Key Auth Endpoints

| Method | Endpoint                               | Auth Required | Description                          |
|:-------|:---------------------------------------|:--------------|:-------------------------------------|
| POST   | `/api/auth/register`                   | No            | Create new user (admin UI uses this) |
| POST   | `/api/auth/login`                      | No            | Authenticate, returns token + role   |
| GET    | `/api/auth/users`                      | JWT           | List all users (ADMIN only)          |
| PUT    | `/api/auth/change-password`            | JWT           | Change own password                  |
| PUT    | `/api/auth/users/<id>/password`        | JWT + ADMIN   | Reset another user's password        |
| PUT    | `/api/auth/users/<id>/toggle-active`   | JWT + ADMIN   | Enable/disable user account          |
| GET    | `/api/audit-logs`                      | No            | List audit logs with filters         |

### 5.3 Client Configuration

The desktop client reads `API_BASE_URL` from `desktop/src/.env`. Default: `http://localhost:5000/api`.

Timeout: 300 seconds (configurable via `APIClient.timeout`).
