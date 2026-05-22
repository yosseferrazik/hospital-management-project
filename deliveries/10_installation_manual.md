# Installation Guide

Everything I did to get the system running from scratch, step by step, with which node each command runs on.

---

## Before you start

### What you need

- Two Ubuntu 24.04 LTS servers (**Briar** and **Sion**) with root access
- A [Tailscale](https://tailscale.com) account to connect them
- Python 3.12, PostgreSQL 16, Git

### Nodes

| Node      | Location                   | LAN IP        | Tailscale IP  | What runs there                |
| --------- | -------------------------- | ------------- | ------------- | ------------------------------ |
| **Briar** | Hospital server room       | 192.168.4.254 | 100.78.155.2  | Flask API + PostgreSQL primary |
| **Sion**  | AWS EC2 (eu-west-3, Paris) | —             | 100.98.214.53 | PostgreSQL standby             |

Hospital users connect to Briar at **192.168.4.254** on the LAN. The admin connects to both servers through **Tailscale**.

Briar server:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-11-19-image.png)

Sion server:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-12-24-image.png)

---

## 1. Install Ubuntu Server 24.04

### On Briar — hardware and partitions

| Component | Spec                                              |
| --------- | ------------------------------------------------- |
| CPU       | Intel Xeon E-2336 (6 cores, 12 threads) @ 4.8 GHz |
| RAM       | 16 GB DDR4 ECC (2 × 8 GB)                         |
| Disk 1    | 240 GB SSD NVMe — OS + system                     |
| Disk 2    | 480 GB SSD SATA — PostgreSQL data + WAL           |
| Network   | 2 × 1 GbE (bonding mode 1 active-passive)         |

LVM layout for Disk 1 (`/dev/sda`, 240 GB NVMe):

```
/dev/sda1   512 MB   /boot/efi    vfat
/dev/sda2   4 GB     [swap]       swap
/dev/sda3   235 GB   LVM VG: vg_system
    ├── vg_system/lv_root     80 GB   /
    ├── vg_system/lv_var      40 GB   /var
    ├── vg_system/lv_log      30 GB   /var/log
    └── vg_system/lv_tmp      10 GB   /tmp
```

LVM layout for Disk 2 (`/dev/sdb`, 480 GB SATA SSD):

```
/dev/sdb1   480 GB   LVM VG: vg_postgres
    ├── vg_postgres/lv_pgdata    350 GB   /var/lib/postgresql/16/main
    └── vg_postgres/lv_pgwal      80 GB   /var/lib/postgresql/16/wal
    (25 GB reserve for LVM snapshots)
```

Separating `lv_pgdata` and `lv_pgwal` on different disks and VGs improves write performance and makes LVM snapshot backups easier.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-08-15-image.png)

### On Sion — hardware and partitions

| Component | Spec                    |
| --------- | ----------------------- |
| CPU       | 2 vCPU (AWS t3.medium)  |
| RAM       | 4 GB                    |
| Disk      | 80 GB gp3 SSD (elastic) |
| Network   | 1 GbE virtual (AWS ENI) |

```
/dev/xvda1   1 MB   [BIOS boot]
/dev/xvda2   79 GB  LVM VG: vg_main
    ├── vg_main/lv_root     20 GB   /
    ├── vg_main/lv_swap      2 GB   swap
    ├── vg_main/lv_pgdata   40 GB   /var/lib/postgresql/16/main
    └── vg_main/lv_pgwal    10 GB   /var/lib/postgresql/16/wal
    (7 GB reserve)
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-00-20-image.png)

### Update and install basic tools (on both)

```bash
# On Briar and Sion
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim ufw openssl
```

---

## 2. Tailscale

This is the VPN connecting Briar and Sion (and my laptop). Auto-encrypted, zero config.

```bash
# On Briar and Sion
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# A browser will open. Authenticate with the project account.
```

Tailscale authentication:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-15-42-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-17-05-image.png)

Tailscale connected:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-22-23-image.png)

From now on, Briar and Sion see each other via 100.x.x.x Tailscale IPs. Ping to confirm:

```bash
# From Briar
ping 100.98.214.53   # should respond
# From Sion
ping 100.78.155.2    # should respond
```

Ping verification:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-23-55-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-24-08-image.png)

---

## 3. Firewall

### On Briar

```bash
sudo ufw allow 22/tcp
sudo ufw allow 5000/tcp
sudo ufw allow from 192.168.4.0/24 to any port 5000
sudo ufw allow from 100.98.214.53 to any port 5432
sudo ufw allow in on tailscale0
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw --force enable
```

UFW status on Briar:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-26-29-image.png)

### On Sion

```bash
sudo ufw allow 22/tcp
sudo ufw allow from 100.78.155.2 to any port 5432
sudo ufw allow in on tailscale0
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw --force enable
```

If Sion is on AWS, also open the ports in its Security Group: 5432 (from Briar only), 22 (from Tailscale only), UDP 41641 (Tailscale).

UFW status on Sion:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-26-10-image.png)

---

## 4. PostgreSQL 16

### On Briar and Sion

```bash
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
sudo apt update
sudo apt install -y postgresql-16 postgresql-contrib-16
psql --version   # should be 16.x
```

PostgreSQL installation:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-29-16-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-29-25-image.png)

---

## 5. TLS certificates

### On Briar

```bash
mkdir -p ~/ssl && cd ~/ssl

# Own CA
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/C=ES/ST=Girona/L=Blanes/O=Hospital de Blanes/CN=CA Hospital"

# Server certificate (with the LAN IP clients will use)
openssl genrsa -out postgresql.key 4096
openssl req -new -key postgresql.key -out postgresql.csr \
  -subj "/C=ES/ST=Girona/L=Blanes/O=Hospital de Blanes/CN=192.168.4.254"
openssl x509 -req -days 365 -in postgresql.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out postgresql.crt

# Install
sudo cp postgresql.crt /etc/ssl/certs/
sudo cp postgresql.key /etc/ssl/private/
sudo cp ca.crt /etc/ssl/certs/
sudo chown postgres:postgres /etc/ssl/private/postgresql.key
sudo chmod 600 /etc/ssl/private/postgresql.key
```

### On Sion (repeat with CN=100.98.214.53)

Same steps but using `CN=100.98.214.53` (Sion's Tailscale IP) in the certificate.

---

## 6. Configure PostgreSQL — Briar (primary)

Edit `/etc/postgresql/16/main/postgresql.conf`:

```ini
listen_addresses = '*'
port = 5432
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 64MB
maintenance_work_mem = 1GB
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1024
max_replication_slots = 5
hot_standby = on
ssl = on
ssl_cert_file = '/etc/ssl/certs/postgresql.crt'
ssl_key_file = '/etc/ssl/private/postgresql.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
```

Edit `/etc/postgresql/16/main/pg_hba.conf`:

```
# Local admin (no SSL)
local   all             postgres                                peer

# Replication over Tailscale (automatic encryption, plus SSL on top)
hostssl replication     replicator      100.98.214.53/32        scram-sha-256

# Application from the hospital LAN
hostssl hsp_db          postgres        192.168.4.0/24            scram-sha-256
hostssl hsp_db          app_admin       192.168.4.0/24          scram-sha-256
hostssl hsp_db          app_doctor      192.168.4.0/24          scram-sha-256
hostssl hsp_db          app_nurse       192.168.4.0/24          scram-sha-256
hostssl hsp_db          app_receptionist 192.168.4.0/24         scram-sha-256
hostssl hsp_db          app_staff       192.168.4.0/24          scram-sha-256

# Application from Briar itself
hostssl hsp_db          postgres        127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_admin       127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_doctor      127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_nurse       127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_receptionist 127.0.0.1/32           scram-sha-256
hostssl hsp_db          app_staff       127.0.0.1/32            scram-sha-256

# Backup user (from Briar itself — needs access to template1 for dropdb/createdb)
host    all             backup_user     127.0.0.1/32            scram-sha-256
host    all             backup_user     ::1/128                 scram-sha-256
```

All remote connections use **SSL** (`hostssl`). Connections over Tailscale have both Tailscale's own encryption **plus** PostgreSQL SSL (double layer).

---

## 7. Configure PostgreSQL — Sion (standby)

Edit `/etc/postgresql/16/main/postgresql.conf`:

```ini
listen_addresses = '*'
port = 5432
max_connections = 50
shared_buffers = 1GB
wal_level = replica
hot_standby = on
primary_conninfo = 'host=100.78.155.2 port=5432 user=replicator password=change_password sslmode=require'
primary_slot_name = 'standby_sion'
ssl = on
ssl_cert_file = '/etc/ssl/certs/postgresql.crt'
ssl_key_file = '/etc/ssl/private/postgresql.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
```

### Restart PostgreSQL on both

```bash
# On Briar and Sion
sudo systemctl restart postgresql-16
sudo systemctl enable postgresql-16
```

---

## 8. Set up replication

### On Briar

```bash
# Replication user
sudo -u postgres psql -c "CREATE ROLE replicator WITH LOGIN REPLICATION PASSWORD 'change_password';"

# Replication slot
sudo -u postgres psql -c "SELECT pg_create_physical_replication_slot('standby_sion');"
```

### On Sion

```bash
sudo systemctl stop postgresql-16
sudo rm -rf /var/lib/postgresql/16/main/*
sudo -u postgres pg_basebackup -h 100.78.155.2 -D /var/lib/postgresql/16/main \
  -U replicator -P -v --slot=standby_sion --wal-method=stream
sudo touch /var/lib/postgresql/16/main/standby.signal
sudo systemctl start postgresql-16
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-05-26-image.png)

### On Briar — verify

```bash
sudo -u postgres psql -c "SELECT slot_name, slot_type, active, restart_lsn FROM pg_replication_slots;"
sudo -u postgres psql -c "SELECT application_name, state, sync_state FROM pg_stat_replication;"
# Should show 'standby_sion', 'physical', 't' and the standby in 'streaming' state
```

Replication verification:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-19-34-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-19-55-image.png)

---

## 9. Clone the repository and prepare the environment

### On Briar

I use a versioned deploy structure so I can roll back quickly if a new version breaks something.

```bash
# Clone once
sudo mkdir -p /opt/hms
cd /opt/hms
sudo git clone https://github.com/yosseferrazik/hospital-management-project.git releases/v1.0

# Symlink for active version
sudo ln -sf /opt/hms/releases/v1.0 /opt/hms/current

# Python virtual environment
cd /opt/hms/current/server/src
sudo python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

The `deploy/deploy.sh` script automates this: it creates a new release directory, symlinks `current`, runs a smoke test, and rolls back if it fails.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-25-19-image.png)

---

## 10. Environment variables

### On Briar — create `server/src/.env`

```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/hsp_db
JWT_SECRET_KEY=openssl rand -hex 32   # run this and paste the output
DB_NAME=hsp_db
EXTERNAL_API_URL=https://api.seg-social.es/export
EXTERNAL_API_USERNAME=api_user
EXTERNAL_API_PASSWORD=api_password
```

---

## 11. Create the database and load schemas

### On Briar

```bash
sudo -u postgres psql -c "CREATE DATABASE hsp_db;"
sudo -u postgres psql -d hsp_db -f /opt/hms/current/scripts/sql/schema.sql
sudo -u postgres psql -d hsp_db -f /opt/hms/current/scripts/sql/security.sql
sudo -u postgres psql -d hsp_db -f /opt/hms/current/scripts/sql/initial_script.sql
```

Verify:

```bash
sudo -u postgres psql -d hsp_db -c "\dt"
# Should show 22 tables
```

Database verification:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-43-29-image.png)

---

## 12. Start the API in dev mode (test)

### On Briar

```bash
cd /opt/hms/current/server/src
source .venv/bin/activate
python run.py
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-44-37-image.png)

Check it works:

```bash
curl http://192.168.4.254:5000/health
# {"status":"healthy","database":"connected","timestamp":"..."}
```

API health check:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-45-45-image.png)

---

## 13. systemd service (production)

### On Briar

The best option to avoid errors is to use the developed scripts.

`/scripts/deploy/deploy_primary.sh` <- Installs dependencies, creates env files, etc.

Deploy primary script:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-59-09-image.png)

Then we execute `/scripts/deploy.sh` this clones the repo, installs venv and installs the whole service.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-02-03-08-image.png)

We check that the service is running correctly:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-02-04-52-image.png)

---

## 14. Desktop client

On your laptop or a hospital computer (inside the 192.168.4.x LAN):

```bash
git clone https://github.com/yosseferrazik/hospital-management-project.git
cd hospital-management-project/desktop/src
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate    # Linux
pip install -r requirements.txt
```

Create `desktop/src/.env`:

```
API_BASE_URL=http://192.168.4.254:5000/api
```

Run:

```bash
python main.py
```

(On Ubuntu you may need `sudo apt install python3-tk`)

Desktop client running:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-18-15-17-image.png)

---

## 15. First login

| Username | Password                |
| -------- | ----------------------- |
| `yossef` | `ChangeMePleaseChange!` |

Change the password on first login.

---

## 16. Desktop client setup (on LAN PCs)

On each hospital computer that will use the application, create `desktop/src/.env` with `API_BASE_URL=http://192.168.4.254:5000/api`.

To make this easier, I prepared an installer with Inno Setup (the `.exe` already includes the configured `.env`); it's at `desktop/dist/HMS_Client_Setup_v2026.05.19.exe`.

---

## 17. Automated backups & full-service recovery

The backup system uses **three layers** to protect against any data loss scenario:

| Layer        | Backup file         | Created by              | Protects against                        |
| ------------ | ------------------- | ----------------------- | --------------------------------------- |
| **Physical** | `physical_*.tar.gz` | `--physical` flag       | Deleted `/var/lib/postgresql/`          |
| **Logical**  | `hsp_db_*.dump`     | default (`pg_dump -Fc`) | Corrupted/deleted database              |
| **Config**   | `config_*.tar.gz`   | default (auto)          | Lost `.env`, systemd, `postgresql.conf` |

### Backup script

`scripts/backup_database.py` runs on **Briar**.

```bash
# Default: logical dump + config backup
python scripts/backup_database.py

# Add physical PGDATA backup
python scripts/backup_database.py --physical

# PGDATA only
python scripts/backup_database.py --physical-only
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-17-31-12-image.png)

### On Briar — cron setup

```bash
sudo crontab -e
# Add the lines (replace <password>):
#
# Daily: logical dump + config (with verify + rsync if configured)
0 2 * * * HMS_DB_PASSWORD='<password>' cd /opt/hms/current && python scripts/backup_database.py >> /tmp/hms_backup_cron.log 2>&1
#
# Daily physical PGDATA backup (separate schedule, heavy I/O)
0 3 * * * HMS_DB_PASSWORD='<password>' cd /opt/hms/current && python scripts/backup_database.py --physical-only >> /tmp/hms_backup_physical.log 2>&1
#
# Every 15 min — quick logical dump for minute-level RPO
*/15 * * * * HMS_DB_PASSWORD='<password>' cd /opt/hms/current && python scripts/backup_database.py --frequent >> /tmp/hms_backup_frequent.log 2>&1
```

> **Passwordless** via `.pgpass`:
> 
> ```bash
> echo 'localhost:5432:hsp_db:backup_user:<password>' | sudo tee -a /root/.pgpass
> sudo chmod 600 /root/.pgpass
> ```

**Config files backed up automatically each run:**
`server/src/.env`, `desktop/src/.env`, `inventory.ini`, `.deploy_meta`, `hms-api.service`, `logrotate.d/hms`, `/etc/hms.env`, `postgresql.conf`, `pg_hba.conf`, `pg_ident.conf`.

### Rsync to Sion (standby) — optional

**Disabled by default.** To enable:

**1. On Sion** — prepare the directory:

```bash
sudo mkdir -p /backups/local
sudo chown ubuntu:ubuntu /backups/local
```

**2. On Briar** — generate SSH key and copy to Sion:

```bash
sudo ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N ""
sudo cat /root/.ssh/id_ed25519.pub
# Copy the output, then from your admin machine with the .pem file:
# ssh -i <your.pem> ubuntu@100.98.214.53 "echo '<paste_key>' | sudo tee -a /home/ubuntu/.ssh/authorized_keys"
```

**3. Run or schedule with the env vars (replace `<password>`):**

```bash
# Manual (STANDBY_USER defaults to ubuntu)
sudo HMS_DB_PASSWORD='<password>' HMS_STANDBY_HOST=100.98.214.53 python3 scripts/backup_database.py

# Cron (with password)
0 2 * * * HMS_DB_PASSWORD='<password>' HMS_STANDBY_HOST=100.98.214.53 cd /opt/hms/current && python3 scripts/backup_database.py >> /tmp/hms_backup_cron.log 2>&1

# Cron (using .pgpass — no password in command line)
0 2 * * * HMS_STANDBY_HOST=100.98.214.53 cd /opt/hms/current && python3 scripts/backup_database.py >> /tmp/hms_backup_cron.log 2>&1
```

**Verify:**

```bash
echo "STANDBY_HOST=$HMS_STANDBY_HOST"   # empty = disabled
# On Sion:
ls -la /backups/local/                  # should show .dump + .tar.gz files
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-54-32-image.png)

### Restore operations

#### List available backups of all types

```bash
python scripts/backup_database.py --list
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-57-42-image.png)

#### Restore logical database

```bash
# Most recent backup
python scripts/backup_database.py --restore latest

# Point-in-time
python scripts/backup_database.py --restore latest --before "2026-05-20 14:30"

# Specific file
python scripts/backup_database.py --restore /backups/local/hsp_db_20260520_020000.dump

# Dry-run (preview only)
python scripts/backup_database.py --restore latest --dry-run
```

#### Restore app + PostgreSQL configuration

```bash
python scripts/backup_database.py --config-restore latest
```

#### Restore PGDATA (physical — when /var/lib/postgresql is lost)

```bash
python scripts/backup_database.py --physical-restore latest
```

This stops PostgreSQL, replaces the data directory, fixes permissions, and restarts.

#### Full bare-metal restore (all three layers)

```bash
python scripts/backup_database.py --full-restore latest
```

Order of restore: **PGDATA → config files → logical DB dump**.

---

## 18. Failover

### If Briar goes down — promote Sion to primary

```bash
# On Sion
sudo -u postgres pg_ctl promote -D /var/lib/postgresql/16/main

# Then reconfigure the API .env to point to Sion
# DATABASE_URL=postgresql://postgres:password@100.98.214.53:5432/hsp_db
```

Failover verification:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-59-40-image.png)

### Return to normal (rebuild Sion as standby)

```bash
# On Sion
sudo systemctl stop postgresql-16
sudo rm -rf /var/lib/postgresql/16/main/*
sudo -u postgres pg_basebackup -h 100.78.155.2 -D /var/lib/postgresql/16/main \
  -U replicator -P -v --slot=standby_sion --wal-method=stream
sudo touch /var/lib/postgresql/16/main/standby.signal
sudo systemctl start postgresql-16
```

Rebuild verification:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-19-02-00-image.png)

---

## 19. Web dashboard

Open a browser from any computer on the LAN:

```
http://192.168.4.254:5000/api/dashboard/view
```

For PowerBI: `http://192.168.4.254:5000/api/dashboard/stats`

Dashboard:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-19-02-35-image.png)

---

## 20. Monitoring

| What                   | Where to run   | Tool                               |
| ---------------------- | -------------- | ---------------------------------- |
| Replication lag        | Briar          | `scripts/ops/check_replication.sh` |
| SSL certificate expiry | Briar and Sion | `scripts/ops/check_cert_expiry.sh` |
| Disk space             | Briar and Sion | `df -h`                            |
| Audit logs             | App (Admin)    | Audit Logs section in the client   |
| PostgreSQL logs        | Briar and Sion | `journalctl -u postgresql-16`      |

Screenshots:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-40-14-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-40-30-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-40-47-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-40-57-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-41-16-image.png)

---

## 21. Verification checklist

| Test               | Where          | Command                                                     |
| ------------------ | -------------- | ----------------------------------------------------------- |
| API works          | Any LAN PC     | `curl http://192.168.4.254:5000/health`                     |
| Login works        | Any LAN PC     | `curl -X POST http://192.168.4.254:5000/api/auth/login ...` |
| Tables created     | On Briar       | `sudo -u postgres psql -d hsp_db -c "\dt"`                  |
| Replication active | On Briar       | `psql -c "SELECT state FROM pg_stat_replication;"`          |
| Dashboard          | Browser on LAN | `http://192.168.4.254:5000/api/dashboard/view`              |

Screenshots:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-41-48-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-42-07-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-42-29-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-42-51-image.png)

---

## 22. Problems I ran into and how I fixed them

| Problem                               | Where        | Solution                                               |
| ------------------------------------- | ------------ | ------------------------------------------------------ |
| `pg_hba.conf` wouldn't let me connect | Briar        | Changed `127.0.0.1/32` to `192.168.4.0/24` for the LAN |
| pg_basebackup timed out               | Briar → Sion | Added `sslmode=require` to `primary_conninfo`          |
| Tailscale wouldn't connect            | Sion (AWS)   | Was missing UDP port 41641 in the Security Group       |
| High replication lag                  | Briar        | `wal_keep_size` was 64 MB, raised it to 1024 MB        |
| psycopg2 wouldn't install             | Briar        | `sudo apt install libpq-dev`                           |
| Tkinter error on Linux                | Hospital PC  | `sudo apt install python3-tk`                          |
| Serial IDs reset on restore           | Briar        | Switched from plain text `pg_dump` to `pg_dump -Fc`    |
| Datacenter firewall blocked API       | Hospital LAN | Coordinated with the network team to open port 5000    |
