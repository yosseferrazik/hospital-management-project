#!/bin/bash

# HMS Backup Wrapper Script for Cron
# 
# This script sets up the environment for the backup database script
# and is suitable for execution from Cron jobs.
#
# Usage: Add to Crontab
#   0 2 * * * /bin/bash /opt/hms/scripts/backup_wrapper.sh >> /var/log/hms_backup_cron.log 2>&1
#
# Configuration:
#   Modify the environment variables below to match your deployment

set -e

# Load configuration
export HMS_DB_NAME="${HMS_DB_NAME:-hospital_management}"
export HMS_DB_HOST="${HMS_DB_HOST:-localhost}"
export HMS_DB_PORT="${HMS_DB_PORT:-5432}"
export HMS_DB_USER="${HMS_DB_USER:-backup_user}"
export HMS_BACKUP_DIR="${HMS_BACKUP_DIR:-/backups/local}"
export HMS_BACKUP_ARCHIVE_DIR="${HMS_BACKUP_ARCHIVE_DIR:-/backups/archive}"
export HMS_LOG_FILE="${HMS_LOG_FILE:-/var/log/hms_backup.log}"
export HMS_RETENTION_DAYS="${HMS_RETENTION_DAYS:-5}"
export HMS_ARCHIVE_DAY="${HMS_ARCHIVE_DAY:-0}"  # 0=Sunday
export HMS_ENABLE_ARCHIVE="${HMS_ENABLE_ARCHIVE:-true}"

# Ensure backup directory exists
mkdir -p "${HMS_BACKUP_DIR}"
mkdir -p "${HMS_BACKUP_ARCHIVE_DIR}"

# Ensure log directory exists
mkdir -p "$(dirname "${HMS_LOG_FILE}")"

# Run backup script
/usr/bin/python3 /opt/hms/scripts/backup_database.py

exit $?
