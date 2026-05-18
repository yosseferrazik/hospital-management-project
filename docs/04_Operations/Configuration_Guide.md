# Configuration Guide — Hospital Management System

## Database

The PostgreSQL database name is **`hsp_db`** and must never be changed.

| Property     | Value                                          |
|--------------|------------------------------------------------|
| Engine       | PostgreSQL 16+                                 |
| Database     | `hsp_db`                                       |
| Port         | 5432                                           |
| Connection   | `DATABASE_URL` environment variable            |

---

## Environment Variables

### Required (all environments)

| Variable          | Description                         | Example                                                      |
|-------------------|-------------------------------------|--------------------------------------------------------------|
| `DATABASE_URL`    | PostgreSQL connection string        | `postgresql://postgres:password@localhost:5432/hsp_db`       |
| `JWT_SECRET_KEY`  | 256-bit hex key for JWT signing     | `a1b2c3d4...` (generate via `openssl rand -hex 32`)          |
| `DB_NAME`         | Database name (must be `hsp_db`)    | `hsp_db`                                                     |

### Optional — Backup Script

| Variable              | Default            | Description                     |
|-----------------------|--------------------|---------------------------------|
| `HMS_DB_HOST`         | `localhost`        | PostgreSQL host                 |
| `HMS_DB_PORT`         | `5432`             | PostgreSQL port                 |
| `HMS_DB_USER`         | `backup_user`      | Backup database user            |
| `HMS_BACKUP_DIR`      | `/backups/local`   | Local backup directory          |
| `HMS_LOG_FILE`        | `/var/log/hms_backup.log` | Log file path           |
| `HMS_RETENTION_DAYS`  | `5`                | Days to retain backups          |
| `HMS_STANDBY_HOST`    | (none)             | Standby host for rsync          |

### Desktop Client

| Variable         | Default                           | Description          |
|------------------|-----------------------------------|----------------------|
| `API_BASE_URL`   | `http://localhost:5000/api`       | Backend API base URL |

---

## Technology Stack Reference

| Layer             | Technology                        | Role                              |
|-------------------|-----------------------------------|-----------------------------------|
| Language          | Python 3.12                       | Full-stack language               |
| API Framework     | Flask 3.1.3                       | REST API framework                |
| WSGI Server       | Gunicorn 23.0.0                   | Production server (via systemd)   |
| ORM               | SQLAlchemy 2.0.49                 | Object-relational mapping         |
| Authentication    | Flask-JWT-Extended 4.7.1          | JWT token issuance/validation     |
| Password Hashing  | bcrypt 5.0.0                      | Password storage                  |
| Database Driver   | psycopg2-binary 2.9.12            | PostgreSQL connectivity           |
| CORS              | Flask-CORS 6.0.2                  | Cross-origin support              |
| Desktop Client    | tkinter + requests                | GUI + HTTP client                 |
| Test Data         | Faker                             | Synthetic data generation         |
| Config Loading    | python-dotenv 1.2.2               | `.env` file loader                |

---

## Environment File Locations

| Environment | File                        | Owner     | Mode |
|-------------|-----------------------------|-----------|------|
| Production  | `/etc/hms.env`              | `root`    | `600` |
| Development | `server/src/.env`           | dev user  | `644` |
| Development | `desktop/src/.env`          | dev user  | `644` |

Copy the template from the project root:

```bash
sudo cp .env.example /etc/hms.env
sudo chmod 600 /etc/hms.env
sudo nano /etc/hms.env
```

---

## Ports

| Service    | Port | Protocol | Bind           |
|------------|------|----------|----------------|
| API        | 5000 | HTTP     | `0.0.0.0`     |
| PostgreSQL | 5432 | TCP      | `127.0.0.1`   |

---

## Logging

| Log                    | Location                   |
|------------------------|----------------------------|
| API access log         | `/var/log/hms/access.log`  |
| API error log          | `/var/log/hms/error.log`   |
| systemd journal        | `journalctl -u hms-api`    |
| Backup log             | `/var/log/hms_backup.log`  |

Log rotation is configured at `/etc/logrotate.d/hms` (daily, 14-day retention, compressed).

---

## Production Secrets

Generate a secure JWT secret:

```bash
openssl rand -hex 32
```

Set a strong PostgreSQL password:

```bash
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'your-strong-password';"
```

Update `/etc/hms.env`:

```
DATABASE_URL=postgresql://postgres:your-strong-password@localhost:5432/hsp_db
JWT_SECRET_KEY=<output from openssl command>
DB_NAME=hsp_db
```
