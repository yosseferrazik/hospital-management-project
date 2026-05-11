# Installation Guide

## Purpose

Provide minimal, step-by-step instructions to prepare a local development environment and run the server (API) and desktop client. This guide targets developers and testers. For production deployment instructions see `docs/03_Security_and_Infrastructure/Deployment_Architecture.md`.

## Prerequisites

- Supported platforms: Windows 10/11, Linux, macOS
- Python 3.10 or newer
- Git
- Optional: VMware or Docker for infrastructure simulations

## Server (API)

1. Clone the repository:

```powershell
git clone <repo-url>
cd hospital-management-project
```

2. Create and activate a virtual environment (PowerShell example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On Linux/macOS (bash):

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install server dependencies:

```powershell
pip install -r server/requirements.txt
```

4. Configure environment variables (local example):

PowerShell:

```powershell
$env:FLASK_ENV = 'development'
$env:DATABASE_URL = 'postgresql://user:password@localhost:5432/hospital_management'
```

bash:

```bash
export FLASK_ENV=development
export DATABASE_URL='postgresql://user:password@localhost:5432/hospital_management'
```

5. Run the API (development mode):

```powershell
python server/run.py
```

The API will normally listen on `http://127.0.0.1:5000` unless configured otherwise.

## Desktop Client

1. Ensure the virtual environment is active and the server is running.

2. Install client dependencies (if present):

```powershell
pip install -r client/requirements.txt
```

Note: The GUI uses `tkinter`, which is typically included with standard Python installations on Windows.

3. Run the client:

```powershell
python client/main.py
```

4. Optional: Create a distributable using PyInstaller (spec included `client/main.spec`):

```powershell
pip install pyinstaller
pyinstaller client/main.spec
```

## Database

- The initial schema is provided in `sql/schema.sql`.
- Create the database and apply the schema using `psql` or another client:

```powershell
psql -U postgres -f sql/schema.sql
```

## Configuration Notes

- Do not store credentials in source control. Use environment variables or a secrets manager.
- For local development a simple `DATABASE_URL` with local credentials is acceptable; follow the security guidance in `docs/03_Security_and_Infrastructure/` for hardened deployments.

## Common Troubleshooting

- Database connection errors: Verify `DATABASE_URL`, ensure PostgreSQL is running, and that the schema was applied.
- Missing Python packages: Activate the virtual environment and re-run `pip install -r`.
- GUI issues: Verify the installed `tkinter` version matches the Python runtime.

## References

- `server/README.md` — server-specific instructions
- `client/README.md` — client-specific instructions
- `docs/03_Security_and_Infrastructure/Deployment_Architecture.md` — deployment guidance
