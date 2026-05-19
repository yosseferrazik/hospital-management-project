# HMS Deploy Scripts

This directory contains deployment automation for the Hospital Management System.

## Files

- **`deploy.sh`** — Unified, versioned deploy script (primary node).
- **`deploy_standby.sh`** — Standby PostgreSQL replica initialization.
- **`setup_api.sh`** — Python virtualenv + dependency setup (called by deploy.sh).

## Deploy Script: `deploy.sh`

Performs versioned deploys with automatic rollback on smoke-test failure.

### Features

- Versioned releases in `/opt/hms/releases/<commit_sha>`
- Symlink-based activation (`/opt/hms/current`)
- Shared virtualenv at `/opt/hms/venv` (recreated per deploy)
- Gunicorn + systemd service management
- Health-check smoke test with retries
- Automatic rollback on failure
- Time-window enforcement (mornings 6-10, nights 20-23)
- Cleanup of old releases (keeps last 5)

### Usage

```bash
# Normal deploy (checks time window)
sudo bash scripts/deploy/deploy.sh

# Force deploy outside window
sudo bash scripts/deploy/deploy.sh --force

# Rollback to previous release
sudo bash scripts/deploy/deploy.sh --rollback

# Dev deploy — syncs repo, updates /opt/hms/current symlink to repo, no release
sudo bash scripts/deploy/deploy.sh --dev
```

### First-Time Setup

```bash
# On Briar (hms-primary-node), as root or with sudo:
git clone https://github.com/yosseferrazik/hospital-management-project.git /opt/hms/repo
bash /opt/hms/repo/scripts/deploy/deploy.sh --force
```

### Deploy Flow (release)

1. Install system packages (python3-venv, build-essential, libpq-dev, git, rsync)
2. Create `hms` system user
3. Create directory structure (`/opt/hms/releases/`, `/var/log/hms`)
4. Clone or pull the repo into `/opt/hms/repo`
5. Get commit SHA of HEAD
6. Skip if already deployed at this SHA
7. Rsync repo into `/opt/hms/releases/<sha>`
8. Update `/opt/hms/current` symlink to point to new release
9. Setup venv + install requirements
10. Install systemd unit + logrotate config
11. Restart `hms-api` service
12. Smoke test (curl `/health` with 5 retries)
13. On success: save metadata, clean old releases
14. On failure: rollback symlink, restart previous release

### Deploy Flow (dev — `--dev` flag)

1. Ensure system packages, user, and directories
2. Pull latest from repo
3. Point `/opt/hms/current` symlink directly to `/opt/hms/repo`
4. Setup venv + install requirements
5. Install systemd unit + logrotate config
6. Restart service + smoke test
7. No release versioning, no time-window check

## Standby Setup: `deploy_standby.sh`

```bash
PRIMARY_IP=100.78.155.2 sudo bash scripts/deploy/deploy_standby.sh
```

Requires PostgreSQL 16 to be installed. Runs `pg_basebackup` from primary to initialize the standby data directory with streaming replication.

## See Also

- [Production Deployment Guide](../../docs/DEPLOYMENT.md)
- [Installation Guide](../../docs/INSTALLATION.md)
- [Configuration Guide](../../docs/CONFIGURATION.md)
