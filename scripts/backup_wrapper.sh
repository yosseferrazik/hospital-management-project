#!/bin/bash
# HMS Backup Wrapper — run via cron.
# Usage in crontab:
#   0 2 * * * /bin/bash /opt/hms/scripts/backup_wrapper.sh >> /var/log/hms_backup_cron.log 2>&1

set -euo pipefail

export HMS_DB_NAME="${HMS_DB_NAME:-hsp_db}"
export HMS_DB_HOST="${HMS_DB_HOST:-localhost}"
export HMS_DB_PORT="${HMS_DB_PORT:-5432}"
export HMS_DB_USER="${HMS_DB_USER:-backup_user}"
export HMS_BACKUP_DIR="${HMS_BACKUP_DIR:-/backups/local}"
export HMS_LOG_FILE="${HMS_LOG_FILE:-/var/log/hms_backup.log}"
export HMS_RETENTION_DAYS="${HMS_RETENTION_DAYS:-5}"

mkdir -p "$HMS_BACKUP_DIR" "$(dirname "$HMS_LOG_FILE")"

exec /usr/bin/python3 /opt/hms/scripts/backup_database.py
