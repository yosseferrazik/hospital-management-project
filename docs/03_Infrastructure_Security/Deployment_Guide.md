# Production Deployment Guide — Hospital Management System

## Architecture

```
Workstation (Tkinter) ──HTTP 5000──► Briar (Gunicorn + Flask)
                                          │
                                          ▼ SQLAlchemy
                                    PostgreSQL 16 Primary
                                          │
                                          │ WAL streaming
                                          ▼
                                    PostgreSQL 16 Standby (Sion, AWS EC2)
```

All traffic flows over **Tailscale overlay network** and the hospital internal LAN. No VPN required.

---

## Node Inventory

| Hostname | Role             | Tailscale IP   | OS                  | Location            |
|----------|------------------|----------------|---------------------|---------------------|
| Briar    | Primary node     | `100.78.155.2` | Ubuntu Server 24.04 | Hospital datacenter |
| Sion     | Secondary node   | `100.98.214.53`| Ubuntu Server 24.04 | AWS EC2             |

### Hardware Specifications

**Primary (Briar):** 4 vCPU, 8 GB RAM, 100 GB SSD, 1 Gbps + Tailscale
**Standby (Sion):** t3.medium (2 vCPU, 4 GB RAM), 80 GB gp3, Tailscale

---

## First-Time Setup on Primary (Briar)

### 1. Clone the repository

```bash
git clone https://github.com/yosseferrazik/hospital-management-project.git /opt/hms/repo
```

### 2. Prepare secrets

```bash
sudo cp .env.example /etc/hms.env
sudo chmod 600 /etc/hms.env
sudo nano /etc/hms.env
```

Set `DATABASE_URL` and `JWT_SECRET_KEY` with real values.

### 3. Run the deploy script

```bash
sudo bash /opt/hms/repo/scripts/deploy/deploy_primary.sh
sudo bash /opt/hms/repo/scripts/deploy/deploy.sh --force
```

### 4. Verify

```bash
curl -f http://localhost:5000/health
sudo systemctl status hms-api
```

---

## What deploy.sh Does

1. **Install system packages** — `python3-venv`, `build-essential`, `libpq-dev`, `git`, `rsync`
2. **Create `hms` system user** — runs the API service
3. **Create directories** — `/opt/hms/releases/`, `/var/log/hms`
4. **Pull or clone repo** — into `/opt/hms/repo`
5. **Create versioned release** — rsync to `/opt/hms/releases/<commit-sha>`
6. **Update symlink** — `/opt/hms/current` points to the new release
7. **Setup virtualenv** — `/opt/hms/venv` with pip dependencies
8. **Install systemd unit** — `hms-api.service` (Gunicorn, 4 workers, port 5000)
9. **Install logrotate** — daily rotation, 14-day retention
10. **Restart service** — `systemctl restart hms-api`
11. **Smoke test** — `curl -f http://localhost:5000/health` (5 retries, 3s interval)
12. **Auto-rollback on failure** — restores previous release symlink
13. **Cleanup** — removes releases older than the last 5

---

## Subsequent Deploys

```bash
# Normal deploy (window-checked: 6-10am or 8-11pm)
sudo bash /opt/hms/repo/scripts/deploy/deploy.sh

# Force deploy outside window
sudo bash /opt/hms/repo/scripts/deploy/deploy.sh --force
```

## Rollback

```bash
sudo bash /opt/hms/current/scripts/deploy/deploy.sh --rollback
```

Reads `PREVIOUS_RELEASE` from `/opt/hms/.deploy_meta`, switches the symlink, restarts the service, and runs the smoke test.

---

## Standby Replica Setup (Sion)

On the standby node:

```bash
PRIMARY_IP=100.78.155.2 sudo bash /opt/hms/repo/scripts/deploy/deploy_standby.sh
```

This stops PostgreSQL, clears the data directory, runs `pg_basebackup` with the `-R` flag (writes `standby.signal`), and starts PostgreSQL. Requires the `replicator` user and `pg_hba.conf` pre-configured on the primary.

---

## Ansible Deployment (Optional)

```bash
cd deploy/ansible
ansible-playbook -i inventory.ini deploy_hms.yml
```

The playbook installs packages, creates the `hms` user, clones the repo, runs `deploy.sh --force` on the primary, installs PostgreSQL 16 on the standby, and runs `deploy_standby.sh`.

---

## Backup Strategy

- **Daily logical backup** via `pg_dump` (custom format)
- **Local retention:** 5 copies in `/backups/local`
- **Off-site copy:** Daily rsync to standby node (Sion)
- **Verification:** `pg_restore -l` lists backup contents

Manual backup:

```bash
sudo bash scripts/ops/backup.sh
```

Automated backup (cron/systemd timer runs `scripts/backup_wrapper.sh` at 2:00 AM).

### Restore

```bash
pg_restore -d hsp_db -c /backups/local/hsp_db_20260518_020000.dump
```

---

## Service Management

```bash
sudo systemctl status hms-api           # Check service status
sudo systemctl restart hms-api           # Restart the API
sudo systemctl enable --now hms-api      # Enable at boot + start
sudo journalctl -u hms-api -n 100 -f    # Tail service logs
sudo journalctl -u hms-api --since "5 min ago"  # Recent logs
tail -f /var/log/hms/error.log          # Gunicorn error log
```

---

## Firewall (UFW)

```bash
sudo ufw allow from 192.168.0.0/16 to any port 5000 proto tcp  # Hospital LAN
sudo ufw allow from 100.64.0.0/10 to any port 5000 proto tcp   # Tailscale
```

PostgreSQL port 5432 must NOT be exposed to the public internet.

---

## Monitoring

| Check                    | Method                            |
|--------------------------|-----------------------------------|
| API health               | `curl -f http://localhost:5000/health` |
| Service status           | `systemctl status hms-api`        |
| Replication lag          | `scripts/ops/check_replication.sh` |
| Certificate expiry       | `scripts/ops/check_cert_expiry.sh` |
| API logs                 | `/var/log/hms/access.log`, `error.log` |

---

## Production Checklist

- [ ] PostgreSQL database `hsp_db` created
- [ ] `/etc/hms.env` created with secure values, mode `600`
- [ ] JWT secret generated with `openssl rand -hex 32`
- [ ] PostgreSQL password set to a strong value
- [ ] UFW allows port 5000 from hospital LAN and Tailscale
- [ ] PostgreSQL port 5432 NOT exposed to public internet
- [ ] Log rotation configured at `/etc/logrotate.d/hms`
- [ ] Backups configured and tested
- [ ] Replication monitoring configured
- [ ] Deployment smoke test passes (`curl -f http://localhost:5000/health`)
