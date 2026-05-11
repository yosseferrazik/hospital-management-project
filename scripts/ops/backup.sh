#!/bin/bash
# Simplified backup script for Hospital Management System
# - creates a compressed custom-format pg_dump
# - keeps last N local backups
# - optionally uploads to S3 using aws cli

set -euo pipefail

BACKUP_DIR=${BACKUP_DIR:-/backups/local}
DB_NAME=${DB_NAME:-hospital_management}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-backup_user}
RETENTION=${RETENTION:-5}
AWS_BUCKET=${AWS_BUCKET:-}

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

# upload to s3 if configured
if [ -n "$AWS_BUCKET" ]; then
  echo "Uploading $filepath to s3://$AWS_BUCKET/"
  aws s3 cp "$filepath" "s3://$AWS_BUCKET/" --sse AES256
fi

echo "Finished backup run"
