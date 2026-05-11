# Backup and Restore Runbook

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Complete     |
| Version        | 3.0          |
| Last Updated   | 2026-05-06   |

## Purpose

This runbook defines operational backup and restore procedures for the Hospital Management System database. It covers both manual procedures and an automated Python + Cron-based backup system suitable for lab and future deployments.

The Hospital Management System uses PostgreSQL as its primary data store for all operational hospital data including patients, staff, surgeries, visits, admissions, medications, and related clinical records. Backups are critical for disaster recovery, data protection, and compliance with healthcare data preservation requirements.

## System Architecture Context

**Application Stack:**

- Desktop Client: Python tkinter application for staff interaction
- Backend API: Flask REST service on port 5000
- Database: PostgreSQL (default port 5432)
- Deployment Model: Current development uses local/lab setup; target deployment uses separate application and data nodes

**Backup Topology:**

- Primary backup node: Same host as PostgreSQL primary (active writes)
- Secondary backup node: Optional standby with replicated data
- Backup storage: Local retention on primary node + external/off-site copy

**Data Criticality:**
All tables contain operational clinical data subject to healthcare privacy regulations. Standard backup retention: 5 most recent daily backups locally, plus 1 weekly off-site copy.

## Scope

This runbook covers:

- Manual logical backups of the PostgreSQL database
- Automated backup using Python scripting and Cron scheduling
- Backup file validation and integrity checks
- Full database restoration procedures
- Targeted restoration for specific tables
- Post-restore validation steps
- Off-site backup replication
- Operational precautions for sensitive healthcare data

Focus on the database layer as PostgreSQL is the system of record for operational data.

## Backup Policy Framework

| Area            | Standard                                                                    |
|:--------------- |:--------------------------------------------------------------------------- |
| Backup Type     | Logical PostgreSQL backup (custom format for flexibility)                   |
| Automation      | Python script scheduled via Cron (daily at 02:00 UTC)                       |
| Frequency       | Daily automated backups                                                     |
| Local Retention | Keep the five most recent daily backups                                     |
| Weekly Archive  | One backup per week retained separately for longer-term recovery            |
| Off-site Copy   | Automated copy of weekly backup to external storage or remote node          |
| Protection      | File permissions restricted; optional encryption for sensitive environments |
| Recovery Target | RTO 2-4 hours, RPO 1 hour for critical data                                 |

## Roles and Responsibilities

| Role                   | Responsibility                                                         |
|:---------------------- |:---------------------------------------------------------------------- |
| System Administrator   | Deploys and maintains backup scripts; monitors automation health       |
| Database Administrator | Validates backup integrity; leads restore operations; tests procedures |
| DevOps/Infrastructure  | Manages backup storage, off-site replication, and monitoring alerts    |
| Project Team           | Updates procedures when database schema or infrastructure changes      |

## Environment Configuration

The backup system requires the following environment setup:

| Variable         | Example Value                          | Description                                  |
|:---------------- |:-------------------------------------- |:-------------------------------------------- |
| `DB_NAME`        | `hospital_management`                  | PostgreSQL database name                     |
| `DB_HOST`        | `localhost` or `vm-hms-primary.local`  | PostgreSQL host                              |
| `DB_PORT`        | `5432`                                 | PostgreSQL port                              |
| `DB_USER`        | `backup_user`                          | PostgreSQL user with backup privilege        |
| `DB_PASSWORD`    | (via `.pgpass` or environment)         | Database user password (secure storage only) |
| `BACKUP_DIR`     | `/backups/local` or `/var/backups/hms` | Local backup directory                       |
| `BACKUP_ARCHIVE` | `/backups/archive` or remote path      | Weekly archive directory (optional)          |
| `LOG_FILE`       | `/var/log/hms_backup.log`              | Backup operation log                         |

## Manual Backup Procedure

### 1. Prepare the Backup Location

- Ensure the backup directory exists and has restrictive permissions (700 or equivalent).
- Ensure only authorized users can read or modify the directory.
- Ensure there is enough free space for the new backup file.
- Ensure the backup directory is on a separate filesystem from the PostgreSQL data directory.

Recommended directory setup on Linux:

```bash
sudo mkdir -p /backups/local
sudo chown postgres:postgres /backups/local
sudo chmod 700 /backups/local
```

### 2. Create a Logical Backup

Preferred method using PostgreSQL custom format (most flexible for restoration):

```bash
pg_dump -h <db_host> -p <db_port> -U <db_user> -d <db_name> \
  -F c -v -f /backups/local/hospital_management_$(date +\%Y\%m\%d_\%H\%M\%S).dump
```

Alternative plain SQL format (human-readable, for specific audit scenarios):

```bash
pg_dump -h <db_host> -p <db_port> -U <db_user> -d <db_name> \
  -F p -f /backups/local/hospital_management_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

Standard naming pattern:

```text
hospital_management_YYYYMMDD_HHMMSS.dump    # Custom format
hospital_management_YYYYMMDD_HHMMSS.sql     # Plain text format
```

### 3. Verify Backup Creation

After backup completes:

```bash
# Check file exists and has reasonable size
ls -lh /backups/local/hospital_management_*.dump | head -5

# Inspect custom-format backup structure
pg_restore -l /backups/local/hospital_management_YYYYMMDD_HHMMSS.dump | head -20

# For plain SQL backups, verify content
wc -l /backups/local/hospital_management_YYYYMMDD_HHMMSS.sql
head -50 /backups/local/hospital_management_YYYYMMDD_HHMMSS.sql
```

### 4. Manual Retention Management

Keep the five most recent local backups; remove older ones:

```bash
# List all backups sorted by date
ls -lt /backups/local/hospital_management_*.dump

# Remove backups older than 5 most recent (example)
cd /backups/local
ls -t hospital_management_*.dump | tail -n +6 | xargs rm -f
```

---

## Quick Start: Deploy Backup System (Step-by-step)

These steps allow a system administrator at Hospital Sa Palomera to deploy the automated backup system for the Hospital Management System from a clean Ubuntu 22.04 node. Run each command as a privileged user (sudo) unless noted.

1) Install required packages

```bash
sudo apt update
sudo apt install -y postgresql-client python3 python3-pip awscli gnupg
sudo pip3 install boto3
```

2) Create directories and set permissions

```bash
# Create script and backup directories
sudo mkdir -p /opt/hms/scripts /backups/local /backups/archive
sudo chown -R postgres:postgres /backups/local /backups/archive
sudo chmod 700 /backups/local /backups/archive

# Create log directory
sudo touch /var/log/hms_backup.log
sudo chown postgres:postgres /var/log/hms_backup.log
sudo chmod 640 /var/log/hms_backup.log
```

3) Create a PostgreSQL backup user (optional but recommended)

Run on the PostgreSQL primary as the postgres superuser:

```bash
sudo -u postgres psql -c "CREATE USER backup_user WITH PASSWORD 'secure_backup_password';"
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE hospital_management TO backup_user;"
sudo -u postgres psql -c "GRANT USAGE ON SCHEMA public TO backup_user;"
sudo -u postgres psql -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;"
```

4) Configure `.pgpass` for non-interactive authentication (on the backup operator account)

Create `/var/lib/postgresql/.pgpass` or `/home/backup/.pgpass` for the OS user that will run backups (commonly `postgres`):

```bash
sudo -u postgres bash -c 'echo "localhost:5432:hospital_management:backup_user:secure_backup_password" > ~/.pgpass'
sudo -u postgres chmod 600 ~/.pgpass
```

5) Deploy the Python backup script

Create `/opt/hms/scripts/backup_database.py` with the content provided in this runbook (the full script appears later in this file). Then:

```bash
sudo chown postgres:postgres /opt/hms/scripts/backup_database.py
sudo chmod 750 /opt/hms/scripts/backup_database.py
```

6) Create wrapper script for environment variables

Create `/opt/hms/scripts/backup_wrapper.sh` with the example env vars (provided earlier). Make it executable:

```bash
sudo chown root:root /opt/hms/scripts/backup_wrapper.sh
sudo chmod 750 /opt/hms/scripts/backup_wrapper.sh
```

7) Add Cron job (as root or backup operator)

Edit root crontab (`sudo crontab -e`) and add:

```cron
0 2 * * * /bin/bash /opt/hms/scripts/backup_wrapper.sh >> /var/log/hms_backup_cron.log 2>&1
```

8) Test the backup manually

Run the script interactively as the postgres user and inspect logs:

```bash
sudo -u postgres /usr/bin/python3 /opt/hms/scripts/backup_database.py
tail -n 200 /var/log/hms_backup.log
ls -lt /backups/local/
cat /backups/local/.metadata.json | python3 -m json.tool
```

9) Test restore to a validation database

```bash
# Select latest backup
BACKUP_FILE=$(ls -t /backups/local/hospital_management_*.dump | head -1)

sudo -u postgres createdb hospital_management_test
sudo -u postgres pg_restore -h localhost -U postgres -d hospital_management_test $BACKUP_FILE

sudo -u postgres psql -d hospital_management_test -c "SELECT COUNT(*) FROM patients;"
sudo -u postgres dropdb hospital_management_test
```

10) (Optional) Configure AWS S3 upload

If using AWS S3, ensure AWS CLI is configured with an IAM user that has PutObject permission to the designated bucket. Run a test upload:

```bash
aws s3 cp /backups/local/$(basename $BACKUP_FILE) s3://hms-backups/daily/ --sse AES256
aws s3 ls s3://hms-backups/daily/ --recursive | tail -n 10
```

---

## Systemd service and timer (recommended)

Instead of cron, the primary node uses a systemd timer to run backups daily at 02:00. The deploy_primary.sh script installs `hms-backup.service` and `hms-backup.timer` which execute `/opt/hms/scripts/backup.sh` as the `postgres` user. To check status:

```bash
sudo systemctl status hms-backup.timer
sudo journalctl -u hms-backup.service -n 200
```


## Automated Backup System (Python + Cron)

The recommended approach for production-like deployments uses a Python script scheduled via Cron. This ensures consistent, unattended backup execution with logging and retention management.

### Setup: Create Backup User (One-time)

Create a PostgreSQL user with minimal backup-only privilege:

```sql
-- Connect as PostgreSQL superuser
CREATE USER backup_user WITH PASSWORD 'secure_backup_password';
GRANT CONNECT ON DATABASE hospital_management TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;

-- Optional: further restrict to read-only
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
```

Or use OS-level passwordless authentication (`.pgpass`):

```bash
# As the backup operator user (e.g., postgres or hms_backup)
cat ~/.pgpass
# Format: hostname:port:database:username:password
localhost:5432:hospital_management:backup_user:secure_backup_password

chmod 600 ~/.pgpass
```

### Setup: Create Backup Script

Create `/opt/hms/scripts/backup_database.py` (or adjust path as appropriate):

```python
#!/usr/bin/env python3
"""
HMS Database Backup Automation Script

Performs daily PostgreSQL logical backups with retention management,
logging, and optional off-site replication.

Supports Cron execution with environment variable configuration.
"""

import os
import sys
import subprocess
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configuration from environment or defaults
DB_NAME = os.getenv('HMS_DB_NAME', 'hospital_management')
DB_HOST = os.getenv('HMS_DB_HOST', 'localhost')
DB_PORT = os.getenv('HMS_DB_PORT', '5432')
DB_USER = os.getenv('HMS_DB_USER', 'backup_user')
BACKUP_DIR = os.getenv('HMS_BACKUP_DIR', '/backups/local')
BACKUP_ARCHIVE_DIR = os.getenv('HMS_BACKUP_ARCHIVE_DIR', '/backups/archive')
LOG_FILE = os.getenv('HMS_LOG_FILE', '/var/log/hms_backup.log')
RETENTION_DAYS = int(os.getenv('HMS_RETENTION_DAYS', '5'))
ARCHIVE_DAY_OF_WEEK = int(os.getenv('HMS_ARCHIVE_DAY', '0'))  # 0=Sunday
ENABLE_ARCHIVE = os.getenv('HMS_ENABLE_ARCHIVE', 'true').lower() == 'true'

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_backup():
    """Execute PostgreSQL backup using pg_dump."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"{DB_NAME}_{timestamp}.dump"
    backup_filepath = os.path.join(BACKUP_DIR, backup_filename)

    # Ensure backup directory exists
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)

    # Build pg_dump command
    cmd = [
        'pg_dump',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '-F', 'c',  # Custom format for flexibility
        '-v',       # Verbose output
        '-f', backup_filepath
    ]

    try:
        logger.info(f"Starting backup to {backup_filepath}...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Verify backup file
        if not os.path.exists(backup_filepath):
            raise FileNotFoundError(f"Backup file not created: {backup_filepath}")

        file_size_mb = os.path.getsize(backup_filepath) / (1024 * 1024)
        logger.info(f"Backup completed successfully: {backup_filename} ({file_size_mb:.2f} MB)")

        # Log backup metadata
        metadata = {
            'timestamp': timestamp,
            'filename': backup_filename,
            'filepath': backup_filepath,
            'size_bytes': os.path.getsize(backup_filepath),
            'size_mb': file_size_mb,
            'status': 'success'
        }
        log_backup_metadata(metadata)

        return backup_filepath, True

    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed: {e.stderr}")
        return None, False
    except Exception as e:
        logger.error(f"Unexpected error during backup: {e}")
        return None, False


def cleanup_old_backups():
    """Remove backups older than RETENTION_DAYS."""
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    deleted_count = 0

    try:
        logger.info(f"Cleaning up backups older than {RETENTION_DAYS} days...")

        for backup_file in Path(BACKUP_DIR).glob(f"{DB_NAME}_*.dump"):
            # Extract timestamp from filename
            try:
                file_timestamp_str = backup_file.stem.replace(f"{DB_NAME}_", "")
                file_timestamp = datetime.strptime(file_timestamp_str, '%Y%m%d_%H%M%S')

                if file_timestamp < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {backup_file.name}")
            except ValueError:
                # Skip files that don't match naming pattern
                logger.debug(f"Skipping non-standard filename: {backup_file.name}")

        logger.info(f"Cleanup complete: {deleted_count} old backups removed")
        return True

    except Exception as e:
        logger.error(f"Error during backup cleanup: {e}")
        return False


def archive_weekly_backup(backup_filepath):
    """Copy latest backup to weekly archive if today is archive day."""
    today_dow = datetime.now().weekday()  # 0=Monday, 6=Sunday

    # Convert ARCHIVE_DAY_OF_WEEK from Sunday=0 to Python's Monday=0 format
    py_archive_day = (ARCHIVE_DAY_OF_WEEK + 6) % 7

    if today_dow != py_archive_day or not ENABLE_ARCHIVE:
        return True

    try:
        logger.info(f"Archiving backup for off-site storage...")
        Path(BACKUP_ARCHIVE_DIR).mkdir(parents=True, exist_ok=True)

        # Copy backup to archive with week number
        week_number = datetime.now().strftime('%Y_W%V')  # e.g., 2026_W18
        archive_filename = backup_filepath.split('/')[-1].replace('.dump', f'_WEEK{week_number}.dump')
        archive_filepath = os.path.join(BACKUP_ARCHIVE_DIR, archive_filename)

        cmd = ['cp', backup_filepath, archive_filepath]
        subprocess.run(cmd, check=True)

        logger.info(f"Backup archived: {archive_filename}")
        return True

    except Exception as e:
        logger.error(f"Error archiving backup: {e}")
        # Don't fail the whole backup on archive error
        return False


def verify_backup(backup_filepath):
    """Validate backup integrity by listing archive contents."""
    try:
        logger.info(f"Verifying backup integrity...")
        cmd = ['pg_restore', '-l', backup_filepath]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Count objects in backup
        object_count = len([line for line in result.stdout.split('\n') if line.strip()])
        logger.info(f"Backup verification successful: {object_count} objects found")
        return True

    except Exception as e:
        logger.error(f"Backup verification failed: {e}")
        return False


def log_backup_metadata(metadata):
    """Log backup metadata to JSON file for monitoring."""
    try:
        metadata_file = os.path.join(BACKUP_DIR, '.metadata.json')

        # Append to metadata log (or create if doesn't exist)
        existing_data = []
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                existing_data = json.load(f)

        existing_data.append(metadata)

        # Keep only last 30 backup records
        if len(existing_data) > 30:
            existing_data = existing_data[-30:]

        with open(metadata_file, 'w') as f:
            json.dump(existing_data, f, indent=2)

    except Exception as e:
        logger.warning(f"Could not log backup metadata: {e}")


def main():
    """Main backup execution flow."""
    logger.info("=== HMS Backup Script Started ===")
    logger.info(f"Database: {DB_NAME} @ {DB_HOST}:{DB_PORT}")
    logger.info(f"Backup directory: {BACKUP_DIR}")

    # Execute backup
    backup_filepath, backup_success = run_backup()

    if not backup_success:
        logger.error("Backup execution failed - aborting cleanup and archive")
        sys.exit(1)

    # Verify backup
    verify_success = verify_backup(backup_filepath)
    if not verify_success:
        logger.warning("Backup verification failed - proceeding with caution")

    # Archive to off-site (if enabled and today is archive day)
    archive_weekly_backup(backup_filepath)

    # Cleanup old backups
    cleanup_old_backups()

    logger.info("=== HMS Backup Script Completed Successfully ===\n")
    sys.exit(0)


if __name__ == '__main__':
    main()
```

### Setup: Cron Job Configuration

Add backup job to Cron (daily at 02:00 UTC):

```bash
# Edit crontab as root or backup operator
sudo crontab -e

# Add line (02:00 UTC every day):
0 2 * * * /usr/bin/python3 /opt/hms/scripts/backup_database.py

# To use environment variables, create a wrapper script:
# /opt/hms/scripts/backup_wrapper.sh
```

Example wrapper script (`/opt/hms/scripts/backup_wrapper.sh`):

```bash
#!/bin/bash

# Load environment configuration
export HMS_DB_NAME=hospital_management
export HMS_DB_HOST=localhost
export HMS_DB_PORT=5432
export HMS_DB_USER=backup_user
export HMS_BACKUP_DIR=/backups/local
export HMS_BACKUP_ARCHIVE_DIR=/backups/archive
export HMS_LOG_FILE=/var/log/hms_backup.log
export HMS_RETENTION_DAYS=5
export HMS_ENABLE_ARCHIVE=true

# Run backup script
/usr/bin/python3 /opt/hms/scripts/backup_database.py
```

Then in crontab:

```bash
0 2 * * * /bin/bash /opt/hms/scripts/backup_wrapper.sh >> /var/log/hms_backup_cron.log 2>&1
```

### Cron Schedule Examples

| Use Case                  | Cron Expression | Explanation                                     |
|:------------------------- |:--------------- |:----------------------------------------------- |
| Daily at 02:00 UTC        | `0 2 * * *`     | Overnight backup for minimal performance impact |
| Daily at 00:00 (midnight) | `0 0 * * *`     | Alternative timing                              |
| Every 6 hours             | `0 */6 * * *`   | Frequent backups for high-change environments   |
| Every Monday at 03:00     | `0 3 * * 1`     | Weekly full backup (combined with daily)        |

### Monitoring Backup Execution

Check backup logs:

```bash
# View recent backup log
tail -50 /var/log/hms_backup.log

# Check backup job status
sudo crontab -l

# Monitor backup directory for recent backups
ls -lt /backups/local/ | head -10

# View backup metadata
cat /backups/local/.metadata.json | python3 -m json.tool
```

### Off-Site Replication

The Python script supports automatic weekly archiving. To replicate to external storage:

**Option 1: Network-mounted backup directory**

```bash
# Mount remote NFS or SMB share
sudo mkdir -p /mnt/remote_backup
sudo mount -t nfs remote_server:/export/backups /mnt/remote_backup

# Update HMS_BACKUP_ARCHIVE_DIR to use remote path
export HMS_BACKUP_ARCHIVE_DIR=/mnt/remote_backup/archive
```

**Option 2: Cloud storage (AWS S3 example)**

Add S3 upload to the Python script:

```python
import boto3

def upload_to_s3(backup_filepath):
    """Upload backup to AWS S3."""
    s3_client = boto3.client('s3')
    bucket_name = os.getenv('HMS_S3_BUCKET', 'hospital-backups')

    try:
        s3_key = f"backups/{datetime.now().strftime('%Y/%m')}/{os.path.basename(backup_filepath)}"
        s3_client.upload_file(backup_filepath, bucket_name, s3_key)
        logger.info(f"Uploaded to S3: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        logger.error(f"S3 upload failed: {e}")
```

Then call `upload_to_s3(backup_filepath)` after successful backup.

## Backup Procedure

## Restore Procedure

### 1. Restore Decision Checklist

Before starting any restore operation, confirm:

- [ ] Type of restore required: full database, single table, or targeted recovery
- [ ] Target environment: new database, staging validation, or replacement of damaged production
- [ ] Application impact: which services should be stopped or notified
- [ ] Backup file selection: confirm the correct recovery point (date/time)
- [ ] Operator authorization: confirm proper change control approval
- [ ] Backup file verification: confirm backup integrity before attempting restore

### 2. Pre-Restore Safety Procedures

**Stop application services to prevent concurrent writes:**

```bash
# Stop Flask API service
sudo systemctl stop hms-api

# Or manually kill the process
pkill -f "python.*run.py"
```

**Create a backup of the current state (optional but recommended):**

```bash
pg_dump -h <db_host> -p <db_port> -U <db_user> -d <db_name> \
  -F c -f /backups/local/pre_restore_snapshot_$(date +\%Y\%m\%d_\%H\%M\%S).dump
```

### 3. Full Restore to an Existing Database

**Option A: Restore with object cleanup (destructive):**

```bash
pg_restore \
  -h <db_host> \
  -p <db_port> \
  -U <db_user> \
  -d <db_name> \
  --clean \
  --if-exists \
  --verbose \
  /backups/local/hospital_management_YYYYMMDD_HHMMSS.dump
```

Flags explained:

- `--clean`: Drop existing objects before recreating them
- `--if-exists`: Don't error if objects don't exist
- `--verbose`: Show detailed progress

**Option B: Restore to a fresh database (safest):**

```bash
# Create new empty database
createdb -h <db_host> -p <db_port> -U postgres -O <db_user> <db_name>_restore_test

# Restore to fresh database
pg_restore \
  -h <db_host> \
  -p <db_port> \
  -U <db_user> \
  -d <db_name>_restore_test \
  --verbose \
  /backups/local/hospital_management_YYYYMMDD_HHMMSS.dump

# Verify success, then swap databases if needed
psql -h <db_host> -p <db_port> -U postgres -c \
  "ALTER DATABASE <db_name> RENAME TO <db_name>_old; \
   ALTER DATABASE <db_name>_restore_test RENAME TO <db_name>;"
```

### 4. Targeted Restore (Single Table or Schema)

Restore specific tables by modifying pg_restore options:

```bash
# List what's available in backup
pg_restore -l /backups/local/hospital_management_YYYYMMDD_HHMMSS.dump | grep PATIENTS

# Restore single table (example: PATIENTS table)
pg_restore \
  -h <db_host> \
  -p <db_port> \
  -U <db_user> \
  -d <db_name> \
  --table=patients \
  --clean \
  --if-exists \
  /backups/local/hospital_management_YYYYMMDD_HHMMSS.dump

# Restore multiple tables
pg_restore \
  -h <db_host> \
  -p <db_port> \
  -U <db_user> \
  -d <db_name> \
  --table=patients \
  --table=visits \
  --table=surgeries \
  --clean \
  --if-exists \
  /backups/local/hospital_management_YYYYMMDD_HHMMSS.dump

# Restore entire schema
pg_restore \
  -h <db_host> \
  -p <db_port> \
  -U <db_user> \
  -d <db_name> \
  --schema=public \
  /backups/local/hospital_management_YYYYMMDD_HHMMSS.dump
```

**Critical Warning on Targeted Restore:**

- Selective restore can break referential integrity if parent or related tables are omitted
- Example: restoring VISITS without PATIENTS will fail foreign key constraints
- Only use targeted restore if you fully understand table dependencies
- Strongly prefer full restore into validation environment before partial recovery

### 5. Post-Restore Validation Steps

After any restore completes, perform validation:

```bash
# Connect to database
psql -h <db_host> -p <db_port> -U <db_user> -d <db_name>

-- Run validation queries
SELECT 'Checking tables...' as status;

-- Count key business tables
SELECT 'app_users' as table_name, COUNT(*) FROM app_users
UNION ALL SELECT 'staff', COUNT(*) FROM staff
UNION ALL SELECT 'patients', COUNT(*) FROM patients
UNION ALL SELECT 'visits', COUNT(*) FROM visits
UNION ALL SELECT 'surgeries', COUNT(*) FROM surgeries
UNION ALL SELECT 'admissions', COUNT(*) FROM admissions
UNION ALL SELECT 'medications', COUNT(*) FROM medications
UNION ALL SELECT 'pharmacy_dispensations', COUNT(*) FROM pharmacy_dispensations;

-- Check for constraint violations
SELECT COUNT(*) as orphaned_visits 
FROM visits v 
WHERE NOT EXISTS (SELECT 1 FROM patients WHERE patient_id = v.patient_id);

-- Verify audit data
SELECT COUNT(*) as audit_records FROM audit_logs LIMIT 1;

-- Check schema integrity
SELECT COUNT(*) as table_count FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
```

### 6. Resume Application Services

```bash
# Restart Flask API service
sudo systemctl start hms-api

# Verify API health
curl http://localhost:5000/api/health || curl http://localhost:5000/api/dummy/health

# Check application logs for errors
tail -50 /var/log/hms_api.log
```

## Restore Procedure

## Security and Data Protection Precautions

Backups of the Hospital Management System contain sensitive healthcare data including patient medical records, staff information, and clinical histories. These files must be treated as confidential assets.

### Data Protection Requirements

- **Access Control**: Restrict backup file access to authorized database and system administrators only (permission mode 600 or equivalent)
- **Storage Location**: Store backups in dedicated, restricted directories separate from application data
- **Encryption at Rest**: For sensitive environments, encrypt backup files using GPG or similar
- **Encryption in Transit**: Use TLS/HTTPS for any network transfer of backup files
- **Off-site Security**: If using remote/cloud storage, enable encryption and verify provider compliance with healthcare regulations (HIPAA/GDPR)
- **Retention Limits**: Do not retain backups indefinitely; follow policy of 5 recent daily + weekly archive, then secure deletion
- **Access Logging**: Log who accesses backup files and when (use `auditd` on Linux)

### Encryption Example (GPG)

```bash
# Encrypt a backup file
gpg --symmetric --cipher-algo AES256 /backups/local/hospital_management_20260506_020000.dump

# Decrypt for restore
gpg --decrypt /backups/local/hospital_management_20260506_020000.dump.gpg > hospital_management_20260506_020000.dump
```

### Healthcare Compliance Reminders

- All backup files are subject to GDPR, HIPAA, or equivalent healthcare data protection regulations
- Unauthorized disclosure of patient data can result in legal liability
- Deletion of backups must follow documented data retention policies
- Audit trails of backup access must be maintained for compliance verification

---

## Failure Handling and Troubleshooting

### Backup Failures

**Symptom:** Backup script exits with error or no backup file is created

**Diagnosis steps:**

```bash
# Check database connectivity
psql -h <db_host> -p <db_port> -U <db_user> -d <db_name> -c "SELECT 1"

# Check backup directory permissions and space
df -h /backups/local
ls -ld /backups/local
du -sh /backups/local

# Check PostgreSQL disk space
psql -U postgres -c "SELECT pg_database_size('hospital_management') / 1024 / 1024 as size_mb;"

# Check for long-running transactions blocking backup
psql -U postgres -c "SELECT pid, usename, query FROM pg_stat_activity WHERE state != 'idle';"
```

**Common fixes:**

- Insufficient disk space: Clean up old backups or add storage
- Permission denied: Ensure backup user has write access to backup directory
- Database locked: Wait for long-running transactions to complete, then retry
- Connection timeout: Verify network connectivity and PostgreSQL is listening on correct port

### Restore Failures

**Symptom:** pg_restore exits with errors or database is partially restored

**Diagnosis steps:**

```bash
# Check if target database exists
psql -h <db_host> -p <db_port> -U postgres -l | grep hospital_management

# Check for constraint violations
psql -U postgres -d <db_name> -c "SELECT * FROM information_schema.constraint_column_usage LIMIT 10;"

# Verify backup file integrity
pg_restore -l /backups/local/hospital_management_YYYYMMDD_HHMMSS.dump | head -50
```

**Common fixes:**

- Conflicting objects: Use `--clean --if-exists` flags in pg_restore command
- Referential integrity: Ensure all related tables are restored; restore to fresh database first
- Insufficient permissions: Verify restore user has appropriate database privileges

### Cron Job Failures

**Symptom:** Backup doesn't run at scheduled time or runs but fails silently

**Diagnosis:**

```bash
# Check Cron logs on Linux
sudo journalctl -u cron -n 50 --no-pager
# Or
grep CRON /var/log/syslog | tail -20

# Check if backup script has execute permissions
ls -la /opt/hms/scripts/backup_database.py
chmod +x /opt/hms/scripts/backup_database.py

# Test backup script manually
/usr/bin/python3 /opt/hms/scripts/backup_database.py

# Verify .pgpass file permissions (must be 600)
ls -la ~/.pgpass
chmod 600 ~/.pgpass
```

---

## Validation and Testing Cadence

Regular testing ensures backups are usable when recovery is needed. Establish a consistent testing schedule:

| Test Type                           | Frequency | Owner          | Pass Criteria                                     |
|:----------------------------------- |:--------- |:-------------- |:------------------------------------------------- |
| Backup execution verification       | Daily     | System Admin   | Backup file created with reasonable size          |
| Restore into validation environment | Weekly    | Database Admin | All tables present, row counts match, no errors   |
| Full database failover drill        | Quarterly | DevOps / DBA   | Complete restore + application boot in under RTO  |
| Targeted table recovery test        | Monthly   | Database Admin | Can restore single table without FK violations    |
| Off-site replication test           | Monthly   | Infrastructure | Weekly archive copies verified in remote location |

---

## Recovery Time and Recovery Point Objectives

These objectives guide backup frequency and testing cadence. For HMS in current (lab/academic) scope:

| Scenario                          | RTO           | RPO                          |
|:--------------------------------- |:-------------:|:----------------------------:|
| Complete database loss on primary | 2-4 hours     | 1 hour (daily backup window) |
| Accidental data deletion          | 1-2 hours     | 1 hour (daily backup window) |
| Corrupted specific table          | 30-60 minutes | 1 hour (targeted restore)    |
| Database disk exhaustion          | 30 minutes    | 15 minutes (backup snapshot) |

**For production-grade deployment:** Adjust these targets based on operational requirements and validate in regular drills.

---

## Documentation and Change Log

### Runbook Updates

Update this runbook whenever:

- Database schema changes significantly (new large tables)
- Backup policy changes (retention, frequency, or encryption)
- Infrastructure or deployment model changes
- Recovery procedures are tested and refined
- Security requirements or compliance needs change

### Change Log

| Date       | Version | Change Summary                                                          | Owner        |
|:---------- |:-------:|:----------------------------------------------------------------------- |:------------ |
| 2026-05-04 | 1.0     | Initial manual backup procedures                                        | Project Team |
| 2026-05-06 | 3.0     | Added Python + Cron automation, enhanced restore, complete independence | Project Team |

---

## Appendix: Quick Reference Commands

### Backup Commands

```bash
# Manual backup now
pg_dump -h localhost -U backup_user -d hospital_management -F c \
  -f /backups/local/hospital_management_$(date +\%Y\%m\%d_\%H\%M\%S).dump

# Run automated backup script
/usr/bin/python3 /opt/hms/scripts/backup_database.py

# List recent backups
ls -lt /backups/local/ | head -10

# Check backup size
du -sh /backups/local/hospital_management_*.dump | sort -h
```

### Restore Commands

```bash
# Full restore from backup
pg_restore -h localhost -U backup_user -d hospital_management \
  --clean --if-exists /backups/local/hospital_management_20260506_020000.dump

# Restore to new database for validation
createdb -U postgres hospital_management_test
pg_restore -h localhost -U backup_user -d hospital_management_test \
  /backups/local/hospital_management_20260506_020000.dump

# Restore single table
pg_restore -h localhost -U backup_user -d hospital_management \
  --table=patients /backups/local/hospital_management_20260506_020000.dump
```

### Verification Commands

```bash
# Check backup integrity
pg_restore -l /backups/local/hospital_management_20260506_020000.dump | wc -l

# Validate database after restore
psql -h localhost -U backup_user -d hospital_management \
  -c "SELECT COUNT(*) FROM patients; SELECT COUNT(*) FROM staff;"

# Monitor backup job
tail -f /var/log/hms_backup.log

# Check Cron scheduling
sudo crontab -l | grep backup
```

---

## Security and Data Protection Precautions
