Operational helper scripts for Hospital Management System

Location: scripts/ops/

Files:
- backup.sh              Simplified logical backup (pg_dump, retention).
- restore_service.sh     Full bare-metal disaster recovery (PGDATA → config → DB → restart).
- check_replication.sh   Monitor replication lag (used by cron or monitoring tools).
- check_cert_expiry.sh   Check TLS certificate expiry and warn via syslog.

Usage examples

Full bare-metal recovery (when /opt/hms or /var/lib/postgresql is lost):

    sudo bash restore_service.sh
    sudo bash restore_service.sh --backup-dir /backups/local --timestamp 20260522_120000
    sudo bash restore_service.sh --physical-only           # restore PGDATA only
    sudo bash restore_service.sh --skip-physical           # skip PGDATA restore
    sudo bash restore_service.sh --dry-run                 # preview only

Run simplified backup manually (as postgres):

    sudo -u postgres /opt/hms/scripts/ops/backup.sh

Run replication check (as any user):

    /bin/bash $(pwd)/scripts/ops/check_replication.sh
