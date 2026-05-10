# HMS Scripts Directory

This directory contains operational and automation scripts for the Hospital Management System.

## Backup Automation Scripts

### `backup_database.py`

**Purpose:** Automated PostgreSQL database backup with retention management and archiving.

**Features:**
- Daily logical backups using `pg_dump` (custom format)
- Automatic cleanup of old backups (configurable retention)
- Weekly archiving to off-site or archive location
- Backup verification and integrity checking
- Comprehensive logging to file and stdout
- Metadata tracking of all backups

**Environment Configuration:**

```bash
export HMS_DB_NAME=hospital_management              # Database name
export HMS_DB_HOST=localhost                         # PostgreSQL host
export HMS_DB_PORT=5432                              # PostgreSQL port
export HMS_DB_USER=backup_user                       # Backup user
export HMS_BACKUP_DIR=/backups/local                 # Local backup directory
export HMS_BACKUP_ARCHIVE_DIR=/backups/archive       # Archive directory
export HMS_LOG_FILE=/var/log/hms_backup.log          # Log file
export HMS_RETENTION_DAYS=5                          # Days to retain local backups
export HMS_ARCHIVE_DAY=0                             # Day to archive (0=Sunday)
export HMS_ENABLE_ARCHIVE=true                       # Enable archiving
```

**Usage (Manual):**

```bash
python3 backup_database.py
```

**Usage (Cron - Daily at 2:00 AM UTC):**

```bash
0 2 * * * /bin/bash /opt/hms/scripts/backup_wrapper.sh >> /var/log/hms_backup_cron.log 2>&1
```

**Example Output:**

```
2026-05-06 02:00:15 - INFO - === HMS Backup Script Started ===
2026-05-06 02:00:15 - INFO - Database: hospital_management @ localhost:5432
2026-05-06 02:00:15 - INFO - Backup directory: /backups/local
2026-05-06 02:00:15 - INFO - Starting backup to /backups/local/hospital_management_20260506_020000.dump...
2026-05-06 02:05:30 - INFO - Backup completed successfully: hospital_management_20260506_020000.dump (45.23 MB)
2026-05-06 02:05:35 - INFO - Backup verification successful: 142 objects found
2026-05-06 02:05:36 - INFO - Cleaning up backups older than 5 days...
2026-05-06 02:05:36 - INFO - Cleanup complete: 2 old backups removed
2026-05-06 02:05:37 - INFO - === HMS Backup Script Completed Successfully ===
```

### `backup_wrapper.sh`

**Purpose:** Shell wrapper script that sets environment variables and calls the Python backup script.

**Usage:** Designed for Cron execution with environment variable configuration.

**Configuration:**

Edit the variables at the top of the script to match your deployment:

```bash
export HMS_DB_NAME="hospital_management"
export HMS_DB_HOST="localhost"
# ... other environment variables
```

## Setup Instructions

### 1. Install Required Tools

Ensure the following are installed on the backup node:

```bash
# PostgreSQL client tools
sudo apt-get install postgresql-client

# Python 3.10+
python3 --version
```

### 2. Create Backup Directories

```bash
sudo mkdir -p /backups/local /backups/archive
sudo chown postgres:postgres /backups/local /backups/archive
sudo chmod 700 /backups/local /backups/archive
```

### 3. Create PostgreSQL Backup User

```bash
sudo -u postgres psql -c "CREATE USER backup_user WITH PASSWORD 'secure_password'"
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE hospital_management TO backup_user"
```

Or use `.pgpass` for passwordless authentication:

```bash
echo "localhost:5432:hospital_management:backup_user:secure_password" >> ~/.pgpass
chmod 600 ~/.pgpass
```

### 4. Deploy Backup Scripts

```bash
sudo mkdir -p /opt/hms/scripts
sudo cp backup_database.py /opt/hms/scripts/
sudo cp backup_wrapper.sh /opt/hms/scripts/
sudo chmod +x /opt/hms/scripts/backup_database.py
sudo chmod +x /opt/hms/scripts/backup_wrapper.sh
```

### 5. Configure Cron Job

```bash
sudo crontab -e

# Add the following line for daily backup at 2:00 AM:
0 2 * * * /bin/bash /opt/hms/scripts/backup_wrapper.sh >> /var/log/hms_backup_cron.log 2>&1
```

### 6. Verify Setup

Test manual backup execution:

```bash
python3 /opt/hms/scripts/backup_database.py
```

Check backup was created:

```bash
ls -lh /backups/local/ | head -5
```

## Monitoring and Troubleshooting

### Check Backup Logs

```bash
# Recent backup logs
tail -50 /var/log/hms_backup.log

# Cron execution logs
sudo journalctl -u cron -n 50
```

### Verify Recent Backups

```bash
ls -lt /backups/local/hospital_management_*.dump | head -10
du -sh /backups/local/hospital_management_*.dump | sort -h
```

### Check Backup Metadata

```bash
cat /backups/local/.metadata.json | python3 -m json.tool
```

### Test Restore from Backup

```bash
# Create validation database
createdb -U postgres hospital_management_test

# Restore from backup
pg_restore -U backup_user -d hospital_management_test /backups/local/hospital_management_YYYYMMDD_HHMMSS.dump

# Verify restore
psql -U postgres -d hospital_management_test -c "SELECT COUNT(*) FROM patients;"
```

## Backup Schedule Reference

| Use Case | Cron Expression | Explanation |
|:---|:---|:---|
| Daily at 2:00 AM UTC | `0 2 * * *` | Standard overnight backup |
| Daily at midnight | `0 0 * * *` | Alternative timing |
| Every 6 hours | `0 */6 * * *` | Frequent backups |
| Every Monday at 3 AM | `0 3 * * 1` | Weekly backup |
| Every 1st of month at 4 AM | `0 4 1 * *` | Monthly archive |

## Security Considerations

- **Backup Permissions:** Ensure backup files are readable only by authorized administrators
- **Credentials:** Use `.pgpass` file with 600 permissions instead of hardcoding passwords
- **Encryption:** Encrypt backups at rest using GPG or similar
- **Retention:** Follow the 5-day local + 1 weekly off-site policy
- **Access Logging:** Monitor who accesses backup files

## Off-Site Replication

The backup script supports weekly archiving to external locations:

### Option 1: Network-Mounted NFS

```bash
# Mount remote storage
sudo mount -t nfs remote_server:/export/backups /mnt/remote_backup

# Update wrapper script
export HMS_BACKUP_ARCHIVE_DIR=/mnt/remote_backup/archive
```

### Option 2: AWS S3

Add to the Python script (after archive_weekly_backup):

```python
import boto3

def upload_to_s3(backup_filepath):
    s3_client = boto3.client('s3')
    bucket_name = 'hospital-backups'
    key = f"backups/{datetime.now().strftime('%Y/%m')}/{os.path.basename(backup_filepath)}"
    s3_client.upload_file(backup_filepath, bucket_name, key)
```

## Future Enhancements

- [ ] Implement encryption for backup files (GPG)
- [ ] Add support for incremental backups
- [ ] Implement automated S3 or cloud storage uploads
- [ ] Add backup verification jobs
- [ ] Create restore testing automation
- [ ] Implement metrics and monitoring integration

## Support and Documentation

For complete procedures, see:
- [Backup and Restore Runbook](../docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md)
- [High Availability and Backup Strategy](../docs/03_Security_and_Infrastructure/High_Availability_and_Backup_Strategy.md)
- [Deployment Architecture](../docs/03_Security_and_Infrastructure/Deployment_Architecture.md)
