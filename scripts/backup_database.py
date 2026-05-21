#!/usr/bin/env python3
"""
HMS Database Backup / Restore Script

Performs daily PostgreSQL logical backups with retention management,
logging, and optional rsync to the standby replica node.
Also supports listing backups and restoring from any point in time.

Supports Cron execution with environment variable configuration.

Usage:
    python3 backup_database.py                          # run backup
    python3 backup_database.py --list                   # list available backups
    python3 backup_database.py --restore latest         # restore from latest backup
    python3 backup_database.py --restore <file>         # restore from specific file
    python3 backup_database.py --list --before "2026-05-20 14:30"   # list backups before a date
    python3 backup_database.py --restore latest --before "2026-05-20 14:30"  # restore latest before a date

Environment Variables:
    HMS_DB_NAME         - Database name (default: hsp_db)
    HMS_DB_HOST         - PostgreSQL host (default: localhost)
    HMS_DB_PORT         - PostgreSQL port (default: 5432)
    HMS_DB_USER         - PostgreSQL backup user (default: backup_user)
    HMS_DB_PASSWORD     - PostgreSQL password (default: none — prompts or uses .pgpass)
    HMS_BACKUP_DIR      - Local backup directory (default: /backups/local)
    HMS_LOG_FILE        - Log file path (default: /tmp/hms_backup.log)
    HMS_RETENTION_DAYS  - Local backup retention days (default: 5)
    HMS_DB_PASSWORD     - PostgreSQL password (default: none — uses .pgpass or prompts)
    HMS_STANDBY_HOST    - Standby node hostname/IP for rsync (default: none)
    HMS_STANDBY_USER    - SSH user on standby (default: yerrazik)
    HMS_STANDBY_DIR     - Backup directory on standby (default: /backups/local)
"""

import argparse
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
DB_PASSWORD = os.getenv('HMS_DB_PASSWORD', '')
BACKUP_DIR = os.getenv('HMS_BACKUP_DIR', '/backups/local')
LOG_FILE = os.getenv('HMS_LOG_FILE', '/tmp/hms_backup.log')
RETENTION_DAYS = int(os.getenv('HMS_RETENTION_DAYS', '5'))
STANDBY_HOST = os.getenv('HMS_STANDBY_HOST', '')
STANDBY_USER = os.getenv('HMS_STANDBY_USER', 'yerrazik')
STANDBY_DIR = os.getenv('HMS_STANDBY_DIR', '/backups/local')

BACKUP_PATTERN = f"{DB_NAME}_*.dump"
TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'


def pg_env():
    env = os.environ.copy()
    if DB_PASSWORD:
        env['PGPASSWORD'] = DB_PASSWORD
    return env


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


def parse_timestamp(filename):
    stem = Path(filename).stem
    ts_str = stem.replace(f"{DB_NAME}_", "", 1)
    return datetime.strptime(ts_str, TIMESTAMP_FORMAT)


def get_backups():
    files = sorted(Path(BACKUP_DIR).glob(BACKUP_PATTERN), reverse=True)
    backups = []
    for f in files:
        try:
            ts = parse_timestamp(f.name)
            backups.append({
                'filename': f.name,
                'filepath': str(f),
                'timestamp': ts,
                'ts_display': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'size_mb': f.stat().st_size / (1024 * 1024),
            })
        except ValueError:
            continue
    return backups


def list_backups(before=None, json_output=False):
    backups = get_backups()
    if before:
        cutoff = datetime.strptime(before, '%Y-%m-%d %H:%M')
        backups = [b for b in backups if b['timestamp'] <= cutoff]

    if not backups:
        print("No backups found.")
        return

    if json_output:
        print(json.dumps([{
            'filename': b['filename'],
            'timestamp': b['ts_display'],
            'size_mb': round(b['size_mb'], 2),
            'filepath': b['filepath'],
        } for b in backups], indent=2))
        return

    print(f"{'Filename':<40} {'Timestamp':<20} {'Size (MB)':<10}")
    print("-" * 70)
    for b in backups:
        print(f"{b['filename']:<40} {b['ts_display']:<20} {b['size_mb']:<10.2f}")


def find_backup(before=None):
    backups = get_backups()
    if not backups:
        logger.error("No backups found in %s", BACKUP_DIR)
        return None

    if before:
        cutoff = datetime.strptime(before, '%Y-%m-%d %H:%M')
        candidates = [b for b in backups if b['timestamp'] <= cutoff]
        if not candidates:
            logger.error("No backup found before %s", before)
            return None
        return candidates[0]

    return backups[0]


def run_backup():
    """Execute PostgreSQL backup using pg_dump."""
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    backup_filename = f"{DB_NAME}_{timestamp}.dump"
    backup_filepath = os.path.join(BACKUP_DIR, backup_filename)

    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)

    cmd = [
        'pg_dump',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '-F', 'c',
        '-v',
        '-f', backup_filepath
    ]

    try:
        logger.info("Starting backup to %s...", backup_filepath)
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=pg_env())

        if not os.path.exists(backup_filepath):
            raise FileNotFoundError(f"Backup file not created: {backup_filepath}")

        file_size_mb = os.path.getsize(backup_filepath) / (1024 * 1024)
        logger.info("Backup completed successfully: %s (%.2f MB)", backup_filename, file_size_mb)

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
        logger.error("Backup failed: %s", e.stderr)
        return None, False
    except Exception as e:
        logger.error("Unexpected error during backup: %s", e)
        return None, False


def restore_database(backup_filepath, dry_run=False):
    """Restore PostgreSQL database from a backup file using pg_restore."""
    logger.info("Restoring database %s from %s ...", DB_NAME, backup_filepath)

    if not os.path.exists(backup_filepath):
        logger.error("Backup file not found: %s", backup_filepath)
        return False

    verify_ok = verify_backup(backup_filepath)
    if not verify_ok:
        logger.warning("Backup verification failed — restore may be incomplete")

    dropdb_cmd = ['dropdb', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER, '--if-exists', DB_NAME]
    createdb_cmd = ['createdb', '-h', DB_HOST, '-p', DB_PORT, '-U', DB_USER, DB_NAME]
    pgrestore_cmd = [
        'pg_restore',
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '--clean',
        '--if-exists',
        '-v',
        backup_filepath
    ]

    if dry_run:
        print("\n[DRY-RUN] Would execute:")
        print(f"  $ {' '.join(dropdb_cmd)}")
        print(f"  $ {' '.join(createdb_cmd)}")
        print(f"  $ {' '.join(pgrestore_cmd)}")
        return True

    try:
        logger.info("Dropping database %s ...", DB_NAME)
        subprocess.run(dropdb_cmd, check=True, capture_output=True, text=True, env=pg_env())

        logger.info("Creating database %s ...", DB_NAME)
        subprocess.run(createdb_cmd, check=True, capture_output=True, text=True, env=pg_env())

        logger.info("Running pg_restore ...")
        result = subprocess.run(pgrestore_cmd, check=True, capture_output=True, text=True, env=pg_env())

        logger.info("Restore completed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Restore failed: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected error during restore: %s", e)
        return False


def cleanup_old_backups():
    """Remove backups older than RETENTION_DAYS."""
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    deleted_count = 0

    try:
        logger.info("Cleaning up backups older than %d days...", RETENTION_DAYS)

        for backup_file in Path(BACKUP_DIR).glob(BACKUP_PATTERN):
            try:
                file_timestamp = parse_timestamp(backup_file.name)
                if file_timestamp < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    logger.info("Deleted old backup: %s", backup_file.name)
            except ValueError:
                logger.debug("Skipping non-standard filename: %s", backup_file.name)

        logger.info("Cleanup complete: %d old backups removed", deleted_count)
        return True

    except Exception as e:
        logger.error("Error during backup cleanup: %s", e)
        return False


def rsync_to_standby(backup_filepath):
    """Rsync backup file to the standby replica node."""
    if not STANDBY_HOST:
        logger.info("No standby host configured, skipping rsync")
        return True

    try:
        dest = f"{STANDBY_USER}@{STANDBY_HOST}:{STANDBY_DIR}/"
        logger.info("Rsyncing backup to standby %s:%s ...", STANDBY_HOST, STANDBY_DIR)

        cmd = ['rsync', '-avz', '--partial', backup_filepath, dest]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        last_line = [l for l in result.stdout.splitlines() if l.strip()][-1] if result.stdout.strip() else 'ok'
        logger.info("Rsync to standby completed: %s", last_line)
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Rsync to standby failed: %s", e.stderr)
        return False
    except Exception as e:
        logger.error("Unexpected rsync error: %s", e)
        return False


def verify_backup(backup_filepath):
    """Validate backup integrity by listing archive contents."""
    try:
        logger.info("Verifying backup integrity...")
        cmd = ['pg_restore', '-l', backup_filepath]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        object_count = len([line for line in result.stdout.split('\n') if line.strip()])
        logger.info("Backup verification successful: %d objects found", object_count)
        return True

    except Exception as e:
        logger.error("Backup verification failed: %s", e)
        return False


def log_backup_metadata(metadata):
    """Log backup metadata to JSON file for monitoring."""
    try:
        metadata_file = os.path.join(BACKUP_DIR, '.metadata.json')

        existing_data = []
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                existing_data = json.load(f)

        existing_data.append(metadata)

        if len(existing_data) > 30:
            existing_data = existing_data[-30:]

        with open(metadata_file, 'w') as f:
            json.dump(existing_data, f, indent=2)

    except Exception as e:
        logger.warning("Could not log backup metadata: %s", e)


def parse_args():
    parser = argparse.ArgumentParser(
        description='HMS Database Backup & Restore Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--restore', nargs='?', const='latest', metavar='FILE',
                        help='Restore database from a backup file. '
                             'Use "latest" or omit FILE to restore from the most recent backup.')
    parser.add_argument('--before', metavar='"YYYY-MM-DD HH:MM"',
                        help='Filter/list backups before this timestamp')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what restore would do without executing it')
    parser.add_argument('--json', action='store_true', help='Output list in JSON format')
    parser.add_argument('--frequent', action='store_true',
                        help='Quick frequent backup mode: skips verify + rsync, '
                             'uses hourly retention (default 24h). '
                             'Ideal for every-15-min cron jobs to achieve minute-level RPO.')
    return parser.parse_args()


def main():
    args = parse_args()

    # --- LIST mode ---
    if args.list:
        list_backups(before=args.before, json_output=args.json)
        return

    # --- RESTORE mode ---
    if args.restore:
        backup_filepath = None

        if args.restore == 'latest':
            backup = find_backup(before=args.before)
            if not backup:
                sys.exit(1)
            backup_filepath = backup['filepath']
            logger.info("Selected backup: %s (from %s)", backup['filename'], backup['ts_display'])
        else:
            backup_filepath = args.restore
            if not os.path.exists(backup_filepath):
                logger.error("Backup file not found: %s", backup_filepath)
                sys.exit(1)
            logger.info("Selected backup: %s", backup_filepath)

        if args.dry_run:
            restore_database(backup_filepath, dry_run=True)
            return

        print(f"\nWARNING: This will DROP and recreate the database '{DB_NAME}'.")
        print(f"All current data in '{DB_NAME}' will be permanently lost.")
        print(f"Source backup: {backup_filepath}")
        confirm = input("Are you sure? Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("Restore cancelled.")
            sys.exit(0)

        success = restore_database(backup_filepath)
        sys.exit(0 if success else 1)

    # --- BACKUP mode ---
    logger.info("=== HMS Backup Script Started ===")
    logger.info("Database: %s @ %s:%s", DB_NAME, DB_HOST, DB_PORT)
    logger.info("Backup directory: %s", BACKUP_DIR)

    if args.frequent:
        logger.info("Frequent mode: skipping verify + rsync")
        freq_hours = int(os.getenv('FREQUENT_RETENTION_HOURS', '24'))

    backup_filepath, backup_success = run_backup()

    if not backup_success:
        logger.error("Backup execution failed - aborting cleanup and archive")
        sys.exit(1)

    if not args.frequent:
        verify_success = verify_backup(backup_filepath)
        if not verify_success:
            logger.warning("Backup verification failed - proceeding with caution")

        rsync_to_standby(backup_filepath)
        cleanup_old_backups()
    else:
        cutoff = datetime.now() - timedelta(hours=freq_hours)
        deleted = 0
        for f in Path(BACKUP_DIR).glob(BACKUP_PATTERN):
            try:
                if parse_timestamp(f.name) < cutoff:
                    f.unlink()
                    deleted += 1
            except ValueError:
                continue
        logger.info("Frequent cleanup: removed %d backup(s) older than %d hours", deleted, freq_hours)

    logger.info("=== HMS Backup Script Completed Successfully ===")
    sys.exit(0)


if __name__ == '__main__':
    main()
