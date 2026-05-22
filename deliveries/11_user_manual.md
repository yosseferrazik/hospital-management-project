# User Manual

## Getting started

1. Start the API server (see [Installation Guide](./10_installation_manual.md))
2. Launch the desktop app: `python desktop/src/main.py`
3. Log in with your credentials

## Logging in

- Enter your username and password
- Click **Sign in** (or press Enter)
- If you're an admin, you'll see extra options in the sidebar (User Management, Audit Logs)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-06-29-image.png)

## Main sections (sidebar)

### Dashboard

Shows today's summary: number of visits, surgeries, active admissions, and record counts. The dashboard gives you a quick overview of the hospital's current status at a glance.

### Maintenance

Register new staff, patients, and manage assignments.

**For staff registration:** fill in personal details, select type (Medical/Nursing/General), and save. Each staff type has different required fields.

**For patients:** enter identification, contact info, medical data (blood type, allergies). The system validates all fields before saving.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-06-48-image.png)

### Data Workspace (Resource Browser)

Browse, edit, or delete any record in the system. Select an entity type from the dropdown, then use the table to view or edit. This is the most versatile section — you can access any table in the database.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-07-00-image.png)

### Operational Reports

- **Daily Visits** — see all visits scheduled for a given date
- **Daily Surgeries** — see surgeries planned for a date

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-07-14-image.png)

### Statistics

- Floor overview (rooms, theaters, nurses per floor)
- Staff directory (all personnel)
- Visits per day (last 12 days)
- Doctor ranking (who sees the most patients)
- Disease ranking (most common diagnoses)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-07-36-image.png)

### Advanced Reports

Multi-tab report viewer with filters and PDF download. You can combine multiple report types, apply date filters, and export the results as a professional PDF document.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-07-53-image.png)

### Dummy Data

Generate test data for development and testing:

1. Enter the number of patients to create (max 50,000)
2. Click **Generate** (this may take a few minutes)
3. Use **Cleanup** to remove all test data

This feature is useful for testing the system's performance and verifying that reports work correctly with large datasets.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-08-05-image.png)

### User Management (admin only)

Create new users, reset passwords, or enable/disable accounts. Users are linked to existing staff records.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-08-18-image.png)

### Audit Logs (admin only)

View all data access and modifications, filterable by user, action, table, and date range. This section provides full traceability of all changes made in the system.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-08-31-image.png)

## Changing your password

Click **Change Password** in the sidebar, enter your old and new password. The system will verify your old password before updating.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-08-40-image.png)

## Logging out

Click **Logout** in the sidebar. Your session will be terminated and you will be returned to the login screen.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/user_manual/2026-05-22-19-08-52-image.png)
