# Authentication

## How login works

1. User enters username + password in the Tkinter client
2. Client sends `POST /api/auth/login` with credentials
3. Server validates against `APP_USERS` table (bcrypt-hashed passwords)
4. On success: returns a **JWT token** with the user's role and staff ID
5. Client stores the token in memory (session singleton) and sends it as `Authorization: Bearer <token>` for all subsequent requests
6. Token expires after a configurable timeout

```bash
# Example login request
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "yossef", "password": "ChangeMePleaseChange!"}'

# Response
{"access_token": "eyJhbGciOiJIUzI1NiIs...", "role": "ADMIN", "staff_id": 1}
```

## Roles

Available roles: ADMIN, DOCTOR, NURSE, STAFF, RECEPTIONIST.

The sidebar in the desktop client shows the same base sections to all roles:
Dashboard, Maintenance, Data Workspace, Operational Reports, Statistics, Advanced Reports, Dummy Data.
Only ADMIN can additionally see **Users** and **Audit Logs** entries.

Server-side endpoints use `@jwt_required()` without per-role restrictions on most CRUD routes. Some administrative endpoints (user management, audit cleanup) and the PDF report download are restricted to specific roles.

## User management endpoints (admin)

| Action | Endpoint |
|--------|----------|
| List users | `GET /api/auth/users` |
| Register new user | `POST /api/auth/register` |
| Change own password | `PUT /api/auth/change-password` |
| Reset another user's password | `PUT /api/auth/users/<id>/password` |
| Toggle user active/inactive | `PUT /api/auth/users/<id>/toggle-active` |

## Password management

- Passwords are hashed with bcrypt (never stored in plaintext)
- Users can change their own password from the desktop app
- Admins can reset other users' passwords or toggle accounts active/inactive
- Disabled accounts cannot log in (checked before password verification)
