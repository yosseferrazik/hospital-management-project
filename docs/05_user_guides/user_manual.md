# User Manual

## Getting started

1. Start the API server (see [Installation Guide](../04_deployment/installation_guide.md))
2. Launch the desktop app: `python desktop/src/main.py`
3. Log in with your credentials

## Logging in

- Enter your username and password
- Click **Sign in** (or press Enter)
- If you're an admin, you'll see extra options in the sidebar (User Management, Audit Logs)

## Main sections (sidebar)

### Dashboard

Shows today's summary: number of visits, surgeries, active admissions, and record counts.

### Maintenance

Register new staff, patients, and manage assignments.

**For staff registration:** fill in personal details, select type (Medical/Nursing/General), and save.

**For patients:** enter identification, contact info, medical data (blood type, allergies).

### Data Workspace (Resource Browser)

Browse, edit, or delete any record in the system. Select an entity type from the dropdown, then use the table to view or edit.

### Operational Reports

- **Daily Visits** — see all visits scheduled for a given date
- **Daily Surgeries** — see surgeries planned for a date

### Statistics

- Floor overview (rooms, theaters, nurses per floor)
- Staff directory (all personnel)
- Visits per day (last 12 days)
- Doctor ranking (who sees the most patients)
- Disease ranking (most common diagnoses)

### Advanced Reports

Multi-tab report viewer with filters and PDF download.

### Dummy Data

Generate test data for development and testing:

1. Enter the number of patients to create (max 50,000)
2. Click **Generate** (this may take a few minutes)
3. Use **Cleanup** to remove all test data

### User Management (admin only)

Create new users, reset passwords, or enable/disable accounts.

### Audit Logs (admin only)

View all data access and modifications, filterable by user, action, table, and date range.

## Changing your password

Click **Change Password** in the sidebar, enter your old and new password.

## Logging out

Click **Logout** in the sidebar.
