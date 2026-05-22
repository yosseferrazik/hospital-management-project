#!/usr/bin/env python3
"""
HMS Full Backup / Restore Script

Performs PostgreSQL logical backups, PHYSICAL backups (PGDATA),
and configuration backups with retention management, logging,
and optional rsync to standby.
Supports full bare-metal service recovery — restore PGDATA, config,
and database.

Supports Cron execution with environment variable configuration.

Usage:
    python3 backup_database.py                                   # full backup (logical + config)
    python3 backup_database.py --physical                        # add physical PGDATA backup
    python3 backup_database.py --physical-only                   # PGDATA backup only
    python3 backup_database.py --db-only                         # logical dump only
    python3 backup_database.py --config-only                     # app config only
    python3 backup_database.py --list                            # list all backups
    python3 backup_database.py --restore latest                  # restore DB (logical)
    python3 backup_database.py --config-restore latest           # restore app config
    python3 backup_database.py --physical-restore latest         # restore PGDATA (physical)
    python3 backup_database.py --full-restore latest             # PGDATA + config + DB
    python3 backup_database.py --pgdata-dir /path/to/data        # override PGDATA path

Environment Variables:
    HMS_DB_NAME              - Database name (default: hsp_db)
    HMS_DB_HOST              - PostgreSQL host (default: localhost)
    HMS_DB_PORT              - PostgreSQL port (default: 5432)
    HMS_DB_USER              - PostgreSQL backup user (default: backup_user)
    HMS_DB_PASSWORD          - PostgreSQL password (default: none)
    HMS_BACKUP_DIR           - Local backup directory (default: /backups/local)
    HMS_LOG_FILE             - Log file path (default: /tmp/hms_backup.log)
    HMS_RETENTION_DAYS       - Local backup retention days (default: 5)
    HMS_STANDBY_HOST         - Standby node hostname/IP for rsync (default: none)
    HMS_STANDBY_USER         - SSH user on standby (default: ubuntu)
    HMS_STANDBY_DIR          - Backup directory on standby (default: /backups/local)
    HMS_CONFIG_PATHS         - Extra config file/dir paths, colon-separated (optional)
    HMS_CONFIG_RESTORE_DIR   - Temporary restore root for config files (default: /)
    HMS_HMS_DIR              - HMS installation root (default: /opt/hms)
    HMS_PGDATA_DIR           - PostgreSQL data directory (default: auto-detect)
    HMS_PG_VERSION           - PostgreSQL major version (default: auto-detect)
    HMS_PG_SERVICE           - PostgreSQL systemd service (default: postgresql@<version>-main)
"""

import argparse
import os
import sys
import subprocess
import logging
import json
import tarfile
import shutil
import fnmatch
import time
from datetime import datetime, timedelta
from pathlib import Path

DB_NAME = os.getenv('HMS_DB_NAME', 'hsp_db')
DB_HOST = os.getenv('HMS_DB_HOST', 'localhost')
DB_PORT = os.getenv('HMS_DB_PORT', '5432')
DB_USER = os.getenv('HMS_DB_USER', 'backup_user')
DB_PASSWORD = os.getenv('HMS_DB_PASSWORD', 'change_password')
BACKUP_DIR = os.getenv('HMS_BACKUP_DIR', '/backups/local')
LOG_FILE = os.getenv('HMS_LOG_FILE', '/tmp/hms_backup.log')
RETENTION_DAYS = int(os.getenv('HMS_RETENTION_DAYS', '5'))
STANDBY_HOST = os.getenv('HMS_STANDBY_HOST', '100.98.214.53')
STANDBY_USER = os.getenv('HMS_STANDBY_USER', 'ubuntu')
STANDBY_DIR = os.getenv('HMS_STANDBY_DIR', '/backups/local')
HMS_DIR = os.getenv('HMS_HMS_DIR', '/opt/hms')
CONFIG_RESTORE_DIR = os.getenv('HMS_CONFIG_RESTORE_DIR', '/')

BACKUP_PATTERN = f"{DB_NAME}_*.dump"
TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'

CONFIG_PATHS_DEFAULT = [
    f"{HMS_DIR}/current/server/src/.env",
    f"{HMS_DIR}/current/desktop/src/.env",
    f"{HMS_DIR}/current/deploy/ansible/inventory.ini",
    f"{HMS_DIR}/.deploy_meta",
    "/etc/systemd/system/hms-api.service",
    "/etc/logrotate.d/hms",
    "/etc/hms.env",
]
EXTRA_CONFIG_PATHS = os.getenv('HMS_CONFIG_PATHS', '')
if EXTRA_CONFIG_PATHS:
    CONFIG_PATHS_DEFAULT.extend(EXTRA_CONFIG_PATHS.split(':'))

# PostgreSQL physical backup (PGDATA) configuration
PGDATA_DIR = os.getenv('HMS_PGDATA_DIR', '')
PG_VERSION = os.getenv('HMS_PG_VERSION', '')
PG_SERVICE = os.getenv('HMS_PG_SERVICE', '')

PHYSICAL_BACKUP_PATTERN = "physical_*.tar.gz"

# Tables that can be safely excluded from frequent backups because they are
# pre-populated by initial SQL scripts and rarely change.
# WARNING: Do NOT add app_users, staff, or any personnel table here.
FREQUENT_EXCLUDE_TABLES = [
    "floors", "rooms", "operating_theaters",
    "medical_devices", "medical_specialties", "medications",
]


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


def run_backup(exclude_static_data=False):
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

    if exclude_static_data:
        for table in FREQUENT_EXCLUDE_TABLES:
            cmd.extend(['--exclude-table-data', table])
        logger.info("Frequent mode: excluding data from %d reference tables (users, staff, and transactions are always included)", len(FREQUENT_EXCLUDE_TABLES))

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


def detect_pg_connection():
    """Detect working PostgreSQL connection method for restore operations.

    Tries configured TCP first, then falls back to Unix socket variants.
    Returns a dict with command prefix, host, port, user, and env,
    or None if all methods fail. Prints debug info for each attempt.
    """
    candidates = []

    # 1. TCP as configured
    candidates.append({
        'label': f'TCP {DB_HOST}:{DB_PORT} user={DB_USER}',
        'prefix': [],
        'host': DB_HOST,
        'port': DB_PORT,
        'user': DB_USER,
        'env': pg_env(),
    })

    # 2. TCP using postgres user from DATABASE_URL host
    cand_host = os.getenv('DATABASE_URL', '').split('@')
    if len(cand_host) > 1:
        db_url_host = cand_host[-1].split(':')[0]
        if db_url_host and db_url_host != DB_HOST:
            candidates.append({
                'label': f'TCP {db_url_host}:{DB_PORT} user={DB_USER}',
                'prefix': [],
                'host': db_url_host,
                'port': DB_PORT,
                'user': DB_USER,
                'env': pg_env(),
            })

    # 3. Unix socket via sudo -nu postgres
    candidates.append({
        'label': 'Unix socket (sudo -nu postgres)',
        'prefix': ['sudo', '-nu', 'postgres'],
        'host': '',
        'port': '',
        'user': '',
        'env': os.environ.copy(),
    })

    # 4. Unix socket via sudo -u postgres
    candidates.append({
        'label': 'Unix socket (sudo -u postgres)',
        'prefix': ['sudo', '-u', 'postgres'],
        'host': '',
        'port': '',
        'user': '',
        'env': os.environ.copy(),
    })

    # 5. Unix socket via su - postgres -c
    candidates.append({
        'label': 'Unix socket (su - postgres -c)',
        'prefix': ['su', '-', 'postgres', '-c'],
        'host': '',
        'port': '',
        'user': '',
        'env': os.environ.copy(),
    })

    for cand in candidates:
        prefix = cand['prefix']
        h_flag = ['-h', cand['host']] if cand['host'] else []
        p_flag = ['-p', cand['port']] if cand['port'] else []
        u_flag = ['-U', cand['user']] if cand['user'] else []

        if prefix and prefix[0] == 'su':
            # su -c expects a single string argument
            inner = 'psql -d template1 -c "SELECT 1"'
            cmd = prefix + [inner]
        else:
            cmd = prefix + ['psql'] + h_flag + p_flag + u_flag + [
                '-d', 'template1', '-c', 'SELECT 1', '--no-password'
            ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    env=cand['env'], timeout=8)
            if result.returncode == 0:
                logger.info("PostgreSQL connection: %s", cand['label'])
                return {
                    'prefix': prefix,
                    'host': cand['host'],
                    'port': cand['port'],
                    'user': cand['user'],
                    'env': cand['env'],
                }
            else:
                stderr_short = result.stderr.strip()[:120] if result.stderr else 'no stderr'
                logger.debug("Connection %s failed (rc=%d): %s",
                             cand['label'], result.returncode, stderr_short)
        except FileNotFoundError as e:
            logger.debug("Connection %s failed: %s", cand['label'], e)
        except Exception as e:
            logger.debug("Connection %s failed: %s", cand['label'], e)

    # Final detailed error
    logger.error("Cannot connect to PostgreSQL. Attempted:")
    for cand in candidates:
        logger.error("  - %s", cand['label'])
    logger.error("Check that PostgreSQL is running and accessible.")
    return None


def restore_database(backup_filepath, dry_run=False):
    """Restore PostgreSQL database from a backup file using pg_restore."""
    logger.info("Restoring database %s from %s ...", DB_NAME, backup_filepath)

    if not os.path.exists(backup_filepath):
        logger.error("Backup file not found: %s", backup_filepath)
        return False

    verify_ok = verify_backup(backup_filepath)
    if not verify_ok:
        logger.warning("Backup verification failed — restore may be incomplete")

    conn = detect_pg_connection()
    if not conn:
        logger.error("No working PostgreSQL connection found — aborting restore")
        return False

    prefix = conn['prefix']
    use_su = bool(prefix and prefix[0] == 'su')
    h_flag = ['-h', conn['host']] if conn['host'] else []
    p_flag = ['-p', conn['port']] if conn['port'] else []
    u_flag = ['-U', conn['user']] if conn['user'] else []

    def build_cmd(tool, extra_args):
        """Build command list, handling su -c syntax."""
        parts = prefix[:]
        if use_su:
            inner = ' '.join([tool] + extra_args)
            parts.append(inner)
        else:
            parts.append(tool)
            parts.extend(extra_args)
        return parts

    def term_args():
        return h_flag + p_flag + u_flag + [
            '-d', 'template1',
            '-c', f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{DB_NAME}' AND pid <> pg_backend_pid()"
        ]

    def drop_args():
        return h_flag + p_flag + u_flag + ['--if-exists', DB_NAME]

    def create_args():
        return h_flag + p_flag + u_flag + [DB_NAME]

    def restore_args():
        return h_flag + p_flag + u_flag + [
            '-d', DB_NAME, '--clean', '--if-exists', '-v', backup_filepath
        ]

    dropdb_cmd = build_cmd('dropdb', drop_args())
    createdb_cmd = build_cmd('createdb', create_args())
    pgrestore_cmd = build_cmd('pg_restore', restore_args())

    if dry_run:
        print("\n[DRY-RUN] Connection: %s" % (
            'su - postgres -c' if use_su else ' '.join(prefix) if prefix else
            f"TCP {conn['host']}:{conn['port']} user={conn['user']}"))
        print("  $ %s" % ' '.join(dropdb_cmd))
        print("  $ %s" % ' '.join(createdb_cmd))
        print("  $ %s" % ' '.join(pgrestore_cmd))
        return True

    try:
        logger.info("Terminating active connections to %s ...", DB_NAME)
        term_cmd = build_cmd('psql', term_args())
        subprocess.run(term_cmd, check=False, capture_output=True, text=True, env=conn['env'])

        logger.info("Dropping database %s ...", DB_NAME)
        subprocess.run(dropdb_cmd, check=True, capture_output=True, text=True, env=conn['env'])

        logger.info("Creating database %s ...", DB_NAME)
        subprocess.run(createdb_cmd, check=True, capture_output=True, text=True, env=conn['env'])

        logger.info("Running pg_restore ...")
        subprocess.run(pgrestore_cmd, check=True, capture_output=True, text=True, env=conn['env'])

        logger.info("Restore completed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Restore failed: %s", e.stderr or e.stdout)
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


# ---------------------------------------------------------------------------
# PostgreSQL physical (PGDATA) helpers
# ---------------------------------------------------------------------------

def detect_pg_version():
    """Detect PostgreSQL major version from pg_config or known paths."""
    if PG_VERSION:
        return PG_VERSION
    try:
        result = subprocess.run(['pg_config', '--version'], capture_output=True,
                                text=True, check=False)
        if result.returncode == 0:
            ver = result.stdout.strip().split()[-1]
            return '.'.join(ver.split('.')[:2])
    except FileNotFoundError:
        pass
    # Fallback: scan /etc/postgresql/ for version dirs
    pg_etc = Path('/etc/postgresql')
    if pg_etc.is_dir():
        versions = sorted(pg_etc.iterdir())
        if versions:
            return versions[-1].name
    # Last resort: try to find pg_lsclusters output
    try:
        result = subprocess.run(['pg_lsclusters', '-h'], capture_output=True,
                                text=True, check=False)
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split()
            if parts:
                return parts[0]
    except FileNotFoundError:
        pass
    logger.warning("Could not detect PostgreSQL version, defaulting to 16")
    return '16'


def detect_pgdata(version=None):
    """Detect PGDATA directory. Checks env var, pg_config, common paths."""
    if PGDATA_DIR:
        return PGDATA_DIR
    ver = version or detect_pg_version()
    # Common locations
    candidates = [
        f"/var/lib/postgresql/{ver}/main",
        f"/var/lib/pgsql/{ver}/data",
        f"/var/lib/pgsql/data",
    ]
    # Try pg_config if available
    try:
        result = subprocess.run(['pg_config', '--data-directory'], capture_output=True,
                                text=True, check=False)
        if result.returncode == 0:
            path = result.stdout.strip()
            if path:
                candidates.insert(0, path)
    except FileNotFoundError:
        pass
    for path in candidates:
        if Path(path).is_dir():
            pgdata = Path(path)
            if (pgdata / 'PG_VERSION').is_file() or (pgdata / 'global').is_dir():
                logger.info("Detected PGDATA: %s", path)
                return path
    logger.warning("PGDATA not found at any known path, defaulting to %s", candidates[0])
    return candidates[0]


def detect_pg_service(version=None):
    """Detect PostgreSQL systemd service name."""
    if PG_SERVICE:
        return PG_SERVICE
    ver = version or detect_pg_version()
    candidates = [
        f"postgresql@{ver}-main",
        f"postgresql-{ver}",
        "postgresql",
    ]
    for svc in candidates:
        try:
            result = subprocess.run(['systemctl', 'is-active', svc], capture_output=True,
                                    text=True, check=False)
            if result.returncode == 0 or result.stdout.strip() in ('active', 'inactive'):
                return svc
        except FileNotFoundError:
            pass
    return f"postgresql@{ver}-main"


def detect_pg_config_dir(version=None):
    """Detect PostgreSQL config directory (postgresql.conf location)."""
    ver = version or detect_pg_version()
    candidates = [
        f"/etc/postgresql/{ver}/main",
    ]
    pgdata = detect_pgdata(ver)
    if pgdata:
        candidates.append(pgdata)
    for path in candidates:
        if Path(path, 'postgresql.conf').is_file():
            return path
    return candidates[0]


def get_pg_version_from_backup(archive_path):
    """Try to extract PG version from a physical backup archive."""
    try:
        with tarfile.open(archive_path, 'r:gz') as tar:
            try:
                member = tar.getmember('PG_VERSION')
            except KeyError:
                for m in tar.getmembers():
                    if m.name.endswith('PG_VERSION'):
                        member = m
                        break
                else:
                    return None
            f = tar.extractfile(member)
            if f:
                return f.read().decode('utf-8').strip()
    except Exception:
        pass
    return None


def detect_postgres_user():
    """Detect the OS user that owns PostgreSQL."""
    try:
        import pwd
        # Try common users
        for user in ['postgres', 'postgresql']:
            try:
                pwd.getpwnam(user)
                return user
            except KeyError:
                continue
    except ImportError:
        pass
    return 'postgres'


# ---------------------------------------------------------------------------
# Physical backup / restore
# ---------------------------------------------------------------------------

def backup_physical():
    """Create a physical backup of PGDATA using pg_basebackup or cold tar."""
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    archive_name = f"physical_{timestamp}.tar.gz"
    archive_path = os.path.join(BACKUP_DIR, archive_name)

    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)

    version = detect_pg_version()
    pgdata = detect_pgdata(version)
    pg_service = detect_pg_service(version)

    logger.info("Physical backup — PGDATA: %s, PG version: %s", pgdata, version)

    if not Path(pgdata).is_dir():
        logger.error("PGDATA directory not found: %s", pgdata)
        return None, False

    temp_dir = os.path.join(BACKUP_DIR, f".pg_basebackup_{timestamp}")
    try:
        # Strategy 1: hot backup via pg_basebackup (preferred)
        if shutil.which('pg_basebackup'):
            logger.info("Using pg_basebackup for hot physical backup...")
            Path(temp_dir).mkdir(parents=True, exist_ok=True)
            cmd = [
                'pg_basebackup',
                '-h', DB_HOST,
                '-p', DB_PORT,
                '-U', DB_USER,
                '-D', temp_dir,
                '-Ft',           # tar format output
                '-z',            # gzip compression
                '-P',            # show progress
                '-X', 'fetch',   # include WAL
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True, env=pg_env())
            # pg_basebackup creates one tar per tablespace; bundle them
            base_files = sorted(Path(temp_dir).glob('*.tar.gz'))
            if base_files:
                # Rename the main base.tar.gz to our archive name
                base_tar = base_files[0]
                shutil.move(str(base_tar), archive_path)
                # If there are additional tablespace tars, include them
                if len(base_files) > 1:
                    # We need to repack: extract base and add extra tars
                    pass  # for now, single tablespace case
            else:
                raise FileNotFoundError("pg_basebackup produced no output files")
        else:
            # Strategy 2: cold backup via tar (requires PG to be stopped)
            logger.warning("pg_basebackup not available, using cold tar backup")
            logger.warning("Stopping PostgreSQL service: %s", pg_service)
            subprocess.run(['systemctl', 'stop', pg_service], check=True,
                           capture_output=True, text=True)
            try:
                with tarfile.open(archive_path, 'w:gz') as tar:
                    tar.add(pgdata, arcname=os.path.basename(pgdata))
            finally:
                subprocess.run(['systemctl', 'start', pg_service], check=False)

        archive_size_mb = os.path.getsize(archive_path) / (1024 * 1024)
        logger.info("Physical backup completed: %s (%.2f MB)", archive_name, archive_size_mb)

        metadata = {
            'timestamp': timestamp,
            'filename': archive_name,
            'filepath': archive_path,
            'size_bytes': os.path.getsize(archive_path),
            'size_mb': round(archive_size_mb, 2),
            'pg_version': version,
            'pgdata': pgdata,
            'type': 'physical',
            'status': 'success',
        }
        log_backup_metadata(metadata)
        return archive_path, True

    except subprocess.CalledProcessError as e:
        logger.error("Physical backup failed: %s", e.stderr or e.stdout)
        return None, False
    except Exception as e:
        logger.error("Unexpected error during physical backup: %s", e)
        return None, False
    finally:
        if Path(temp_dir).is_dir():
            shutil.rmtree(temp_dir, ignore_errors=True)


def restore_physical(archive_filepath, dry_run=False, target_dir=None):
    """Restore PGDATA from a physical backup archive."""
    logger.info("Restoring physical PGDATA from %s ...", archive_filepath)

    if not os.path.exists(archive_filepath):
        logger.error("Physical backup not found: %s", archive_filepath)
        return False

    version = get_pg_version_from_backup(archive_filepath) or detect_pg_version()
    pgdata = target_dir or detect_pgdata(version)
    pg_service = detect_pg_service(version)
    pg_user = detect_postgres_user()

    if dry_run:
        try:
            with tarfile.open(archive_filepath, 'r:gz') as tar:
                members = tar.getmembers()
                print(f"\n[DRY-RUN] Physical backup contents ({len(members)} entries):")
                print(f"  Would restore to: {pgdata}")
                print(f"  PG version: {version}")
                print(f"  PG service: {pg_service}")
                for m in members[:20]:  # show first 20
                    print(f"    {m.name} ({m.size} bytes)")
                if len(members) > 20:
                    print(f"    ... and {len(members) - 20} more entries")
                print(f"\n  Steps:")
                print(f"  1. Stop PostgreSQL: systemctl stop {pg_service}")
                print(f"  2. Clear PGDATA: rm -rf {pgdata}/*")
                print(f"  3. Extract archive to {os.path.dirname(pgdata)}")
                print(f"  4. Fix permissions: chown -R {pg_user}:{pg_user} {pgdata}")
                print(f"  5. Start PostgreSQL: systemctl start {pg_service}")
        except Exception as e:
            logger.error("Cannot read physical backup: %s", e)
            return False
        return True

    try:
        log_warn("PostgreSQL service WILL BE STOPPED during restore")
        log_info("Stopping PostgreSQL: %s", pg_service)
        subprocess.run(['systemctl', 'stop', pg_service], check=True,
                       capture_output=True, text=True)

        pgdata_path = Path(pgdata)
        pgdata_parent = pgdata_path.parent

        if pgdata_path.is_dir():
            logger.info("Clearing existing PGDATA: %s", pgdata)
            # Remove contents but keep the directory itself
            for item in pgdata_path.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        else:
            logger.info("Creating PGDATA directory: %s", pgdata)
            pgdata_path.mkdir(parents=True, exist_ok=True)

        logger.info("Extracting physical backup to %s ...", pgdata_parent)
        with tarfile.open(archive_filepath, 'r:gz') as tar:
            # Check if archive contains the data dir directly or just contents
            members = tar.getmembers()
            if members and '/' not in members[0].name and not members[0].isdir():
                # Archive has just the base dir name as prefix, extract to parent
                tar.extractall(path=pgdata_parent)
            else:
                # Archive has relative paths, extract directly to pgdata
                tar.extractall(path=pgdata)

        logger.info("Fixing permissions: chown -R %s:%s %s", pg_user, pg_user, pgdata)
        subprocess.run(['chown', '-R', f'{pg_user}:{pg_user}', pgdata], check=True,
                       capture_output=True, text=True)

        logger.info("Starting PostgreSQL: %s", pg_service)
        subprocess.run(['systemctl', 'start', pg_service], check=True,
                       capture_output=True, text=True)

        # Wait for PG to be ready
        for i in range(15):
            ready = subprocess.run(['pg_isready', '-h', DB_HOST, '-p', DB_PORT],
                                   capture_output=True, check=False)
            if ready.returncode == 0:
                logger.info("PostgreSQL is accepting connections after %d retries", i + 1)
                break
            if i < 14:
                logger.info("Waiting for PostgreSQL to start (attempt %d/15)...", i + 1)
                time.sleep(2)
        else:
            logger.error("PostgreSQL did not become ready after physical restore")
            return False

        logger.info("Physical restore completed successfully")
        return True

    except subprocess.CalledProcessError as e:
        logger.error("Physical restore failed: %s", e.stderr or e.stdout)
        return False
    except Exception as e:
        logger.error("Unexpected error during physical restore: %s", e)
        return False


def resolve_config_paths():
    """Return list of existing config file paths to back up."""
    paths = []
    for p in CONFIG_PATHS_DEFAULT:
        expanded = os.path.expandvars(p)
        if os.path.exists(expanded):
            paths.append(expanded)
        else:
            logger.debug("Config path not found, skipping: %s", expanded)

    # Add PostgreSQL config files (postgresql.conf, pg_hba.conf, pg_ident.conf)
    pg_ver = detect_pg_version()
    pg_conf_dir = detect_pg_config_dir(pg_ver)
    for conf_file in ['postgresql.conf', 'pg_hba.conf', 'pg_ident.conf']:
        conf_path = os.path.join(pg_conf_dir, conf_file)
        if os.path.exists(conf_path):
            paths.append(conf_path)

    return paths


def backup_config():
    """Archive all critical configuration files into a tar.gz alongside DB backups."""
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    archive_name = f"config_{timestamp}.tar.gz"
    archive_path = os.path.join(BACKUP_DIR, archive_name)

    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)

    config_files = resolve_config_paths()
    if not config_files:
        logger.warning("No configuration files found to back up")
        return None, False

    manifest = []
    try:
        with tarfile.open(archive_path, 'w:gz') as tar:
            for filepath in config_files:
                arcname = filepath.lstrip('/')
                tar.add(filepath, arcname=arcname)
                manifest.append({
                    'source': filepath,
                    'archive_path': arcname,
                })

        archive_size_mb = os.path.getsize(archive_path) / (1024 * 1024)
        logger.info("Config backup completed: %s (%.2f MB, %d files)",
                     archive_name, archive_size_mb, len(config_files))

        metadata = {
            'timestamp': timestamp,
            'filename': archive_name,
            'filepath': archive_path,
            'size_bytes': os.path.getsize(archive_path),
            'size_mb': round(archive_size_mb, 2),
            'file_count': len(config_files),
            'type': 'config',
            'status': 'success',
        }
        log_backup_metadata(metadata)
        return archive_path, True

    except Exception as e:
        logger.error("Config backup failed: %s", e)
        return None, False


def restore_config(archive_filepath, dry_run=False):
    """Restore configuration files from a tar.gz archive."""
    logger.info("Restoring configuration from %s ...", archive_filepath)

    if not os.path.exists(archive_filepath):
        logger.error("Config archive not found: %s", archive_filepath)
        return False

    if dry_run:
        try:
            with tarfile.open(archive_filepath, 'r:gz') as tar:
                print("\n[DRY-RUN] Config archive contents:")
                for member in tar.getmembers():
                    print(f"  {member.name} ({member.size} bytes)")
                print(f"\n  Would extract to root: {CONFIG_RESTORE_DIR}")
        except Exception as e:
            logger.error("Cannot read config archive: %s", e)
            return False
        return True

    try:
        timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
        backup_dir = os.path.join(BACKUP_DIR, '.config_restore_backups')
        Path(backup_dir).mkdir(parents=True, exist_ok=True)

        with tarfile.open(archive_filepath, 'r:gz') as tar:
            for member in tar.getmembers():
                dest_path = os.path.join(CONFIG_RESTORE_DIR, member.name)
                parent_dir = os.path.dirname(dest_path)

                if os.path.exists(dest_path):
                    backup_path = os.path.join(
                        backup_dir,
                        f"{member.name.replace('/', '_')}.{timestamp}"
                    )
                    shutil.copy2(dest_path, backup_path)
                    logger.info("Backed up existing file to: %s", backup_path)

                Path(parent_dir).mkdir(parents=True, exist_ok=True)
                tar.extract(member, path=CONFIG_RESTORE_DIR)

            file_count = len(tar.getmembers())
            logger.info("Config restore completed: %d files restored to %s",
                         file_count, CONFIG_RESTORE_DIR)
            logger.warning("You may need to restart services (systemctl restart hms-api)")

        return True

    except Exception as e:
        logger.error("Config restore failed: %s", e)
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


def find_backup_by_type(before=None, backup_type=None):
    """Find latest backup of a specific type (logical/config/physical)."""
    files = sorted(Path(BACKUP_DIR).iterdir(), reverse=True)
    if backup_type == 'config':
        pattern = "config_*.tar.gz"
    elif backup_type == 'physical':
        pattern = PHYSICAL_BACKUP_PATTERN
    else:
        pattern = BACKUP_PATTERN
    matches = [f for f in files if fnmatch.fnmatch(f.name, pattern)]
    if not matches:
        logger.error("No %s backups found in %s", backup_type or 'database', BACKUP_DIR)
        return None
    if before:
        cutoff = datetime.strptime(before, '%Y-%m-%d %H:%M')
        matches = [m for m in matches if datetime.fromtimestamp(m.stat().st_mtime) <= cutoff]
        if not matches:
            logger.error("No %s backup found before %s", backup_type or 'database', before)
            return None
    return str(matches[0])


def list_backups_all(before=None, json_output=False):
    """List all backup types: logical, config, physical."""
    db_backups = get_backups()
    config_backups = sorted(Path(BACKUP_DIR).glob("config_*.tar.gz"), reverse=True)
    physical_backups = sorted(Path(BACKUP_DIR).glob(PHYSICAL_BACKUP_PATTERN), reverse=True)

    if before:
        cutoff = datetime.strptime(before, '%Y-%m-%d %H:%M')
        db_backups = [b for b in db_backups if b['timestamp'] <= cutoff]
        config_backups = [
            f for f in config_backups
            if datetime.fromtimestamp(f.stat().st_mtime) <= cutoff
        ]
        physical_backups = [
            f for f in physical_backups
            if datetime.fromtimestamp(f.stat().st_mtime) <= cutoff
        ]

    if not db_backups and not config_backups and not physical_backups:
        print("No backups found.")
        return

    if json_output:
        output = {'logical': [], 'config': [], 'physical': []}
        for b in db_backups:
            output['logical'].append({
                'filename': b['filename'],
                'timestamp': b['ts_display'],
                'size_mb': round(b['size_mb'], 2),
                'filepath': b['filepath'],
            })
        for f in config_backups:
            output['config'].append({
                'filename': f.name,
                'timestamp': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size_mb': round(f.stat().st_size / (1024 * 1024), 2),
                'filepath': str(f),
            })
        for f in physical_backups:
            output['physical'].append({
                'filename': f.name,
                'timestamp': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'size_mb': round(f.stat().st_size / (1024 * 1024), 2),
                'filepath': str(f),
            })
        print(json.dumps(output, indent=2))
        return

    def print_section(title, items, name_attr, ts_attr, size_attr):
        print(f"\n{title:^70}")
        print(f"{'Filename':<40} {'Timestamp':<20} {'Size (MB)':<10}")
        print("-" * 70)
        for item in items:
            print(f"{item[name_attr]:<40} {item[ts_attr]:<20} {item[size_attr]:<10.2f}")

    if db_backups:
        print_section('LOGICAL BACKUPS (pg_dump)',
                      [{'Filename': b['filename'], 'Timestamp': b['ts_display'], 'Size MB': b['size_mb']}
                       for b in db_backups],
                      'Filename', 'Timestamp', 'Size MB')
    if config_backups:
        print_section('CONFIG BACKUPS (app + postgresql.conf)',
                      [{'Filename': f.name,
                        'Timestamp': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'Size MB': f.stat().st_size / (1024 * 1024)}
                       for f in config_backups],
                      'Filename', 'Timestamp', 'Size MB')
    if physical_backups:
        print_section('PHYSICAL BACKUPS (PGDATA)',
                      [{'Filename': f.name,
                        'Timestamp': datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'Size MB': f.stat().st_size / (1024 * 1024)}
                       for f in physical_backups],
                      'Filename', 'Timestamp', 'Size MB')
    print()


def parse_args():
    parser = argparse.ArgumentParser(
        description='HMS Full Backup & Restore Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--restore', nargs='?', const='latest', metavar='FILE',
                        help='Restore database from a backup file. '
                             'Use "latest" or omit FILE to restore from the most recent backup.')
    parser.add_argument('--config-restore', nargs='?', const='latest', metavar='FILE',
                        help='Restore configuration files from a config archive. '
                             'Use "latest" or provide a specific file path.')
    parser.add_argument('--physical-restore', nargs='?', const='latest', metavar='FILE',
                        help='Restore PGDATA from a physical backup archive. '
                             'Use "latest" or provide a specific file path.')
    parser.add_argument('--physical-restore-dir', metavar='DIR',
                        help='Target directory for physical restore (default: auto-detected PGDATA)')
    parser.add_argument('--full-restore', nargs='?', const='latest', metavar='TIMESTAMP',
                        help='Full bare-metal restore: physical(PGDATA) → config → logical(DB). '
                             'Provide a timestamp (e.g. 20260522_120000) or "latest".')
    parser.add_argument('--physical', action='store_true',
                        help='Also perform physical PGDATA backup alongside logical dump')
    parser.add_argument('--physical-only', action='store_true',
                        help='Run physical PGDATA backup only')
    parser.add_argument('--db-only', action='store_true',
                        help='Run logical database dump only')
    parser.add_argument('--config-only', action='store_true',
                        help='Run configuration backup only')
    parser.add_argument('--pgdata-dir', metavar='DIR',
                        help='Override PostgreSQL data directory path')
    parser.add_argument('--before', metavar='"YYYY-MM-DD HH:MM"',
                        help='Filter/list backups before this timestamp')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what restore would do without executing it')
    parser.add_argument('--json', action='store_true', help='Output list in JSON format')
    parser.add_argument('--frequent', action='store_true',
                        help='Incremental frequent backup mode: skips verify + rsync, '
                             'excludes static table data, uses hourly retention.')
    return parser.parse_args()


def main():
    args = parse_args()

    # Override PGDATA_DIR if --pgdata-dir was passed
    global PGDATA_DIR
    if args.pgdata_dir:
        PGDATA_DIR = args.pgdata_dir

    # --- LIST ---
    if args.list:
        list_backups_all(before=args.before, json_output=args.json)
        return

    # --- PHYSICAL RESTORE ---
    if args.physical_restore:
        if args.physical_restore == 'latest':
            archive_path = find_backup_by_type(before=args.before, backup_type='physical')
            if not archive_path:
                sys.exit(1)
        else:
            archive_path = args.physical_restore
            if not os.path.exists(archive_path):
                logger.error("Physical backup not found: %s", archive_path)
                sys.exit(1)

        logger.info("Selected physical backup: %s", archive_path)
        target_dir = args.physical_restore_dir or None

        if args.dry_run:
            restore_physical(archive_path, dry_run=True, target_dir=target_dir)
            return

        pgdata = target_dir or detect_pgdata()
        print(f"\nWARNING: This will STOP PostgreSQL and REPLACE the entire PGDATA directory.")
        print(f"  PGDATA target: {pgdata}")
        print(f"  Source archive: {archive_path}")
        print(f"\n  PostgreSQL will be stopped during the restore and restarted afterwards.")
        confirm = input("Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("Physical restore cancelled.")
            sys.exit(0)

        success = restore_physical(archive_path, target_dir=target_dir)
        sys.exit(0 if success else 1)

    # --- CONFIG RESTORE ---
    if args.config_restore:
        if args.config_restore == 'latest':
            archive_path = find_backup_by_type(before=args.before, backup_type='config')
            if not archive_path:
                sys.exit(1)
        else:
            archive_path = args.config_restore
            if not os.path.exists(archive_path):
                logger.error("Config archive not found: %s", archive_path)
                sys.exit(1)

        logger.info("Selected config archive: %s", archive_path)

        if args.dry_run:
            restore_config(archive_path, dry_run=True)
            return

        print(f"\nWARNING: This will OVERWRITE existing configuration files.")
        print(f"Source archive: {archive_path}")
        print(f"Existing files will be backed up to: {BACKUP_DIR}/.config_restore_backups/")
        confirm = input("Are you sure? Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("Restore cancelled.")
            sys.exit(0)

        success = restore_config(archive_path)
        sys.exit(0 if success else 1)

    # --- FULL RESTORE (physical → config → logical) ---
    if args.full_restore:
        ts = args.full_restore
        physical_backup = None
        config_archive = None
        logical_backup = None

        def find_by_ts(ts, pattern):
            if ts == 'latest':
                return None  # will use type-based find
            candidate = os.path.join(BACKUP_DIR, pattern)
            if os.path.exists(candidate):
                return candidate
            return None

        if ts == 'latest':
            physical_backup = find_backup_by_type(before=args.before, backup_type='physical')
            config_archive = find_backup_by_type(before=args.before, backup_type='config')
            logical_backup_obj = find_backup(before=args.before)
            if logical_backup_obj:
                logical_backup = logical_backup_obj['filepath']
        else:
            physical_backup = find_by_ts(ts, f"physical_{ts}.tar.gz") or \
                              find_backup_by_type(before=args.before, backup_type='physical')
            config_archive = find_by_ts(ts, f"config_{ts}.tar.gz") or \
                             find_backup_by_type(before=args.before, backup_type='config')
            logical_backup = find_by_ts(ts, f"{DB_NAME}_{ts}.dump")
            if not logical_backup:
                lb = find_backup(before=args.before)
                if lb:
                    logical_backup = lb['filepath']

        if not physical_backup and not config_archive and not logical_backup:
            logger.error("No backups found. Provide a valid timestamp or 'latest'.")
            sys.exit(1)

        print(f"\n{'=' * 60}")
        print(f"  FULL BARE-METAL RESTORE")
        print(f"{'=' * 60}")
        if physical_backup:
            print(f"  Physical (PGDATA): {physical_backup}")
        if config_archive:
            print(f"  Config:            {config_archive}")
        if logical_backup:
            print(f"  Logical (DB dump): {logical_backup}")
        print(f"{'=' * 60}")

        if args.dry_run:
            if physical_backup:
                restore_physical(physical_backup, dry_run=True)
            if config_archive:
                restore_config(config_archive, dry_run=True)
            if logical_backup:
                restore_database(logical_backup, dry_run=True)
            return

        print(f"\nWARNING: This will:")
        if physical_backup:
            print(f"  - STOP PostgreSQL and REPLACE entire PGDATA directory")
        if config_archive:
            print(f"  - OVERWRITE existing configuration files (app + PG)")
        if logical_backup:
            print(f"  - DROP and recreate the database '{DB_NAME}'")
        print(f"\nAll backups from: {BACKUP_DIR}")
        confirm = input("Are you sure? Type 'yes' to continue: ")
        if confirm.lower() != 'yes':
            print("Full restore cancelled.")
            sys.exit(0)

        all_ok = True

        # Step 1: Restore PGDATA (physical)
        if physical_backup:
            print(f"\n--- Step 1/3: Restoring PGDATA (physical backup) ---")
            if not restore_physical(physical_backup):
                logger.error("Physical restore failed")
                all_ok = False

        # Step 2: Restore config files
        if config_archive and all_ok:
            print(f"\n--- Step 2/3: Restoring configuration ---")
            if not restore_config(config_archive):
                logger.error("Config restore failed")
                all_ok = False

        # Step 3: Restore logical DB dump
        if logical_backup and all_ok:
            print(f"\n--- Step 3/3: Restoring database (logical dump) ---")
            if not restore_database(logical_backup):
                logger.error("Database restore failed")
                all_ok = False

        if all_ok:
            logger.info("=== Full bare-metal restore completed successfully ===")
            logger.info("Run 'systemctl restart hms-api' to apply restored service configuration.")
        else:
            logger.error("=== Full bare-metal restore completed with ERRORS ===")

        sys.exit(0 if all_ok else 1)

    # --- DB RESTORE (logical dump only) ---
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

    # --- BACKUP EXECUTION ---
    logger.info("=== HMS Backup Script Started ===")
    logger.info("Database: %s @ %s:%s", DB_NAME, DB_HOST, DB_PORT)
    logger.info("Backup directory: %s", BACKUP_DIR)
    logger.info("HMS directory: %s", HMS_DIR)

    if args.frequent:
        logger.info("Frequent mode: skipping verify + rsync, incremental (static table data excluded)")
        freq_hours = int(os.getenv('FREQUENT_RETENTION_HOURS', '24'))

    if args.physical_only:
        logger.info("Physical-only mode: PGDATA backup only")

    do_logical = not args.config_only and not args.physical_only
    do_config = not args.db_only and not args.physical_only
    do_physical = args.physical or args.physical_only

    logical_ok = True
    config_ok = True
    physical_ok = True
    logical_filepath = None

    # 1. Logical DB dump
    if do_logical:
        logical_filepath, logical_ok = run_backup(exclude_static_data=args.frequent)
        if not logical_ok:
            logger.error("Logical database backup failed")
            if do_config or do_physical:
                logger.warning("Proceeding with other backup types...")

    # 2. Configuration backup
    if do_config:
        config_archive, config_ok = backup_config()
        if not config_ok:
            logger.warning("Configuration backup had issues")

    # 3. Physical PGDATA backup
    if do_physical:
        physical_archive, physical_ok = backup_physical()
        if not physical_ok:
            logger.warning("Physical PGDATA backup had issues (PG may be down or pg_basebackup unavailable)")

    if not logical_ok and not config_ok and not physical_ok:
        logger.error("All backup types failed")
        sys.exit(1)

    # Post-backup steps
    if not args.frequent and do_logical and logical_filepath:
        verify_success = verify_backup(logical_filepath)
        if not verify_success:
            logger.warning("Backup verification failed - proceeding with caution")
        rsync_to_standby(logical_filepath)

    # Cleanup old backups of all types
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    for pattern in [BACKUP_PATTERN, "config_*.tar.gz", PHYSICAL_BACKUP_PATTERN]:
        for f in Path(BACKUP_DIR).glob(pattern):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime < cutoff:
                    f.unlink()
                    logger.info("Deleted old backup: %s", f.name)
            except Exception:
                continue

    logger.info("=== HMS Backup Script Completed Successfully ===")
    sys.exit(0)


if __name__ == '__main__':
    main()
