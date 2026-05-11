Operational helper scripts for Hospital Management System

Location: scripts/ops/

Files:
- backup.sh             Simplified backup script (pg_dump custom format, retention, optional S3 upload).
- check_replication.sh  Monitor replication lag (used by cron or monitoring tools).
- check_cert_expiry.sh  Check TLS certificate expiry and warn via syslog.

Usage examples

Run backup manually (as postgres):

    sudo -u postgres /opt/hms/scripts/backup.sh

Run replication check (as any user):

    /bin/bash $(pwd)/scripts/ops/check_replication.sh
