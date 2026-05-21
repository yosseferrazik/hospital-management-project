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

## Role-based access

The sidebar in the desktop client dynamically shows/hides options based on role:

| Role | Can see |
|------|---------|
| ADMIN | Everything (including User Management, Audit Logs) |
| DOCTOR | Dashboard, Maintenance, Reports, Export |
| NURSE | Dashboard, Maintenance (limited), Reports |
| RECEPTIONIST | Dashboard, Maintenance (patients), Reports |
| STAFF | Dashboard (limited view) |

## Password management

- Passwords are hashed with bcrypt (never stored in plaintext)
- Users can change their own password from the desktop app
- Admins can reset other users' passwords or toggle accounts active/inactive
- Disabled accounts cannot log in (checked before password verification)
