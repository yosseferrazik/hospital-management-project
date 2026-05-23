# User Manual

## Table of Contents

1. [Getting started](#getting-started)
2. [Logging in](#logging-in)
3. [Main sections (sidebar)](#main-sections-sidebar)
   - [Dashboard](#dashboard)
   - [Maintenance](#maintenance)
   - [Data Workspace (Resource Browser)](#data-workspace-resource-browser)
   - [Operational Reports](#operational-reports)
   - [Statistics](#statistics)
   - [Advanced Reports](#advanced-reports)
   - [Dummy Data](#dummy-data)
   - [User Management (admin only)](#user-management-admin-only)
   - [Audit Logs (admin only)](#audit-logs-admin-only)
4. [Changing your password](#changing-your-password)
5. [Common tasks walkthrough](#common-tasks-walkthrough)
6. [Tips and tricks](#tips-and-tricks)
7. [Logging out](#logging-out)

---

## Getting started

### Prerequisites

1. The API server must be running (see the [Installation Guide](./10_installation_manual.md)).
2. The desktop application must be installed on your computer.
3. You must have valid credentials provided by the system administrator.

### Launching the application

```bash
# From the project directory
cd desktop/src
python main.py
```

> **Tip:** Create a desktop shortcut to `main.py` for quicker access.

---

## Logging in

1. Launch the desktop application.
2. Enter your **username** and **password** in the login form.
3. Click **Sign in** (or press Enter).
4. If you are an administrator, additional options will appear in the sidebar (User Management, Audit Logs).

### Login form fields

| Field      | Description                        |
|------------|------------------------------------|
| Username   | Your unique system username        |
| Password   | Your confidential password         |

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-06-29-image.png)

**Troubleshooting:**
- If you see **"Invalid credentials"**, check that Caps Lock is off and verify your username and password with the administrator.
- If the application does not connect, ensure the API server is running (`curl http://192.168.4.254:5000/health`).

---

## Main sections (sidebar)

### Dashboard

The Dashboard shows a summary of the hospital's current activity at a glance. It displays:

- **Visits today** — number of medical visits registered
- **Surgeries today** — surgeries scheduled or completed
- **Active admissions** — patients currently admitted
- **Record counts** — totals for patients, doctors, nurses, and staff

The dashboard automatically refreshes each time you navigate to it. Use this section as your home screen to get a quick overview of the day's activity.

### Maintenance

The Maintenance section allows you to register and manage staff, patients, and assignments.

#### Registering a new staff member

1. Navigate to **Maintenance** in the sidebar.
2. Click **Add Staff**.
3. Fill in the personal details form:
   - **First name** and **Last name**
   - **DNI / NIF** (Spanish national ID)
   - **Phone number** and **Email**
   - **Date of birth**
4. Select the **Staff Type**:
   - **Medical** — doctors and surgeons (requires license number)
   - **Nursing** — nurses and nursing assistants (requires nursing license)
   - **General** — administrative and support staff
5. Each staff type has different required fields. Fields marked with an asterisk `*` are mandatory.
6. Click **Save**. The system validates all fields before saving.

#### Registering a new patient

1. Navigate to **Maintenance** → **Add Patient**.
2. Enter the patient's identification details:
   - **DNI / NIF**
   - **First name** and **Last name**
   - **Date of birth**
   - **Gender**
3. Enter contact information:
   - **Phone number**
   - **Address**
   - **Email** (optional)
4. Enter medical data:
   - **Blood type** (A+, A−, B+, B−, AB+, AB−, O+, O−)
   - **Allergies** (comma-separated list, e.g., "Penicillin, Latex")
   - **Medical conditions** (optional)
5. Click **Save**.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-06-48-image.png)

> **Tip:** Use the **Data Workspace** to quickly verify that a patient or staff member already exists before creating a duplicate.

### Data Workspace (Resource Browser)

The Data Workspace is the most versatile section. It provides direct access to every table in the database.

#### Browsing records

1. Select an **Entity Type** from the dropdown (e.g., Patients, Visits, Doctors, Rooms).
2. The table displays all records for that entity.
3. Use the **Search** field to filter by keywords.
4. Click on any column header to sort.

#### Editing a record

1. In the table, select the record you want to edit.
2. Click **Edit** (or double-click the row).
3. Modify the fields in the form that opens.
4. Click **Save** to apply changes, or **Cancel** to discard.

#### Deleting a record

1. Select the record in the table.
2. Click **Delete**.
3. Confirm the deletion when prompted.

> **Warning:** Deletions are permanent. Audit logs will record who deleted what and when.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-07-00-image.png)

### Operational Reports

Generate daily operational reports for visits and surgeries.

#### Viewing daily visits

1. Navigate to **Operational Reports** → **Daily Visits**.
2. Select a **date** using the date picker.
3. The report shows all visits scheduled for that date, including:
   - Patient name and DNI
   - Doctor assigned
   - Time and reason for visit
   - Status (Scheduled / Completed / Cancelled)

#### Viewing daily surgeries

1. Navigate to **Operational Reports** → **Daily Surgeries**.
2. Select a **date**.
3. The report shows all surgeries planned for that date:
   - Patient name
   - Surgeon(s) assigned
   - Operating room
   - Scheduled time and duration
   - Status

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-07-14-image.png)

### Statistics

The Statistics section provides analytical views of hospital data.

| View                           | Description                                   |
|--------------------------------|-----------------------------------------------|
| **Floor Overview**             | Rooms, operating theaters, and nurses per floor |
| **Staff Directory**            | Complete list of all personnel                 |
| **Visits per Day (12 days)**   | Daily visit count trend chart                  |
| **Doctor Ranking**             | Which doctors see the most patients            |
| **Disease Ranking**            | Most common diagnoses across all patients      |

These views update automatically from live database data. Use them for quick insights without running formal reports.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-07-36-image.png)

### Advanced Reports

The Advanced Reports section is a multi-tab report viewer with filters and PDF export.

#### Generating a report

1. Navigate to **Advanced Reports**.
2. Select one or more **report types** from the tabs (e.g., Patient List, Visit Summary, Surgery Log).
3. Apply **filters** as needed:
   - **Date range** — filter by a specific period
   - **Specialty** — filter by medical specialty
   - **Doctor** — filter by attending physician
4. Click **Generate** to build the report.
5. Review the results in the preview pane.
6. Click **Export PDF** to download a professional PDF document.

#### Report types available

| Report Type       | Description                              |
|-------------------|------------------------------------------|
| Patient List      | All patients with contact and medical info |
| Visit Summary     | Visits within a date range                |
| Surgery Log       | Surgeries with details and outcomes       |
| Admission History | Patient admission and discharge records    |
| Prescription Log  | Medications prescribed                    |
| Exam Results      | Diagnostic exam results                   |

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-07-53-image.png)

### Dummy Data

Generate test data for development and performance testing purposes.

1. Navigate to **Dummy Data** in the sidebar.
2. Enter the number of **patients to create** (maximum: 50,000).
3. Click **Generate**.
   - This may take a few minutes for large datasets.
   - A progress bar shows the generation status.
4. The generated data includes related records (visits, admissions, prescriptions) for realistic testing.
5. Use **Cleanup** to remove all test data when finished.

> **Warning:** The Cleanup operation removes **all** dummy data. Real patient records are never affected.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-08-05-image.png)

### User Management (admin only)

This section is only visible to users with the **ADMIN** role.

See the [Administrator Manual](./12_administrator_manual.md) for detailed instructions on user management.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-08-18-image.png)

### Audit Logs (admin only)

This section is only visible to users with the **ADMIN** role.

The Audit Logs provide full traceability of all changes made in the system. See the [Administrator Manual](./12_administrator_manual.md) for details.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-08-31-image.png)

---

## Changing your password

1. Click **Change Password** in the sidebar.
2. Enter your **current password**.
3. Enter your **new password** (minimum 8 characters).
4. Re-enter the **new password** to confirm.
5. Click **Save**.

The system will verify your old password before updating. If successful, a confirmation message appears.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-08-40-image.png)

---

## Common tasks walkthrough

### Task 1: Register a new patient and schedule a visit

1. **Maintenance** → **Add Patient** → Fill in details → **Save**.
2. Note the patient ID that appears after saving.
3. **Data Workspace** → Select **Visits** from the dropdown → **Add**.
4. Enter the patient ID, select the doctor, date, and reason.
5. **Save**.

### Task 2: Look up a patient's medical history

1. **Data Workspace** → Select **Patients**.
2. Search by name or DNI.
3. Select the patient → **View Details**.
4. Related tabs show: visits, prescriptions, admissions, exams.

### Task 3: Generate end-of-month report

1. **Advanced Reports** → Select **Visit Summary** and **Surgery Log**.
2. Set date range to the full month.
3. Click **Generate** → review → **Export PDF**.

### Task 4: Find which doctor has the most patients

1. **Statistics** → **Doctor Ranking**.
2. The table shows doctors sorted by visit count, descending.

---

## Tips and tricks

| Tip                                                                 | Benefit                                              |
|---------------------------------------------------------------------|------------------------------------------------------|
| Use the **Search** field in Data Workspace to quickly find records   | Saves time navigating large tables                   |
| Sort tables by clicking column headers                              | Easier to find the highest/lowest values              |
| Generate dummy data before testing reports                          | Verify reports work with realistic volumes            |
| Use **Advanced Reports** multi-tab to combine data types             | One PDF with all information instead of many files    |
| Check the **Dashboard** first thing in the morning                  | Quick status overview without running multiple reports |
| Set `API_BASE_URL` in `desktop/src/.env` correctly                  | Prevents "Connection refused" errors                  |
| Use daily operational reports for morning briefings                 | Stay informed about today's schedule                  |

---

## Logging out

1. Click **Logout** in the sidebar.
2. Your session will be terminated immediately.
3. You will be returned to the login screen.

> **Security tip:** Always log out when leaving your workstation, especially in shared hospital environments.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-08-52-image.png)
