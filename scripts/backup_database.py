#!/usr/bin/env python3
"""
HMS Database Backup Automation Script

Performs daily PostgreSQL logical backups with retention management,
logging, and optional off-site replication.

Supports Cron execution with environment variable configuration.

Usage:
    python3 backup_database.py

Environment Variables:
    HMS_DB_NAME         - Database name (default: hsp_db)
    HMS_DB_HOST         - PostgreSQL host (default: localhost)
    HMS_DB_PORT         - PostgreSQL port (default: 5432)
    HMS_DB_USER         - PostgreSQL backup user (default: backup_user)
    HMS_BACKUP_DIR      - Local backup directory (default: /backups/local)
    HMS_BACKUP_ARCHIVE_DIR - Weekly archive directory (default: /backups/archive)
    HMS_LOG_FILE        - Log file path (default: /var/log/hms_backup.log)
    HMS_RETENTION_DAYS  - Local backup retention days (default: 5)
    HMS_ARCHIVE_DAY     - Day of week for archiving, 0=Sunday (default: 0)
    HMS_ENABLE_ARCHIVE  - Enable off-site archiving (default: true)
"""

import os
import sys
import subprocess
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configuration from environment or defaults
DB_NAME = os.getenv('HMS_DB_NAME', 'hsp_db')
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
