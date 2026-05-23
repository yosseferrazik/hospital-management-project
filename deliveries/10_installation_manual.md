# Installation Guide

Everything done to get the system running from scratch, step by step, with the node on which each command runs.

---

## Table of Contents

1. [Before you start](#before-you-start)
2. [Install Ubuntu Server 24.04](#1-install-ubuntu-server-2404)
3. [Tailscale](#2-tailscale)
4. [Firewall](#3-firewall)
5. [PostgreSQL 16](#4-postgresql-16)
6. [TLS certificates](#5-tls-certificates)
7. [Configure PostgreSQL — Briar (primary)](#6-configure-postgresql--briar-primary)
8. [Configure PostgreSQL — Sion (standby)](#7-configure-postgresql--sion-standby)
9. [Set up replication](#8-set-up-replication)
10. [Clone the repository and prepare the environment](#9-clone-the-repository-and-prepare-the-environment)
11. [Environment variables](#10-environment-variables)
12. [Create the database and load schemas](#11-create-the-database-and-load-schemas)
13. [Start the API in dev mode](#12-start-the-api-in-dev-mode-test)
14. [systemd service (production)](#13-systemd-service-production)
15. [Desktop client](#14-desktop-client)
16. [First login](#15-first-login)
17. [Desktop client setup (on LAN PCs)](#16-desktop-client-setup-on-lan-pcs)
18. [Automated backups & full-service recovery](#17-automated-backups--full-service-recovery)
19. [Failover](#18-failover)
20. [Web dashboard](#19-web-dashboard)
21. [Monitoring](#20-monitoring)
22. [Verification checklist](#21-verification-checklist)
23. [Troubleshooting](#22-troubleshooting)

---

## Before you start

### Prerequisites

- Two Ubuntu 24.04 LTS servers (**Briar** and **Sion**) with root access.
- A [Tailscale](https://tailscale.com) account to connect them over an encrypted mesh VPN.
- Python 3.12, PostgreSQL 16, Git installed.

### Node overview

| Node      | Location                   | LAN IP        | Tailscale IP  | Role                                |
|-----------|----------------------------|---------------|---------------|-------------------------------------|
| **Briar** | Hospital server room       | 192.168.4.254 | 100.78.155.2  | Flask API + PostgreSQL primary      |
| **Sion**  | AWS EC2 (eu-west-3, Paris) | —             | 100.98.214.53 | PostgreSQL standby (disaster recovery) |

Hospital users connect to Briar at **192.168.4.254** on the LAN. The administrator connects to both servers through **Tailscale** from any location.

### Network topology (text description)

```
┌──────────────────────────────────────────────────────────────────┐
│                        Hospital LAN (192.168.4.0/24)             │
│                                                                  │
│  ┌─────────────┐    ┌──────────────┐     ┌──────────────────┐   │
│  │ Doctor PC    │    │ Reception PC │     │ Admin Laptop     │   │
│  │ (192.168.4.x)│    │ (192.168.4.x)│     │ (Tailscale)      │   │
│  └──────┬──────┘    └──────┬───────┘     └────────┬─────────┘   │
│         │                  │                       │              │
│         └──────────────────┼───────────────────────┘              │
│                            │                                     │
│                   ┌────────▼────────┐                            │
│                   │   Briar Server  │   LAN: 192.168.4.254       │
│                   │   Flask API     │   TS:  100.78.155.2        │
│                   │   PostgreSQL 16 │                            │
│                   │   (PRIMARY)     │                            │
│                   └────────┬────────┘                            │
│                            │ Tailscale (encrypted)               │
│                            │                                      │
└────────────────────────────┼──────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Sion Server   │   AWS EC2 (eu-west-3)
                    │   PostgreSQL 16 │   TS: 100.98.214.53
                    │   (STANDBY)     │
                    └─────────────────┘
```

Briar server:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-11-19-image.png)

Sion server:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-12-24-image.png)

---

## 1. Install Ubuntu Server 24.04

### On Briar — hardware and partitions

| Component | Spec                                              |
|-----------|---------------------------------------------------|
| CPU       | Intel Xeon E-2336 (6 cores, 12 threads) @ 4.8 GHz |
| RAM       | 16 GB DDR4 ECC (2 × 8 GB)                         |
| Disk 1    | 240 GB SSD NVMe — OS + system                     |
| Disk 2    | 480 GB SSD SATA — PostgreSQL data + WAL           |
| Network   | 2 × 1 GbE (bonding mode 1 active-passive)         |

**LVM layout for Disk 1** (`/dev/sda`, 240 GB NVMe):

```
/dev/sda1   512 MB   /boot/efi    vfat
/dev/sda2   4 GB     [swap]       swap
/dev/sda3   235 GB   LVM VG: vg_system
    ├── vg_system/lv_root     80 GB   /
    ├── vg_system/lv_var      40 GB   /var
    ├── vg_system/lv_log      30 GB   /var/log
    └── vg_system/lv_tmp      10 GB   /tmp
```

**LVM layout for Disk 2** (`/dev/sdb`, 480 GB SATA SSD):

```
/dev/sdb1   480 GB   LVM VG: vg_postgres
    ├── vg_postgres/lv_pgdata    350 GB   /var/lib/postgresql/16/main
    └── vg_postgres/lv_pgwal      80 GB   /var/lib/postgresql/16/wal
    (25 GB reserved for LVM snapshots)
```

Separating `lv_pgdata` and `lv_pgwal` on different disks and volume groups improves write performance (reduces I/O contention) and makes LVM snapshot backups easier.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-08-15-image.png)

### On Sion — hardware and partitions

| Component | Spec                    |
|-----------|-------------------------|
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

Tailscale is the VPN connecting Briar and Sion (and the admin laptop). It provides WireGuard-based auto-encrypted tunnels with zero configuration.

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

From now on, Briar and Sion see each other via `100.x.x.x` Tailscale IPs. Verify connectivity:

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

The firewall restricts access to only necessary ports and sources.

### On Briar

```bash
sudo ufw allow 22/tcp                                          # SSH
sudo ufw allow 5000/tcp                                        # Flask API
sudo ufw allow from 192.168.4.0/24 to any port 5000            # API from LAN
sudo ufw allow from 100.98.214.53 to any port 5432             # PostgreSQL replication from Sion
sudo ufw allow in on tailscale0                                # Allow all Tailscale traffic
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw --force enable
```

**Rules breakdown:**

| Rule                                     | Purpose                                |
|------------------------------------------|----------------------------------------|
| `allow 22/tcp`                           | SSH access (from LAN or Tailscale)     |
| `allow 5000/tcp`                         | Flask API access                       |
| `from 192.168.4.0/24 to any port 5000`   | Restrict API to hospital LAN           |
| `from 100.98.214.53 to any port 5432`    | Allow only Sion to reach PostgreSQL    |
| `allow in on tailscale0`                 | Allow all traffic over Tailscale       |

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

If Sion is on AWS, also open the ports in its **Security Group**:

| Port       | Protocol | Source         | Purpose                   |
|------------|----------|----------------|---------------------------|
| 5432       | TCP      | Briar TS IP    | PostgreSQL replication    |
| 22         | TCP      | Tailscale only | SSH                       |
| 41641      | UDP      | 0.0.0.0/0      | Tailscale WireGuard       |

UFW status on Sion:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-26-10-image.png)

---

## 4. PostgreSQL 16

### On Briar and Sion

```bash
# Add PostgreSQL official repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
sudo apt update
sudo apt install -y postgresql-16 postgresql-contrib-16
psql --version   # should output 16.x
```

PostgreSQL installation:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-29-16-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-29-25-image.png)

### Service management

```bash
sudo systemctl status postgresql-16    # Check if running
sudo systemctl stop postgresql-16      # Stop
sudo systemctl start postgresql-16     # Start
sudo systemctl restart postgresql-16   # Restart
sudo systemctl enable postgresql-16    # Enable on boot
```

---

## 5. TLS certificates

PostgreSQL connections use SSL with a custom CA and server certificates.

### On Briar

```bash
mkdir -p ~/ssl && cd ~/ssl

# Create own CA (valid 10 years)
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

Same steps as above but using `CN=100.98.214.53` (Sion's Tailscale IP) in the certificate.

---

## 6. Configure PostgreSQL — Briar (primary)

### postgresql.conf

Edit `/etc/postgresql/16/main/postgresql.conf`:

```ini
listen_addresses = '*'
port = 5432
max_connections = 200
shared_buffers = 4GB                    # 25% of RAM
effective_cache_size = 12GB             # 75% of RAM
work_mem = 64MB
maintenance_work_mem = 1GB
wal_level = replica                     # Required for replication
max_wal_senders = 5                     # Max standby connections
wal_keep_size = 1024                    # MB of WAL to retain
max_replication_slots = 5               # Physical + logical slots
hot_standby = on                        # Allow read-only queries on standby
ssl = on
ssl_cert_file = '/etc/ssl/certs/postgresql.crt'
ssl_key_file = '/etc/ssl/private/postgresql.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
```

### pg_hba.conf

Edit `/etc/postgresql/16/main/pg_hba.conf`:

```bash
# Local admin (no SSL required)
local   all             postgres                                peer

# Replication over Tailscale (Tailscale encryption + SSL on top)
hostssl replication     replicator      100.98.214.53/32        scram-sha-256

# Application from the hospital LAN
hostssl hsp_db          postgres        192.168.4.0/24          scram-sha-256
hostssl hsp_db          app_admin       192.168.4.0/24          scram-sha-256
hostssl hsp_db          app_doctor      192.168.4.0/24          scram-sha-256
hostssl hsp_db          app_nurse       192.168.4.0/24          scram-sha-256
hostssl hsp_db          app_receptionist 192.168.4.0/24         scram-sha-256
hostssl hsp_db          app_staff       192.168.4.0/24          scram-sha-256

# Application from Briar itself (localhost)
hostssl hsp_db          postgres        127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_admin       127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_doctor      127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_nurse       127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_receptionist 127.0.0.1/32           scram-sha-256
hostssl hsp_db          app_staff       127.0.0.1/32            scram-sha-256

# Backup user (needs access to template1 for dropdb/createdb operations)
host    all             backup_user     127.0.0.1/32            scram-sha-256
host    all             backup_user     ::1/128                 scram-sha-256
```

**Security note:** All remote connections use `hostssl` (SSL mandatory). Connections over Tailscale have both Tailscale's own encryption **plus** PostgreSQL SSL (double encryption layer).

---

## 7. Configure PostgreSQL — Sion (standby)

Edit `/etc/postgresql/16/main/postgresql.conf`:

```ini
listen_addresses = '*'
port = 5432
max_connections = 50                     # Lower than primary
shared_buffers = 1GB                     # 25% of 4GB RAM
wal_level = replica
hot_standby = on                         # Allow read-only queries
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

### On Briar (primary)

```bash
# Create replication user
sudo -u postgres psql -c "CREATE ROLE replicator WITH LOGIN REPLICATION PASSWORD 'change_password';"

# Create physical replication slot
sudo -u postgres psql -c "SELECT pg_create_physical_replication_slot('standby_sion');"
```

### On Sion (standby)

```bash
sudo systemctl stop postgresql-16
sudo rm -rf /var/lib/postgresql/16/main/*
sudo -u postgres pg_basebackup -h 100.78.155.2 -D /var/lib/postgresql/16/main \
  -U replicator -P -v --slot=standby_sion --wal-method=stream
sudo touch /var/lib/postgresql/16/main/standby.signal
sudo systemctl start postgresql-16
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-05-26-image.png)

### On Briar — verify replication

```bash
sudo -u postgres psql -c "SELECT slot_name, slot_type, active, restart_lsn FROM pg_replication_slots;"
sudo -u postgres psql -c "SELECT application_name, state, sync_state FROM pg_stat_replication;"
```

Expected output:
- `slot_name` = `standby_sion`, `slot_type` = `physical`, `active` = `t`
- `state` = `streaming`, `sync_state` = `async`

Replication verification:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-19-34-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-19-55-image.png)

---

## 9. Clone the repository and prepare the environment

### On Briar

A versioned deploy structure is used so rollbacks are quick if a new version breaks something.

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

### Deploy script

The `deploy/deploy.sh` script automates the full process: cloning a new release, creating the symlink, running a smoke test, and rolling back on failure.

```bash
cd /opt/hms
sudo ./current/scripts/deploy/deploy.sh    # see deploy/deploy_primary.sh for details
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-25-19-image.png)

### Release structure

```
/opt/hms/
├── current -> /opt/hms/releases/v1.0/      # Active symlink
├── releases/
│   ├── v1.0/                                # Initial release
│   └── v1.1/                                # Future update
├── backups/
│   └── local/                               # Backup storage
└── deploy/
    └── deploy.sh                            # Deployment automation
```

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

**Important:** Run `openssl rand -hex 32` to generate a cryptographically strong `JWT_SECRET_KEY`. Never use a default value.

---

## 11. Create the database and load schemas

### On Briar

```bash
sudo -u postgres psql -c "CREATE DATABASE hsp_db;"
sudo -u postgres psql -d hsp_db -f /opt/hms/current/scripts/sql/schema.sql
sudo -u postgres psql -d hsp_db -f /opt/hms/current/scripts/sql/security.sql
sudo -u postgres psql -d hsp_db -f /opt/hms/current/scripts/sql/initial_script.sql
```

### Verify tables

```bash
sudo -u postgres psql -d hsp_db -c "\dt"
# Should show 22 tables
```

The 22 tables include: `patients`, `staff`, `doctors`, `nurses`, `visits`, `surgeries`, `admissions`, `prescriptions`, `exams`, `rooms`, `floors`, `specialties`, `users`, `roles`, `audit_logs`, and supporting tables.

Database verification:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-41-48-image.png)

---

## 12. Start the API in dev mode (test)

### On Briar

```bash
cd /opt/hms/current/server/src
source .venv/bin/activate
python run.py
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-44-37-image.png)

### Check it works

```bash
curl http://192.168.4.254:5000/health
# Expected: {"status":"healthy","database":"connected","timestamp":"..."}
```

API health check:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-45-45-image.png)

---

## 13. systemd service (production)

### On Briar

The best option to avoid errors is to use the developed scripts.

**`/scripts/deploy/deploy_primary.sh`** — Installs dependencies, creates environment files, sets up systemd, etc.

Deploy primary script:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-01-59-09-image.png)

Then execute **`/scripts/deploy.sh`** which clones the repo, installs the virtual environment, and installs the whole service.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-02-03-08-image.png)

### systemd unit file

The service is managed via a systemd unit at `/etc/systemd/system/hms-api.service`:

```ini
[Unit]
Description=Hospital Management System API
After=network.target postgresql-16.service
Requires=postgresql-16.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/hms/current/server/src
EnvironmentFile=/opt/hms/current/server/src/.env
ExecStart=/opt/hms/current/server/src/.venv/bin/python run.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Service management commands

```bash
sudo systemctl daemon-reload
sudo systemctl enable hms-api.service
sudo systemctl start hms-api.service
sudo systemctl status hms-api.service
sudo systemctl stop hms-api.service
sudo journalctl -u hms-api.service -f    # Follow logs
```

Check that the service is running correctly:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-02-04-52-image.png)

---

## 14. Desktop client

### On a laptop or hospital computer (inside the 192.168.4.x LAN)

```bash
git clone https://github.com/yosseferrazik/hospital-management-project.git
cd hospital-management-project/desktop/src
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate    # Linux
pip install -r requirements.txt
```

### Configure API endpoint

Create `desktop/src/.env`:

```
API_BASE_URL=http://192.168.4.254:5000/api
```

### Run

```bash
python main.py
```

> **Note:** On Ubuntu you may need `sudo apt install python3-tk`.

Desktop client running:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-18-15-17-image.png)

---

## 15. First login

Default administrator credentials:

| Username | Password                     |
|----------|------------------------------|
| `yossef` | `ChangeMePleaseChange!`      |

**Important:** Change the password on first login via the **Change Password** option in the sidebar.

---

## 16. Desktop client setup (on LAN PCs)

On each hospital computer that will use the application, create `desktop/src/.env` with:

```
API_BASE_URL=http://192.168.4.254:5000/api
```

To make installation easier, an **Inno Setup installer** is available at `desktop/dist/HMS_Client_Setup_v2026.05.19.exe`. This `.exe` already includes the configured `.env` file and creates a desktop shortcut.

---

## 17. Automated backups & full-service recovery

### Backup layers

The backup system uses **three layers** to protect against any data loss scenario:

| Layer        | Backup file              | Created by              | Protects against                        |
|--------------|--------------------------|-------------------------|-----------------------------------------|
| **Physical** | `physical_*.tar.gz`      | `--physical` flag       | Deleted `/var/lib/postgresql/` directory |
| **Logical**  | `hsp_db_*.dump`          | default (`pg_dump -Fc`) | Corrupted/deleted database              |
| **Config**   | `config_*.tar.gz`        | default (auto)          | Lost `.env`, systemd, `postgresql.conf` |

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

### Config files backed up automatically each run

```
server/src/.env
desktop/src/.env
inventory.ini
.deploy_meta
hms-api.service
logrotate.d/hms
/etc/hms.env
postgresql.conf
pg_hba.conf
pg_ident.conf
```

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

> **Passwordless alternative via `.pgpass`:**
>
> ```bash
> echo 'localhost:5432:hsp_db:backup_user:<password>' | sudo tee -a /root/.pgpass
> sudo chmod 600 /root/.pgpass
> ```

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

This stops PostgreSQL, replaces the data directory, fixes permissions, and restarts the service.

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

For PowerBI data source:

```
http://192.168.4.254:5000/api/dashboard/stats
```

Dashboard:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-19-02-35-image.png)

---

## 20. Monitoring

| What                   | Where to run   | Tool                                |
|------------------------|----------------|-------------------------------------|
| Replication lag        | Briar          | `scripts/ops/check_replication.sh`  |
| SSL certificate expiry | Briar and Sion | `scripts/ops/check_cert_expiry.sh`  |
| Disk space             | Briar and Sion | `df -h`                             |
| Audit logs             | App (Admin)    | Audit Logs section in the client    |
| PostgreSQL logs        | Briar and Sion | `journalctl -u postgresql-16 -f`    |
| API logs               | Briar          | `journalctl -u hms-api.service -f`  |

Screenshots:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-40-14-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-40-30-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-40-47-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-40-57-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-41-16-image.png)

---

## 21. Verification checklist

| Test                    | Where          | Command                                                                 |
|-------------------------|----------------|-------------------------------------------------------------------------|
| API works               | Any LAN PC     | `curl http://192.168.4.254:5000/health`                                 |
| Login works             | Any LAN PC     | `curl -X POST http://192.168.4.254:5000/api/auth/login -H "Content-Type: application/json" -d '{"username":"yossef","password":"..."}'` |
| Tables created          | On Briar       | `sudo -u postgres psql -d hsp_db -c "\dt"`                              |
| Replication active      | On Briar       | `sudo -u postgres psql -c "SELECT state FROM pg_stat_replication;"`     |
| Dashboard accessible    | Browser on LAN | `http://192.168.4.254:5000/api/dashboard/view`                          |
| Backup runs             | On Briar       | `sudo python3 scripts/backup_database.py --list`                         |
| Tailscale connectivity  | Either node    | `ping 100.78.155.2` or `ping 100.98.214.53`                             |

Screenshots:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-41-48-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-42-07-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-42-29-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-18-42-51-image.png)

---

## 22. Troubleshooting

| Problem                                    | Where        | Solution                                                             |
|--------------------------------------------|--------------|----------------------------------------------------------------------|
| `pg_hba.conf` wouldn't let me connect      | Briar        | Changed `127.0.0.1/32` to `192.168.4.0/24` for the LAN range        |
| `pg_basebackup` timed out                  | Briar → Sion | Added `sslmode=require` to `primary_conninfo`                        |
| Tailscale wouldn't connect                 | Sion (AWS)   | Was missing UDP port 41641 in the AWS Security Group                 |
| High replication lag                       | Briar        | `wal_keep_size` was 64 MB, raised it to 1024 MB                      |
| psycopg2 wouldn't install                  | Briar        | `sudo apt install libpq-dev` (needed for compilation)                |
| Tkinter error on Linux                     | Hospital PC  | `sudo apt install python3-tk`                                        |
| Serial IDs reset on restore                | Briar        | Switched from plain text `pg_dump` to `pg_dump -Fc` (custom format)  |
| Datacenter firewall blocked API            | Hospital LAN | Coordinated with the network team to open port 5000                  |
| `JWT_SECRET_KEY` not set                   | Briar        | Generate with `openssl rand -hex 32` and add to `.env`               |
| Could not connect to database              | Briar        | Check PostgreSQL is running: `sudo systemctl status postgresql-16`    |
| Permission denied for `.pgpass`            | Briar        | Run `chmod 600 /root/.pgpass`                                        |
| AWS Security Group blocking Tailscale      | Sion (AWS)   | Add UDP port 41641 to the inbound rules                              |
| `standby.signal` not detected on startup   | Sion         | Verify file exists at `/var/lib/postgresql/16/main/standby.signal`   |
| API returns 500 Internal Server Error      | Briar        | Check logs: `journalctl -u hms-api.service -f`                       |
| Disk space full on `/backups/local`        | Briar        | Adjust retention period in cron or increase disk size                |
