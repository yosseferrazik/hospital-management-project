#!/bin/bash
# HMS Full Backup Wrapper — run via cron.
# Backs up both PostgreSQL database AND configuration files.
#
# Usage in crontab:
#   0 2 * * * /bin/bash /opt/hms/scripts/backup_wrapper.sh >> /tmp/hms_backup_cron.log 2>&1
#
# For frequent incremental DB-only backups (every 15 min):
#   */15 * * * * /bin/bash /opt/hms/scripts/backup_wrapper.sh --frequent >> /tmp/hms_backup_frequent.log 2>&1

set -euo pipefail

export HMS_DB_NAME="${HMS_DB_NAME:-hsp_db}"
export HMS_DB_HOST="${HMS_DB_HOST:-localhost}"
export HMS_DB_PORT="${HMS_DB_PORT:-5432}"
export HMS_DB_USER="${HMS_DB_USER:-backup_user}"
export HMS_BACKUP_DIR="${HMS_BACKUP_DIR:-/backups/local}"
export HMS_LOG_FILE="${HMS_LOG_FILE:-/tmp/hms_backup.log}"
export HMS_RETENTION_DAYS="${HMS_RETENTION_DAYS:-5}"
export HMS_HMS_DIR="${HMS_HMS_DIR:-/opt/hms}"

# Optional: add extra config paths to backup (colon-separated)
# export HMS_CONFIG_PATHS="/custom/path/file.conf:/other/path/config.yml"

mkdir -p "$HMS_BACKUP_DIR" "$(dirname "$HMS_LOG_FILE")"

EXTRA_FLAGS=""
case "${1:-}" in
    --frequent) EXTRA_FLAGS="--frequent" ;;
    --physical) EXTRA_FLAGS="--physical" ;;
    --db-only)  EXTRA_FLAGS="--db-only" ;;
esac

exec /usr/bin/python3 /opt/hms/current/scripts/backup_database.py $EXTRA_FLAGS
