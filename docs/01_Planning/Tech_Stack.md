# Technology Stack

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 2.1          |
| Last Updated   | 2026-05-04   |

## Purpose

Summarize the technologies used by the Hospital Management System and explain their role in the solution.

## Solution Scope

The current platform is implemented as a desktop client plus backend API architecture:

- Presentation layer: Python desktop client built with `tkinter`.
- Application layer: REST API built with Flask.
- Domain and persistence layer: SQLAlchemy ORM mapped to PostgreSQL.
- Security layer: JWT-based authentication and password hashing.

## Core Technologies

### Programming Language

| Technology | Version | Primary Use                                                | Notes                                                                         |
|:---------- |:------- |:---------------------------------------------------------- |:----------------------------------------------------------------------------- |
| Python     | 3.10+   | Client application, backend API, business logic, utilities | Shared language across the full stack simplifies development and maintenance. |

### Backend and API

| Technology         | Primary Use              | Notes                                                                        |
|:------------------ |:------------------------ |:---------------------------------------------------------------------------- |
| Flask              | HTTP API framework       | Used to expose authentication, maintenance, query, and dummy-data endpoints. |
| Flask-SQLAlchemy   | ORM integration          | Provides model mapping, session handling, and database access patterns.      |
| Flask-JWT-Extended | Authentication tokens    | Issues and validates JWT access tokens for protected routes.                 |
| Flask-CORS         | Cross-origin support     | Enabled at application level for integration flexibility during development. |
| Werkzeug           | Flask runtime foundation | Included as part of the Flask execution stack.                               |

### Data and Persistence

| Technology | Primary Use                 | Notes                                                                       |
|:---------- |:--------------------------- |:--------------------------------------------------------------------------- |
| PostgreSQL | Primary relational database | Intended system of record for hospital entities and operational data.       |
| SQLAlchemy | ORM and query abstraction   | Used through Flask-SQLAlchemy for model definitions and queries.            |
| psycopg2   | PostgreSQL driver           | Provides runtime connectivity between the Flask application and PostgreSQL. |

### Security and Authentication

| Technology | Primary Use               | Notes                                              |
|:---------- |:------------------------- |:-------------------------------------------------- |
| bcrypt     | Password hashing          | Used to hash user passwords before persistence.    |
| JWT        | Session/auth token format | Used to protect maintenance and dummy-data routes. |

### Client Application

| Technology  | Primary Use                 | Notes                                                                           |
|:----------- |:--------------------------- |:------------------------------------------------------------------------------- |
| tkinter     | Desktop graphical interface | Main staff-facing interface for login, maintenance, and operational queries.    |
| ttk         | Native themed widgets       | Used for notebook tabs and structured UI controls.                              |
| requests    | HTTP client                 | Sends API requests from the desktop application to the backend server.          |
| PyInstaller | Desktop packaging           | Indicated by `main.spec`; suitable for generating distributable desktop builds. |

### Development and Test Support

| Technology         | Primary Use               | Notes                                                                        |
|:------------------ |:------------------------- |:---------------------------------------------------------------------------- |
| Faker              | Synthetic data generation | Supports large-scale dummy data creation for development and manual testing. |
| python-dotenv      | Environment loading       | Loads backend configuration from environment variables.                      |
| Git                | Version control           | Change tracking and collaboration.                                           |
| Visual Studio Code | Development environment   | Practical IDE for Python, Markdown, and project maintenance.                 |

## Current Application Modules

### Client-Side Modules

- `views/`: login, registration, main menu, maintenance, surgeries, and visits screens.
- `services/api_client.py`: centralized HTTP communication with the backend.
- `utils/session.py`: in-memory session singleton for token, username, and role.

### Server-Side Modules

- `app/routes/`: API endpoints grouped by authentication, maintenance, and dummy-data concerns.
- `app/services/`: business logic for authentication, staff, patients, visits, surgeries, and dummy data.
- `app/models.py`: SQLAlchemy model definitions for the current hospital domain.
- `app/utils/`: Helper modules.

## Runtime and Deployment Assumptions

| Area                    | Current Approach                                        |
| :---------------------- | :------------------------------------------------------ |
| Client execution        | Local desktop process started from `client/src/main.py` |
| API execution           | Local Flask process started from `server/src/run.py`    |
| Default API base URL    | `http://localhost:5000/api`                             |
| Database initialization | `db.create_all()` in the Flask app factory              |
| Configuration source    | Environment variables loaded through `python-dotenv`    |

## Technology Decisions and Rationale

- Python is used end-to-end to reduce complexity across client, API, and utility code.
- Flask provides a simple and understandable service layer for the current academic scope.
- SQLAlchemy accelerates implementation while preserving a clear data model.
- `tkinter` is appropriate for a desktop-first internal tool with limited deployment complexity.
- JWT-based protection is enough for the current stage, although authorization is still coarse-grained.


