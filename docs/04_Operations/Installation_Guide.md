# Installation Guide — Hospital Management System

## Prerequisites

- **Python 3.10+** (3.12 recommended)
- **PostgreSQL 16+**
- **Git**
- Supported platforms: Windows 10/11, Linux (Ubuntu 24.04 LTS recommended), macOS

---

## 1. Clone the Repository

```bash
git clone https://github.com/yosseferrazik/hospital-management-project.git
cd hospital-management-project
```

## 2. Database Setup

Create the database. The name **must be `hsp_db`** — do not change it.

```bash
sudo -u postgres psql -c "CREATE DATABASE hsp_db;"
```

Apply the schema and security scripts:

```bash
sudo -u postgres psql -d hsp_db -f scripts/sql/schema.sql
sudo -u postgres psql -d hsp_db -f scripts/sql/security.sql
sudo -u postgres psql -d hsp_db -f scripts/sql/initial_script.sql
```

## 3. Backend API Setup

### Virtual environment

```bash
cd server/src
python3 -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

### Environment configuration

Create `server/src/.env` (or copy from the root `.env.example`):

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/hsp_db
JWT_SECRET_KEY=$(openssl rand -hex 32)
DB_NAME=hsp_db
```

Alternatively, set environment variables directly:

```bash
# Linux/Mac
export DATABASE_URL='postgresql://postgres:password@localhost:5432/hsp_db'
export JWT_SECRET_KEY='your-secret-key'
export DB_NAME=hsp_db

# Windows PowerShell
$env:DATABASE_URL = 'postgresql://postgres:password@localhost:5432/hsp_db'
$env:JWT_SECRET_KEY = 'your-secret-key'
$env:DB_NAME = 'hsp_db'
```

### Run the development server

```bash
python run.py
```

The API starts at `http://0.0.0.0:5000`. Verify:

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{"status": "healthy", "database": "connected", "timestamp": "2026-05-18T10:00:00+00:00"}
```

## 4. Desktop Client Setup

```bash
cd desktop/src
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `desktop/src/.env`:

```
API_BASE_URL=http://localhost:5000/api
DB_NAME=hsp_db
```

Run the client:

```bash
python main.py
```

> The GUI uses `tkinter`, which is included with standard Python installations on Windows. On Ubuntu, install it with `sudo apt install python3-tk`.

## 5. Verify the Installation

| Check | Command |
|-------|---------|
| API health | `curl http://localhost:5000/health` |
| Database tables | `sudo -u postgres psql -d hsp_db -c "\dt"` |
| Desktop app | Window titled "Sa Palomera Hospital - Management System" opens |

## Default Credentials

After running `initial_script.sql`:

- **Username:** `yossef`
- **Password:** `ChangeMePleaseChange!`

Change the password on first login.

## Common Troubleshooting

| Issue | Solution |
|-------|----------|
| Database connection errors | Verify `DATABASE_URL`, ensure PostgreSQL is running, check schema was applied |
| Missing Python packages | Activate virtual environment and re-run `pip install -r requirements.txt` |
| GUI issues (`tkinter`) | Verify `tkinter` is installed: `python -m tkinter` |
| Module not found | Ensure you're running from `server/src/` or `desktop/src/` directory |
