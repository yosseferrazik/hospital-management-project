# Architecture Overview (Reduced)

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 3.2          |
| Last Updated   | 2026-05-07   |

## Purpose

This document provides a high-level overview of the Hospital Management System (HMS) architecture, covering main components, their responsibilities, and key design decisions. It is self-contained and does not require external references.

**Scope:** Desktop + backend architecture for development and lab environments.

## System Overview

The Hospital Management System is a desktop-based healthcare application using a client-server architecture with a REST API backend and PostgreSQL database.

### Key Design Principles

- **Layered Architecture**: Separation between presentation, API, business logic, and persistence
- **API-Centric**: All client-server communication through REST API
- **Service Isolation**: Business logic isolated in service modules
- **Database Centralization**: PostgreSQL as single source of truth
- **Security by Default**: JWT authentication on protected operations
- **Python End-to-End**: Consistent language across all components

## Architectural Style

Layered client-server architecture:

- **Presentation layer**: `tkinter` desktop client
- **Application layer**: Flask REST API
- **Service layer**: Python business logic modules
- **Persistence layer**: SQLAlchemy ORM + PostgreSQL
- **Security layer**: JWT + password hashing

## High-Level Component View

```
+------------------------+
| Desktop Client         |
| tkinter + requests     |
+-----------+------------+
            | HTTP/JSON
            v
+------------------------+
| Flask API              |
| routes + JWT + CORS    |
+-----------+------------+
            | service calls
            v
+------------------------+
| Application Services   |
| business logic layer   |
+-----------+------------+
            | ORM access
            v
+------------------------+
| SQLAlchemy Models      |
+-----------+------------+
            | PostgreSQL driver
            v
+------------------------+
| PostgreSQL Database    |
+------------------------+
```

## Main Subsystems

### 1. Desktop Client
- User interface (login, menus, forms, queries)
- In-memory session state (JWT token)
- Delegates all business operations to backend API

### 2. API Layer
- REST endpoints organized with Flask blueprints (auth, maintenance, dummy)
- Request parsing, validation, response formatting
- Route protection with `@jwt_required()`

### 3. Service Layer
- Business logic isolated from route handlers
- Services for auth, staff, patient, surgery, visit, and test data

### 4. Persistence Layer
- SQLAlchemy ORM models for domain entities (staff, patients, surgeries, visits, etc.)
- Schema initialization during startup (development convenience)

### 5. Security Layer
- Password hashing with `bcrypt`
- JWT tokens via Flask-JWT-Extended

## Request Flow (Simplified)

### Authentication Flow
1. Client sends credentials to `POST /api/auth/login`
2. Backend validates user in database and credential file
3. JWT token returned to client
4. Client stores token in session

### Protected Business Flow
1. Client calls protected endpoint with `Authorization: Bearer <token>`
2. Flask-JWT-Extended validates token
3. Route delegates to service module
4. Service interacts with ORM and database
5. JSON response returned and rendered in UI

## Current Functional Domains

| Domain              | Current Support                                |
|:------------------- |:---------------------------------------------- |
| Authentication      | Login and user registration                    |
| Staff maintenance   | Medical, nursing, and general staff creation   |
| Patient maintenance | Patient registration                           |
| Nursing management  | Assignment to doctor or floor                  |
| Operational queries | Surgeries and scheduled visits by date         |
| Test tooling        | Dummy data generation and cleanup              |

## Technology Stack Summary

| Layer          | Technologies                                      |
| :------------- | :------------------------------------------------ |
| Language       | Python 3.10+ (end-to-end)                         |
| Desktop Client | tkinter, requests, PyInstaller                    |
| Backend API    | Flask, Flask-SQLAlchemy, Flask-JWT-Extended, CORS |
| Database       | PostgreSQL, psycopg2, SQLAlchemy ORM              |
| Security       | bcrypt, JWT, Fernet                               |

## Architectural Boundaries

- **Client**: UI rendering, session state, API requests
- **Backend**: Authentication, business rules, persistence, data workflows
- **Database**: Structured storage, relational integrity, source of truth

## Known Limitations (Summary)

- Coarse-grained authorization (authenticated ≈ fully allowed)
- Schema initialized with `db.create_all()` (no migration history)
- HTTP in development (TLS documented but not enforced)
- Single-instance deployment (no redundancy)
- Local encrypted credential file adds deployment complexity

## Future Directions (Summary)

- Fine-grained RBAC with audit logging
- Alembic migrations for schema versioning
- Mandatory HTTPS in all environments
- Load-balanced API instances with database replication
- External secrets management (eliminate local credential files)