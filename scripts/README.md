# HMS Scripts

This directory contains operational and deployment scripts for the Hospital Management System.

## Directory Structure

```
scripts/
├── deploy/          # Deployment automation (deploy.sh, setup_api.sh, deploy_standby.sh)
├── ops/             # Operational helpers (backup, replication, cert expiry)
├── systemd/         # systemd service units
├── logrotate/       # Log rotation configuration
├── sql/             # Database schema, security, seed scripts
├── backup_database.py       # Python automated backup script
└── backup_wrapper.sh        # Cron wrapper for backup
```

## Deployment

See `scripts/deploy/README.md` for the versioned deploy workflow.

## Operations

See `scripts/ops/README.md` for monitoring and maintenance helpers.

## systemd

The `hms-api.service` unit is deployed automatically by `deploy.sh`. Source template at `scripts/systemd/hms-api.service`.

## Logrotate

Config at `scripts/logrotate/hms` — installed to `/etc/logrotate.d/hms` during deploy.
