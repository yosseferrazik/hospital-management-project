#!/bin/bash
# Simplified backup script for Hospital Management System
# - creates a compressed custom-format pg_dump
# - keeps last N local backups

set -euo pipefail

BACKUP_DIR=${BACKUP_DIR:-/backups/local}
DB_NAME=${DB_NAME:-hsp_db}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-backup_user}
RETENTION=${RETENTION:-5}

mkdir -p "$BACKUP_DIR"
timestamp=$(date +%Y%m%d_%H%M%S)
filename="${DB_NAME}_${timestamp}.dump"
filepath="$BACKUP_DIR/$filename"

echo "Starting backup: $filepath"

PGPASSWORD=${PGPASSWORD:-} pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -F c -v -f "$filepath" "$DB_NAME"

if [ ! -f "$filepath" ]; then
  echo "Backup file not created: $filepath" >&2
  exit 1
fi

echo "Backup completed: $filepath ($(du -h "$filepath" | cut -f1))"

# rotate
cd "$BACKUP_DIR"
ls -1t ${DB_NAME}_*.dump | tail -n +$((RETENTION+1)) | xargs -r rm -f --

echo "Finished backup run"
