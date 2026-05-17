# Hospital Management System — Technical Specification

> **Audience:** Infrastructure engineers, deployment automation, maintainers.
> **Canonical document.** This is the single source of truth for architecture, deployment, operations, and constraints. All other documentation is subordinate.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Infrastructure & Topology](#2-infrastructure--topology)
3. [Repository Structure](#3-repository-structure)
4. [Backend API](#4-backend-api)
5. [Database](#5-database)
6. [Deployment Pipeline](#6-deployment-pipeline)
7. [Service Management](#7-service-management)
8. [Security](#8-security)
9. [Operations](#9-operations)
10. [Constraints & Safeguards](#10-constraints--safeguards)
11. [Quick Reference](#11-quick-reference)

---

## 1. System Overview

Hospital Management System (HMS) is a three-tier application:

| Tier        | Technology                          | Location               |
|:------------|:------------------------------------|:-----------------------|
| Client      | Python 3.12 / Tkinter desktop app   | Hospital workstations  |
| API         | Flask 3.1 / Gunicorn / SQLAlchemy   | Briar (primary node)   |
| Database    | PostgreSQL 16.13                    | Briar (primary) + Sion (standby replica) |

### Communication Flow

```
Workstation (Tkinter) ──HTTP 5000──► Briar (Gunicorn + Flask)
                                          │
                                          ▼ SQLAlchemy
                                    PostgreSQL 16 Primary
                                          │
                                          │ WAL streaming
                                          ▼
                                    PostgreSQL 16 Standby (Sion, AWS EC2)
```

All inter-node traffic flows over **Tailscale overlay network** plus the hospital internal LAN.

---

## 2. Infrastructure & Topology

### 2.1 Node Inventory

| Hostname     | Role                | Tailscale IP     | OS                    | Location             |
|:-------------|:--------------------|:-----------------|:----------------------|:---------------------|
| **Briar**    | Primary node        | `100.78.155.2`   | Ubuntu Server 24.04   | Hospital datacenter  |
| **Sion**     | Secondary node      | `100.98.214.53`  | Ubuntu Server 24.04   | AWS EC2              |
| —            | Admin workstation   | —                | Windows 11            | Hospital LAN         |

### 2.2 Access

- **SSH user on all nodes:** `yerrazik`
- **Authentication:** Direct SSH key (no bastion, no jump host)
- **Sudo:** Password-protected. For automated deploys, `hms` user should have NOPASSWD sudo (configure manually or via Ansible).
- **Connectivity:** Tailscale + hospital internal LAN. No VPN.

### 2.3 Installed Software Versions

| Component        | Version      |
|:-----------------|:-------------|
| OS               | Ubuntu 24.04 LTS |
| Architecture     | x86_64       |
| Python           | 3.12         |
| PostgreSQL       | 16.13        |
| Ansible (Briar)  | Core 2.16.3  |

### 2.4 Service User

A dedicated system user `hms` owns the application directory and runs the API service:

```bash
useradd --system --home-dir /opt/hms --shell /usr/sbin/nologin hms
```

---

## 3. Repository Structure

```
hospital-management-project/
├── TECHINCAL_SPECIFICATION.md    # ← this document
├── .env.example                  # Environment variable template
├── server/
│   └── src/
│       ├── run.py                # Dev entry point (Flask dev server)
│       ├── wsgi.py               # Production entry point (Gunicorn target)
│       ├── requirements.txt      # Pinned Python dependencies
│       ├── .env                  # Local dev environment (gitignored)
│       ├── venv/                 # Local dev virtualenv (gitignored)
│       └── app/
│           ├── __init__.py       # create_app() factory, /health endpoint
│           ├── config.py         # DATABASE_URL, JWT_SECRET_KEY from env
│           ├── models.py         # 18 SQLAlchemy models
│           ├── routes/           # 20 Blueprints (auth, CRUD for all entities)
│           ├── services/         # Business logic per entity
│           └── utils/            # Utility modules
├── desktop/
│   └── src/
│       ├── main.py               # Tkinter entry point
│       ├── .env                  # API_BASE_URL=http://100.78.155.2:5000/api
│       ├── views/                # 12+ UI views
│       └── services/             # API client with caching
├── scripts/
│   ├── deploy/
│   │   ├── deploy.sh             # Versioned deploy (releases, rollback, smoke tests)
│   │   ├── deploy_standby.sh     # pg_basebackup for standby initialization
│   │   ├── setup_api.sh          # Virtualenv + dependency installer
│   │   └── README.md
│   ├── ops/
│   │   ├── backup.sh             # PostgreSQL backup script
│   │   ├── check_replication.sh  # Replication lag monitor
│   │   └── check_cert_expiry.sh  # TLS certificate expiry checker
│   ├── systemd/
│   │   └── hms-api.service       # systemd unit template (copied during deploy)
│   ├── logrotate/
│   │   └── hms                   # Log rotation config (copied during deploy)
│   ├── sql/
│   │   ├── schema.sql            # Full PostgreSQL schema (25 tables)
│   │   ├── security.sql          # RBAC roles, RLS, triggers, audit
│   │   └── initial_script.sql    # Admin user seed
│   ├── backup_database.py        # Python automated backup script
│   └── backup_wrapper.sh         # Cron wrapper for backup
├── deploy/
│   └── ansible/
│       ├── inventory.ini         # Briar + Sion Tailscale IPs
│       └── deploy_hms.yml        # Ansible playbook
└── docs/                         # Historical documentation (see §11.2)
```

### 3.1 Key Paths

| Path (in repo)                  | Purpose                         |
|:--------------------------------|:--------------------------------|
| `server/src/run.py`             | Flask dev server entry point    |
| `server/src/wsgi.py`            | Gunicorn production entry point |
| `server/src/app/__init__.py`    | App factory + `/health` route   |
| `server/src/app/config.py`      | Config from environment vars    |
| `server/src/requirements.txt`   | Pinned dependencies             |
| `scripts/deploy/deploy.sh`      | Versioned deploy automation     |
| `scripts/systemd/hms-api.service`| systemd unit for the API       |
| `.env.example`                  | Template for `/etc/hms.env`     |

---

## 4. Backend API

### 4.1 Technology Stack

| Component          | Library                  | Role                           |
|:-------------------|:-------------------------|:-------------------------------|
| Framework          | Flask 3.1.3              | HTTP API framework             |
| WSGI Server        | Gunicorn 23.0.0          | Production server (via systemd)|
| ORM                | SQLAlchemy 2.0.49        | Object-relational mapping      |
| Authentication     | Flask-JWT-Extended 4.7.1 | JWT token issuance/validation  |
| Password Hashing   | bcrypt 5.0.0             | Password storage               |
| Database Driver    | psycopg2-binary 2.9.12   | PostgreSQL connectivity        |
| CORS               | Flask-CORS 6.0.2         | Cross-origin support           |
| Config Loading     | python-dotenv 1.2.2      | `.env` file loader             |

Full pinned list: `server/src/requirements.txt`

### 4.2 Application Factory

Defined in `server/src/app/__init__.py`:

- `create_app()` instantiates Flask with `Config`, initializes `SQLAlchemy`, `JWTManager`, `CORS`.
- Registers a `/health` endpoint directly on the app (not behind `/api` prefix).
- Registers 20 route Blueprints under `/api/` prefix.
- Calls `db.create_all()` at startup to auto-create tables from SQLAlchemy models.

### 4.3 Entry Points

| Environment | Command                                  | File         |
|:------------|:-----------------------------------------|:-------------|
| Development | `python run.py`                          | `run.py`     |
| Production  | `gunicorn --bind 0.0.0.0:5000 wsgi:app`  | `wsgi.py`    |

- `run.py` uses Flask's built-in server on `0.0.0.0:5000` with `debug=False`.
- `wsgi.py` is a thin wrapper that calls `create_app()` — the target for Gunicorn.

### 4.4 Health Endpoint

```
GET /health
```

Response (200 OK):
```json
{
    "status": "healthy",
    "database": "connected",
    "timestamp": "2026-05-13T10:30:00+00:00"
}
```

On database failure returns 503 with `status: "degraded"`, `database: "disconnected"`.

### 4.5 API Routes

20 Blueprints registered with URL prefix `/api`:

| Blueprint          | Prefix                       | Auth Required |
|:-------------------|:-----------------------------|:--------------|
| auth_bp            | `/api/auth`                  | No (login/register) |
| maintenance_bp     | `/api/maintenance`           | Yes (JWT)     |
| dummy_bp           | `/api/dummy`                 | Yes (JWT)     |
| floor_bp           | `/api/floors`                | No            |
| room_bp            | `/api/rooms`                 | No            |
| operating_theater_bp | `/api/operating_theaters`  | No            |
| medical_device_bp  | `/api/medical_devices`       | No            |
| medical_specialty_bp | `/api/medical_specialties` | No            |
| patient_bp         | `/api/patients`              | No            |
| visit_bp           | `/api/visits`                | No            |
| scheduled_appointment_bp | `/api/scheduled_appointments` | No        |
| medication_bp      | `/api/medications`           | No            |
| prescription_bp    | `/api/prescriptions`         | No            |
| admission_bp       | `/api/admissions`            | No            |
| surgery_bp         | `/api/surgeries`             | No            |
| surgery_assistant_bp | `/api/surgery_assistants`  | No            |
| pharmacy_dispensation_bp | `/api/pharmacy_dispensations` | No        |
| dispensation_item_bp | `/api/dispensation_items`  | No            |
| radiology_exam_bp  | `/api/radiology_exams`       | No            |
| staff_bp           | `/api/staff`                 | No            |

**Note on auth enforcement:** Only `maintenance` and `dummy` blueprints currently enforce `@jwt_required()`. Other routes are open. This is a known gap for future hardening.

### 4.6 Dependencies

All production dependencies are pinned in `server/src/requirements.txt`. The file was cleaned up to remove unused packages (`dotenv`, `greenlet`, `colorama`) and add `gunicorn` and `psycopg2-binary`.

**System packages required during deploy:**
- `python3-venv` — virtualenv creation
- `build-essential` — native compilation
- `libpq-dev` — PostgreSQL client headers
- `git` — repository operations
- `rsync` — release creation

---

## 5. Database

### 5.1 Configuration

| Property     | Value                                       |
|:-------------|:--------------------------------------------|
| Engine       | PostgreSQL 16.13                            |
| Database     | `hsp_db`                                    |
| User         | `postgres`                                  |
| Port         | 5432                                        |
| Connection   | `DATABASE_URL` env var (e.g. `postgresql://postgres:password@localhost:5432/hsp_db`) |

### 5.2 Replication Topology

- **Primary:** Briar (`100.78.155.2:5432`) — read-write
- **Standby:** Sion (`100.98.214.53:5432`) — read-only, streaming replication
- **Replication method:** PostgreSQL native WAL streaming via `pg_basebackup`
- **Replication user:** `replicator` (configured in `pg_hba.conf` and `postgresql.conf`)

### 5.3 Schema Management

- **SQLAlchemy models** (18 models in `server/src/app/models.py`) are the Python-side schema definition.
- **SQL scripts** (`scripts/sql/schema.sql`, `security.sql`) contain the canonical production schema with additional features: RBAC roles, Row-Level Security (RLS), audit triggers, constraint triggers.
- `db.create_all()` runs at every startup in the Flask app factory. In production the SQL scripts are applied separately — the Python models must remain compatible with the production schema.

### 5.4 Critical Restriction

> **DO NOT modify SQL schema scripts, PostgreSQL configuration, or apply migrations that could break replication.**
>
> This includes but is not limited to:
> - Editing `scripts/sql/schema.sql`
> - Editing `scripts/sql/security.sql`
> - Editing `scripts/sql/initial_script.sql`
> - Altering PostgreSQL `postgresql.conf` or `pg_hba.conf`
> - Running DDL that could cause replication conflicts
> - Adding or removing tables, columns, or constraints via migration scripts
>
> All schema changes must be evaluated for replication impact before execution.

---

## 6. Deployment Pipeline

### 6.1 Principles

- **Branch:** `main` — no staging/production branches, no release branches
- **Policy:** Direct commits to `main` (no PR requirement, no CI gate)
- **Repository:** GitHub (`https://github.com/yosseferrazik/hospital-management-project.git`)
- **Access:** SSH keys configured on both nodes
- **Automation:** Semi-automated via Bash (`deploy.sh`); Ansible available as future enhancement
- **Window:** Deploys restricted to morning window (06:00–10:00) or night window (20:00–23:00). Override with `--force`.

### 6.2 Filesystem Layout

```
/opt/hms/
├── repo/                        # Git clone (persistent, used for pulls)
├── releases/
│   ├── a1b2c3d/                 # Each release = full copy of repo at a commit
│   ├── e4f5678/
│   └── ...
├── current → releases/a1b2c3d/  # Symlink to active release
├── venv/                        # Shared Python virtualenv
├── scripts/                     # (symlinked from current/scripts or copied)
├── .deploy_meta                 # Metadata for rollback tracking
└── deploy.sh → current/scripts/deploy/deploy.sh  # Convenience symlink
```

### 6.3 Deploy Script: `scripts/deploy/deploy.sh`

**Usage:**
```bash
sudo bash scripts/deploy/deploy.sh              # normal (window-checked)
sudo bash scripts/deploy/deploy.sh --force       # bypass time window
sudo bash scripts/deploy/deploy.sh --rollback    # revert to previous release
```

**Flow (normal deploy):**

1. **Time window check** — aborts if outside window (unless `--force`)
2. **Install system packages** — `python3-venv`, `build-essential`, `libpq-dev`, `git`, `rsync` (idempotent)
3. **Ensure `hms` user** — creates system user if absent
4. **Ensure directories** — `/opt/hms/releases/`, `/var/log/hms`
5. **Clone or pull repo** — into `/opt/hms/repo`
6. **Get commit SHA** — `git rev-parse --short HEAD`
7. **Skip if current** — checks `.deploy_meta`; exits early if same SHA already deployed
8. **Create release** — `rsync` from repo to `/opt/hms/releases/<sha>` (skips `venv/`, `*.pyc`, `__pycache__`)
9. **Update symlink** — `ln -sfn /opt/hms/releases/<sha> /opt/hms/current`
10. **Setup venv** — creates `/opt/hms/venv` if absent; `pip install -r requirements.txt`
11. **Install systemd unit** — copies `scripts/systemd/hms-api.service` to `/etc/systemd/system/`
12. **Install logrotate** — copies `scripts/logrotate/hms` to `/etc/logrotate.d/hms`
13. **Restart service** — `systemctl restart hms-api`
14. **Smoke test** — `curl -f http://localhost:5000/health` with 5 retries at 3-second intervals
15. **On success:** save metadata to `.deploy_meta`, clean old releases (>5 removed)
16. **On failure:** revert symlink to previous release, restart service, re-run smoke test; if that also fails — **CRITICAL** — manual intervention required

### 6.4 Rollback

```bash
sudo bash scripts/deploy/deploy.sh --rollback
```

Reads `PREVIOUS_RELEASE` from `/opt/hms/.deploy_meta`, switches the symlink, restarts the service, and runs the smoke test. If the smoke test fails, the rollback is marked as failed and requires manual intervention.

### 6.5 Ansible Playbook

Located at `deploy/ansible/deploy_hms.yml`:

```bash
cd deploy/ansible
ansible-playbook -i inventory.ini deploy_hms.yml
```

The playbook:
1. Installs system packages on the primary
2. Creates `hms` user and directory structure
3. Clones/updates the repository
4. Runs `deploy.sh --force` on the primary
5. (Standby play) Installs PostgreSQL 16 and runs `deploy_standby.sh`

**Inventory** (`deploy/ansible/inventory.ini`):
```ini
[primary]
primary ansible_host=100.78.155.2

[standby]
standby ansible_host=100.98.214.53

[all:vars]
ansible_user=yerrazik
ansible_python_interpreter=/usr/bin/python3
```

### 6.6 Standby Initialization

`scripts/deploy/deploy_standby.sh`:

```bash
PRIMARY_IP=100.78.155.2 sudo bash scripts/deploy/deploy_standby.sh
```

Stops PostgreSQL, clears the data directory, runs `pg_basebackup` from the primary with the `-R` flag (writes `standby.signal`), then starts PostgreSQL. Requires the `replicator` user and `pg_hba.conf` to be pre-configured on the primary.

---

## 7. Service Management

### 7.1 systemd Unit: `hms-api.service`

**Template:** `scripts/systemd/hms-api.service`

```ini
[Unit]
Description=Hospital Management System API (hms-api)
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=hms
Group=hms
WorkingDirectory=/opt/hms/current/server/src
EnvironmentFile=/etc/hms.env
ExecStart=/opt/hms/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 \
    --access-logfile /var/log/hms/access.log \
    --error-logfile /var/log/hms/error.log wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Key properties:**
- Runs as `hms` user
- Reads secrets from `/etc/hms.env`
- Auto-restarts on failure or crash (`Restart=always`)
- Logs to both journald (`journalctl -u hms-api`) and Gunicorn log files (`/var/log/hms/access.log`, `error.log`)

### 7.2 Common Commands

```bash
sudo systemctl status hms-api              # Check service status
sudo systemctl restart hms-api              # Restart the API
sudo systemctl enable --now hms-api         # Enable at boot + start
sudo journalctl -u hms-api -n 100 -f       # Tail service logs
sudo journalctl -u hms-api --since "5 min ago"  # Recent logs
tail -f /var/log/hms/error.log             # Gunicorn error log
```

### 7.3 Log Rotation

Installed to `/etc/logrotate.d/hms`:

```
/var/log/hms/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    dateext
    dateformat -%Y%m%d
}
```

---

## 8. Security

### 8.1 Secrets Management

All secrets stored in `/etc/hms.env` (owned by `root:root`, mode `600`):

```bash
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/hsp_db
JWT_SECRET_KEY=<hex-256-bit-key>
```

**Template:** `.env.example` at the repository root.

**Generation:**
```bash
# Generate a secure JWT secret
openssl rand -hex 32
```

**Important:** Never commit real secrets to the repository. The `server/src/.env` file is gitignored.

### 8.2 Network Security

- **API:** Bound to `0.0.0.0:5000` — accessible on hospital LAN and Tailscale. **Not exposed to the public internet.**
- **PostgreSQL:** Port 5432 — not exposed publicly; accessible only via Tailscale or LAN.
- **SSH:** Port 22 — accessible to admins via Tailscale.
- **Future:** Nginx reverse proxy planned in front of Gunicorn for TLS termination (Let's Encrypt).

### 8.3 Firewall (UFW)

If UFW is active, ensure these rules:

```bash
sudo ufw allow from 192.168.0.0/16 to any port 5000 proto tcp  # Hospital LAN
sudo ufw allow from 100.64.0.0/10 to any port 5000 proto tcp   # Tailscale
```

### 8.4 Authentication

- JWT tokens issued at `/api/auth/login`
- Token required for protected routes (`maintenance`, `dummy`)
- Password hashing via `bcrypt`
- Default admin seed: `scripts/sql/initial_script.sql`
- **Known gap:** JWT enforcement is not applied to 18 of 20 route blueprints. This is acceptable for the current internal-network deployment posture but should be addressed before any public exposure.

---

## 9. Operations

### 9.1 Backup

Backup strategy is documented in the canonical runbook at:
`docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md`

**Scripts:**
- `scripts/ops/backup.sh` — `pg_dump`-based backup with rotation
- `scripts/backup_database.py` — Python automated backup with metadata tracking
- `scripts/backup_wrapper.sh` — Cron wrapper

### 9.2 Monitoring

| Check                    | Method                            |
|:-------------------------|:----------------------------------|
| API health               | `curl -f http://localhost:5000/health` |
| Service status           | `systemctl status hms-api`        |
| Replication lag          | `scripts/ops/check_replication.sh` |
| Certificate expiry       | `scripts/ops/check_cert_expiry.sh` |
| API logs                 | `/var/log/hms/access.log`, `error.log` |

### 9.3 Deployment Smoke Test

Performed automatically by `deploy.sh`:

```bash
curl -f http://localhost:5000/health
```

5 retries with 3-second intervals. The endpoint must return HTTP 200 for the deploy to be considered successful.

### 9.4 Deploy Windows

| Window        | Hours              |
|:--------------|:-------------------|
| Morning       | 06:00 – 10:00      |
| Night         | 20:00 – 23:00      |

Use `--force` to bypass. Intended to prevent accidental deploys during peak clinical hours.

---

## 10. Constraints & Safeguards

### 10.1 Critical Restrictions

| # | Restriction                                              | Rationale                        |
|:-:|:---------------------------------------------------------|:---------------------------------|
| 1 | **DO NOT** modify SQL schema scripts or PostgreSQL configuration. | Would break replication or schema consistency. |
| 2 | **DO NOT** apply unverified DDL on the primary.         | Could cause replication conflicts or data loss. |
| 3 | **DO NOT** expose PostgreSQL port 5432 to the public internet. | Security requirement. |
| 4 | **DO NOT** commit real secrets (`.env`, credentials).   | Repository is not a secret store. |
| 5 | **DO NOT** run `deploy.sh` without `sudo`.               | Script requires root for system operations. |
| 6 | **DO NOT** modify the `/opt/hms/current` symlink manually during a deploy. | Causes race conditions with the deploy script. |

### 10.2 Implicit Decisions (Explicitified)

| Decision | Rationale |
|:---------|:----------|
| Releases are identified by commit SHA (not semver). | Simple, deterministic, no version-management overhead. |
| Virtualenv is shared across releases (not per-release). | Saves disk space and install time; all releases share compatible dependencies. |
| Gunicorn runs with 4 workers. | Matches the 4 vCPU of the primary node. Adjust if CPU changes. |
| Old releases >5 are pruned automatically. | Balances rollback depth with disk usage. |
| Deploy script clones repo to `/opt/hms/repo`. | Decouples the git working tree from the active release. |
| No Docker. | Not installed; OS-level process management via systemd is sufficient for the current scale. |
| No CI/CD pipeline. | Deploy is semi-automated via `deploy.sh`; Ansible is available as an optional layer. |
| No reverse proxy (yet). | API is internal-only; Nginx + Let's Encrypt planned for future. |
| Database migrations use `db.create_all()`. | Acceptable for current schema maturity; Alembic may be introduced later. |
| `psycopg2-binary` used instead of `psycopg2`. | Avoids native compilation at deploy time; acceptable for production at current scale. |

---

## 11. Quick Reference

### 11.1 Command Cheatsheet

```bash
# ─── First-time deploy ───────────────────────────────────────────
git clone https://github.com/yosseferrazik/hospital-management-project.git /opt/hms/repo
sudo bash /opt/hms/repo/scripts/deploy/deploy.sh --force

# ─── Subsequent deploys ──────────────────────────────────────────
sudo bash /opt/hms/repo/scripts/deploy/deploy.sh
sudo bash /opt/hms/repo/scripts/deploy/deploy.sh --force   # bypass window

# ─── Rollback ────────────────────────────────────────────────────
sudo bash /opt/hms/current/scripts/deploy/deploy.sh --rollback

# ─── Service management ──────────────────────────────────────────
sudo systemctl status hms-api
sudo systemctl restart hms-api
sudo journalctl -u hms-api -f

# ─── Health check ────────────────────────────────────────────────
curl -f http://localhost:5000/health

# ─── Ansible (from admin node's WSL or Briar itself) ─────────────
cd deploy/ansible
ansible-playbook -i inventory.ini deploy_hms.yml

# ─── Standby setup ───────────────────────────────────────────────
# On Sion:
PRIMARY_IP=100.78.155.2 sudo bash scripts/deploy/deploy_standby.sh

# ─── Secrets setup ───────────────────────────────────────────────
sudo cp .env.example /etc/hms.env
sudo chmod 600 /etc/hms.env
sudo nano /etc/hms.env   # fill DATABASE_URL and JWT_SECRET_KEY
```

### 11.2 Document Hierarchy

| Document | Status | Purpose |
|:---------|:-------|:--------|
| `TECHNICAL_SPECIFICATION.md` | **Canonical** | Single source of truth for architecture, deploy, operations |
| `docs/` | **Historical** | Contains planning docs, runbooks, manuals — may contain outdated information; cross-reference with this spec |
| `scripts/deploy/README.md` | Active | Deploy script usage |
| `scripts/ops/README.md` | Active | Operations helper usage |
| `scripts/README.md` | Active | Scripts directory overview |
