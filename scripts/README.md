# HMS Scripts

This directory contains operational and deployment scripts for the Hospital Management System.

## Directory Structure

```
scripts/
├── deploy/                  # Deployment automation (deploy.sh, setup_api.sh, deploy_standby.sh)
├── ops/                     # Operational helpers (backup, restore_service, replication, cert expiry)
├── systemd/                 # systemd service units
├── logrotate/               # Log rotation configuration
├── sql/                     # Database schema, security, seed scripts
├── backup_database.py       # Python backup/restore script (logical, config, physical PGDATA)
└── backup_wrapper.sh        # Cron wrapper for backup
```

## Backup system (three-layer)

`backup_database.py` covers three layers of protection:

| Layer | File pattern | Creates with |
|-------|-------------|--------------|
| **Physical** (PGDATA) | `physical_*.tar.gz` | `--physical` or `--physical-only` |
| **Logical** (pg_dump) | `hsp_db_*.dump` | default or `--db-only` |
| **Config** (app + PG .conf) | `config_*.tar.gz` | default or `--config-only` |

All restore modes are available: `--restore`, `--config-restore`, `--physical-restore`, `--full-restore`.

See `docs/02_database/high_availability.md` for full usage reference.

## Disaster recovery

`scripts/ops/restore_service.sh` performs full bare-metal recovery:
1. Deploy app from git
2. Restore PGDATA (physical)
3. Restore config (app + postgresql.conf)
4. Restore logical DB dump
5. Restart service + smoke test

## Deployment

See `scripts/deploy/README.md` for the versioned deploy workflow.  
See `docs/04_deployment/installation_guide.md` for the full production deployment guide.

## Operations

See `scripts/ops/README.md` for monitoring and maintenance helpers.  
See `docs/04_deployment/configuration.md` for logging and backup configuration.

## systemd

The `hms-api.service` unit is deployed automatically by `deploy.sh`. Source template at `scripts/systemd/hms-api.service`.

## Logrotate

Config at `scripts/logrotate/hms` — installed to `/etc/logrotate.d/hms` during deploy.
