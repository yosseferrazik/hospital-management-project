# Production Deployment Guide

This guide ties together the canonical runbooks and scripts to deploy the Hospital Management System (HMS) to production.

## Scope

- Prepare primary node (Briar) and standby node (Sion), connected via Tailscale.
- Deploy the HMS API with Gunicorn + systemd, versioned releases, and smoke tests.
- Configure PostgreSQL 16 replication and backups.
- Provision secrets securely.

## Prerequisites

- Two Ubuntu Server 24.04 nodes with Tailscale installed and reachable by their Tailscale IPs.
- An operator with sudo access on both nodes (user `yerrazik`).
- GitHub SSH access configured on the primary node.

## High-Level Steps

### 1) Prepare secrets

Copy the environment template to `/etc/hms.env` and fill in secure values:

```bash
sudo cp .env.example /etc/hms.env
sudo chmod 600 /etc/hms.env
sudo nano /etc/hms.env
```

Required variables:
- `DATABASE_URL` — PostgreSQL connection string (e.g. `postgresql://postgres:password@localhost:5432/hsp_db`)
- `JWT_SECRET_KEY` — Generate with `openssl rand -hex 32`

### 2) First-time deploy on primary

```bash
# Clone the repository
git clone https://github.com/yosseferrazik/hospital-management-project.git /opt/hms/repo

# Run the deploy script
sudo bash /opt/hms/repo/scripts/deploy/deploy.sh --force
```

What this does:
- Installs system packages (python3-venv, build-essential, libpq-dev, git, rsync)
- Creates `hms` system user
- Creates directory structure: `/opt/hms/releases/`, `/var/log/hms`
- Pulls latest code, creates versioned release at `/opt/hms/releases/<sha>`
- Sets up Python virtualenv at `/opt/hms/venv` and installs requirements
- Creates symlink `/opt/hms/current` pointing to the new release
- Installs systemd unit `hms-api.service` (Gunicorn on port 5000)
- Installs logrotate config for `/var/log/hms/*.log`
- Runs smoke test: `curl -f http://localhost:5000/health`

### 3) Subsequent deploys

```bash
sudo bash /opt/hms/repo/scripts/deploy/deploy.sh
# or from anywhere:
sudo bash /opt/hms/current/scripts/deploy/deploy.sh
```

Use `--force` to bypass the time-window check (mornings 6-10, nights 20-23).

### 4) Rollback

```bash
sudo bash /opt/hms/current/scripts/deploy/deploy.sh --rollback
```

Restores the previous release by switching the `/opt/hms/current` symlink.

### 5) Initialize standby

On the standby node (Sion):

```bash
PRIMARY_IP=100.78.155.2 sudo bash scripts/deploy/deploy_standby.sh
```

This runs `pg_basebackup` from the primary to initialize streaming replication.

### 6) Validate deployment

```bash
# Check API service
sudo systemctl status hms-api.service

# Check health endpoint
curl -f http://localhost:5000/health

# Check logs
sudo journalctl -u hms-api.service -n 50
tail -f /var/log/hms/error.log
```

### 7) Ansible deployment (optional)

```bash
cd deploy/ansible
ansible-playbook -i inventory.ini deploy_hms.yml
```

## Related Runbooks

1. `docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md`
2. `docs/04_Operations_and_Manuals/Replication_and_HA_Runbook.md`
3. `docs/04_Operations_and_Manuals/Installation_Guide.md`

## Notes on Secrets

- Do not store secrets in git. Use `/etc/hms.env` (owned by root, mode 600).
- Generate `JWT_SECRET_KEY` with `openssl rand -hex 32`. Never use the example value in production.
