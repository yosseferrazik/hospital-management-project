# Server

This directory contains the Flask backend for the Hospital Sa Palomera project. It exposes the API used by the Tkinter client, connects the application to the hospital database model, and centralizes the current business logic for authentication, maintenance tasks, and test-data utilities.

## Purpose

The backend is the core application layer of the project. It is responsible for:

* Receiving requests from the desktop client.
* Validating and persisting hospital-related data through SQLAlchemy models.
* Protecting most operational routes with JWT authentication.
* Managing encrypted credential verification for registered application users.
* Providing development helpers for large dummy-data generation and cleanup.

## Current Functional Scope

### Authentication
The authentication module supports:

* User registration linked to an existing staff member.
* Password hashing with `bcrypt`.
* JWT access-token generation with `Flask-JWT-Extended`.
* Additional encrypted credential storage in `login_credentials.enc`.

The login flow validates both the database password hash and the encrypted credential file before issuing a token.

### Maintenance operations
Protected maintenance routes currently cover:

* Medical staff creation
* Nursing staff creation
* General staff creation
* Patient creation
* Nursing assignment to a doctor
* Nursing assignment to a floor
* Surgery lookup by date
* Scheduled visit lookup by date

### Development/test utilities
The backend also includes protected endpoints for:

* Generating dummy data
* Cleaning previously generated dummy data

These helpers are useful during development and manual testing, especially for validating the client query screens against larger datasets.

## Project Layout

```text
server/
|-- app/
|   |-- routes/       # Flask blueprints and API endpoints
|   |-- services/     # Application/business logic
|   |-- utils/        # Helper modules such as encryption support
|   |-- __init__.py   # Flask app factory and extension setup
|   |-- config.py     # Environment-based configuration
|   `-- models.py     # SQLAlchemy ORM models
|-- requirements.txt  # Python dependencies
|-- login_credentials.enc
`-- run.py            # Local development entry point
```

## Main Components

### Application factory
`app/__init__.py` creates the Flask app, loads configuration, initializes:

* `Flask-SQLAlchemy`
* `Flask-JWT-Extended`
* `Flask-CORS`

It also registers the `auth`, `maintenance`, and `dummy` blueprints.

### Configuration
`app/config.py` loads runtime settings from environment variables. The most important values are:

* `DATABASE_URL`
* `JWT_SECRET_KEY`
* `ENCRYPTION_KEY`

### Models
`app/models.py` defines the main entities used by the backend, including:

* Application users
* Staff and staff specializations
* Patients
* Visits and scheduled appointments
* Surgeries and surgery assistants
* Floors, rooms, operating theaters, and devices
* Dummy registry tracking

### Services
The `app/services/` package isolates business logic from routing code:

* `auth_service.py`: registration, login, password hashing, token issuance
* `staff_service.py`: staff creation and nursing assignment
* `patient_service.py`: patient creation
* `surgery_service.py`: surgery queries by date
* `visit_service.py`: scheduled visit queries by date
* `dummy_service.py`: dummy-data generation and cleanup

### Utilities
`app/utils/encryption.py` encrypts and verifies locally stored login credentials using Fernet symmetric encryption.

## Available API Routes

### Authentication
* `POST /api/auth/register`
* `POST /api/auth/login`

### Maintenance
* `POST /api/maintenance/staff/medical`
* `POST /api/maintenance/staff/nursing`
* `POST /api/maintenance/staff/general`
* `POST /api/maintenance/patients`
* `PUT /api/maintenance/nursing/assign`
* `GET /api/maintenance/surgeries?date=YYYY-MM-DD`
* `GET /api/maintenance/visits/scheduled?date=YYYY-MM-DD`

### Dummy data
* `POST /api/dummy/generate`
* `DELETE /api/dummy/cleanup`

All maintenance and dummy-data routes are currently protected with `@jwt_required()`.

## Database Behavior

The backend uses SQLAlchemy ORM models that mirror the hospital domain. On startup, the app factory executes `db.create_all()`, which creates any missing tables defined in the ORM models.

This is practical for development, but it should be viewed as a convenience layer rather than a full migration strategy. The repository also includes SQL scripts in `../sql/` that document and support the broader database design.

## Environment Setup

### Required environment variables

```text
DATABASE_URL=postgresql://user:password@host:port/hospital_management
JWT_SECRET_KEY=replace-with-a-secure-secret
ENCRYPTION_KEY=fernet-key-value
```

Notes:

* `DATABASE_URL` must point to a reachable PostgreSQL database.
* `ENCRYPTION_KEY` must be a valid Fernet key.
* `JWT_SECRET_KEY` should be changed from any default value in real deployments.

## Local Execution

### Install dependencies

From the repository root:

```powershell
cd server
pip install -r requirements.txt
```

### Start the backend

```powershell
cd server
python run.py
```

By default, the application runs in development mode on:

```text
http://localhost:5000
```

The client expects the API under `http://localhost:5000/api`.

## Security Notes

* Passwords are hashed with `bcrypt` before being stored in the database.
* JWT tokens are used to protect most operational endpoints.
* The backend also writes encrypted credential mappings to `login_credentials.enc`.
* The file `login_credentials.enc` contains sensitive derived authentication material and should not be committed to version control or reused carelessly across environments.

## Important Operational Notes

* User registration requires that the referenced `staff_id` already exists in the `staff` table.
* Date-based queries expect `YYYY-MM-DD` input.
* Some routes rely on related domain records already existing, such as specialties, doctors, floors, or appointments.
* Error handling is present but still minimal in some routes and services, so invalid inputs may surface as raw backend error messages.

## Current Limitations

* The project currently uses `db.create_all()` instead of a migration tool such as Alembic or Flask-Migrate.
* Role claims are included in JWTs, but route-level role authorization is not yet enforced.
* The backend is configured for local development and learning purposes; it is not yet structured as a production deployment target.
* The encrypted credential file introduces an extra verification step that should be documented and reviewed carefully as the authentication design evolves.

## Relationship With the Rest of the Project

This backend works together with:

* [`../client/README.md`](../client/README.md) for the Tkinter desktop application.
* [`../sql/`](../sql/) for the database schema, triggers, test helpers, and security configuration.
* [`../docs/`](../docs/) for planning, infrastructure, and project-wide documentation.
