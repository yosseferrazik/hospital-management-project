# Production Deployment Guide

This guide ties together the canonical runbooks and scripts to deploy the Hospital Management System (HMS) to production. It is written in Spanish to match the operations runbooks but includes all exact commands to run.

Scope
- Prepare primary and standby nodes (Tailscale-connected).
- Install PostgreSQL 14, backups, replication, the HMS API, and systemd units.
- Ensure secrets are provisioned securely and services are tested.

Pre-requisites
- A cloned repository on the machine used to run the primary deploy (or an accessible Git URL for Ansible).
- Two machines (primary and standby) with Tailscale installed and reachable by Tailscale IPs.
- An operator with sudo access on both machines.
- Optional: AWS S3 bucket for offsite backups and IAM role or AWS credentials configured on primary.

High-level steps
1) Prepare secrets
   - Copy and edit the environment template into /etc/hms.env on both primary and standby where required.
     - sudo cp .env.example /etc/hms.env
     - Edit /etc/hms.env and set DB_PASSWORD, AWS credentials (if needed), and any other variables.

2) Deploy primary
   - On primary machine, with repo already cloned into working directory, run:
     - sudo bash scripts/deploy/deploy_primary.sh
   - What this does:
     - Installs packages (postgresql-14, awscli, python3-venv, etc.)
     - Creates directories: /opt/hms/scripts, /backups/local, /backups/archive, /var/log/hms
     - Copies operational scripts to /opt/hms/scripts
     - Installs systemd units: hms-backup.timer + hms-backup.service and (optionally) hms-api.service
     - Prepares API virtualenv under /opt/hms/venv if API code exists and installs requirements

3) Initialize standby
   - On standby machine, run (replace <primary_tailscale_ip>):
     - PRIMARY_IP=<primary_tailscale_ip> sudo bash scripts/deploy/deploy_standby.sh
   - What this does:
     - Installs packages needed for PostgreSQL and base backup
     - Uses pg_basebackup via Tailscale to initialize the standby data directory

4) Validate replication
   - On primary: sudo -u postgres psql -c "SELECT client_addr, state, sync_state FROM pg_stat_replication;"
   - On standby: sudo -u postgres psql -c "SELECT pg_is_in_recovery();"

5) Validate backups
   - Trigger a manual backup on primary: sudo -u postgres /opt/hms/scripts/backup.sh
   - Inspect logs: sudo journalctl -u hms-backup.service -n 200
   - If using S3, verify the file is present in s3://$AWS_BUCKET/

6) Validate API
   - Ensure the API service is running: sudo systemctl status hms-api.service
   - Check logs: sudo tail -n 200 /var/log/hms/api.log
   - Curl health endpoint (if implemented): curl -f http://<primary_ip_or_domain>:5000/health

7) Failover testing (optional, follow runbook)
   - Follow docs/04_Operations_and_Manuals/Replication_and_HA_Runbook.md for promotion and failback.

Runbooks to follow (order)
1. docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md
2. docs/04_Operations_and_Manuals/Replication_and_HA_Runbook.md
3. docs/04_Operations_and_Manuals/Production_Deployment_Guide.md (this file)

Notes on secrets
- Do not store secrets in git. Use /etc/hms.env (600) or a secrets manager.
- For AWS S3 upload, prefer using an EC2 IAM role with S3 PutObject permissions.

If you want, I can:
- Add Ansible tasks to template /etc/hms.env securely (using Ansible Vault)
- Add a smoke-test script that runs basic DB and API checks after deploy
- Add a systemd unit override with EnvironmentFile=/etc/hms.env to ensure services read secrets
