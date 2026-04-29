# Client
> This directory contains the Tkinter desktop client for the Hospital Sa Palomera project. It is the staff-facing application used to authenticate against the backend and access the main operational workflows already implemented in the project.

## Purpose

The client acts as the presentation layer of the platform. Its job is to provide a simple desktop interface for hospital staff while delegating validation, persistence, and business rules to the Flask API in the `server/` module.

At the moment, the application focuses on four practical areas:

* User authentication with login and registration screens.
* Maintenance forms for staff and patient creation.
* Daily consultation views for surgeries and scheduled visits.
* Test-data utilities to generate or clean large dummy datasets from the UI.

## Main Features

### Authentication flow
* `LoginView` sends credentials to `POST /api/auth/login`.
* `RegisterView` allows creating an application user linked to an existing `staff_id`.
* After a successful login, the JWT access token is stored in the singleton session helper at `client/utils/session.py`.

### Main menu
* The main menu is the entry point after login.
* It opens the maintenance area, the daily query/report windows, and the dummy-data tools.
* A logout action clears the in-memory session and returns the user to the login screen.

### Maintenance area
The maintenance window is organized into tabs:

* Doctor registration
* Nursing staff registration
* General staff registration
* Patient registration
* Nursing assignment to either a doctor or a floor

These forms collect user input and submit it to protected backend endpoints through the API client layer.

### Queries and reports
The current reporting interface provides two date-based consultation screens:

* `SurgeriesView`: displays surgeries scheduled on a given day.
* `VisitsView`: displays scheduled appointments and visit information for a given day.

Both screens use Tkinter `Treeview` widgets so users can inspect multiple records in a tabular format.

## Runtime Architecture

```text
client/
|-- services/         # HTTP communication with the backend API
|-- utils/            # Client-side helpers such as session state
|-- views/            # Tkinter screens and secondary windows
`-- main.py           # Desktop application entry point
```

## Important Files

* `main.py`: starts the Tkinter application, creates the root window, and switches between top-level views.
* `services/api_client.py`: centralizes all HTTP requests to the backend and applies the JWT header automatically when a session token exists.
* `utils/session.py`: singleton used to keep the logged-in username, token, and role in memory during the session.
* `views/login_view.py`: login form and access entry point.
* `views/register_view.py`: user registration form for application accounts.
* `views/main_menu.py`: navigation hub for maintenance, daily queries, and dummy-data actions.
* `views/maintenance_view.py`: notebook-based CRUD-style forms for hospital entities.
* `views/surgeries_view.py` and `views/visits_view.py`: read-only query screens for operational data.

## Backend Integration

The client expects the backend API to be available at:

```text
http://localhost:5000/api
```

That base URL is currently hardcoded in `client/services/api_client.py`, so both applications are expected to run locally with the Flask server listening on port `5000`.

## API Operations Used by the Client

The client currently consumes the following backend routes:

* `POST /api/auth/login`
* `POST /api/auth/register`
* `POST /api/maintenance/staff/medical`
* `POST /api/maintenance/staff/nursing`
* `POST /api/maintenance/staff/general`
* `POST /api/maintenance/patients`
* `PUT /api/maintenance/nursing/assign`
* `GET /api/maintenance/surgeries?date=YYYY-MM-DD`
* `GET /api/maintenance/visits/scheduled?date=YYYY-MM-DD`
* `POST /api/dummy/generate`
* `DELETE /api/dummy/cleanup`

## Local Execution

### Requirements
* Python 3.10 or newer is recommended.
* Tkinter must be available in the Python installation.
* The `requests` package must be installed.
* The backend server must be running before using the client.

### Start the client

From the repository root:

```powershell
cd client
python main.py
```

## Usage Notes

* Registration requires a valid `staff_id` already present in the backend database.
* The client stores authentication state only in memory, so restarting the application resets the session.
* The role returned by the backend is not yet surfaced in the UI for feature-based access control.
* Date searches expect the `YYYY-MM-DD` format.
* The dummy-data option warns about generating more than 50,000 records, so it should be used only in development or test environments.

## Current Limitations

* The API base URL is hardcoded instead of being configurable.
* Error handling is functional but still basic, especially for validation and network failures.
* The interface is desktop-oriented and intentionally simple; it does not yet include advanced filtering, export tools, or role-specific menus.
* A disabled "Data Export" button is already present in the main menu, but that feature has not been implemented yet.

## Relationship With the Rest of the Project

This client is designed to work alongside:

* [`../server/README.md`](../server/README.md) for the Flask API and business logic.
* [`../sql/`](../sql/) for the PostgreSQL schema, security rules, triggers, and sample data.
* [`../docs/`](../docs/) for planning, infrastructure, and supporting project documentation.
