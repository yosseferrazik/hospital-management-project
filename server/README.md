# Server

This directory contains the Flask backend for the Hospital Sa Palomera project.

## Responsibilities
* Expose API routes for authentication, maintenance tasks, and dummy data utilities.
* Connect the application layer with the PostgreSQL data model.
* Centralize business logic in service modules.
* Manage JWT authentication and environment-based configuration.

## Main Structure
```text
server/
├── app/
│   ├── routes/      # API endpoints
│   ├── services/    # Business logic
│   ├── utils/       # Helpers such as credential encryption
│   ├── config.py    # Environment-based settings
│   ├── models.py    # SQLAlchemy models
│   └── __init__.py  # Flask application factory
├── requirements.txt
└── run.py           # Local entry point
```

## Notes
* The backend expects environment variables such as `DATABASE_URL`, `JWT_SECRET_KEY`, and `ENCRYPTION_KEY`.
* Local encrypted login credentials are stored in `server/login_credentials.enc`, which should not be committed.
