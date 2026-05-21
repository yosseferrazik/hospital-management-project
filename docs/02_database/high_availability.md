# High Availability and Disaster Recovery

## Hardware proposal

Two nodes: one on-premise at the hospital and one cloud standby, connected through Tailscale.

| Node | Location | Role | OS |
|------|----------|------|-----|
| **Briar** | Hospital de Blanes (server room) | Primary: API + active PostgreSQL | Ubuntu Server 24.04 LTS |
| **Sion** | AWS EC2 (eu-west-3, Paris) | Standby: hot PostgreSQL (read-only) | Ubuntu Server 24.04 LTS |

### Briar (primary)

| Component | Detail |
|-----------|--------|
| CPU | Intel Xeon E-2336 (6 cores, 12 threads) @ 4.8 GHz |
| RAM | 16 GB DDR4 ECC (2 × 8 GB) |
| Disk 1 | 240 GB SSD NVMe — OS + system |
| Disk 2 | 480 GB SSD SATA — PostgreSQL data + WAL |
| Network | 2 × 1 GbE (bonding mode 1 active-passive) |
| Hospital LAN IP | **192.168.4.254** |
| Tailscale IP | 100.78.155.2 |

#### LVM partitions

```
Disk 1 — /dev/sda (240 GB NVMe)
├── /dev/sda1   512 MB   /boot/efi    vfat
├── /dev/sda2   4 GB     [swap]       swap
└── /dev/sda3   235 GB   LVM VG: vg_system
    ├── vg_system/lv_root     80 GB   /
    ├── vg_system/lv_var      40 GB   /var
    ├── vg_system/lv_log      30 GB   /var/log
    └── vg_system/lv_tmp      10 GB   /tmp

Disk 2 — /dev/sdb (480 GB SATA SSD)
└── /dev/sdb1   480 GB   LVM VG: vg_postgres
    ├── vg_postgres/lv_pgdata    350 GB   /var/lib/postgresql/16/main
    └── vg_postgres/lv_pgwal      80 GB   /var/lib/postgresql/16/wal
    └── (25 GB reserve for LVM snapshots)
```

Separating `lv_pgdata` and `lv_pgwal` on different disks and VGs improves write performance and makes LVM snapshot backups easier. Separating `lv_log` prevents logs from filling up the root partition.

### Sion (standby)

| Component | Detail |
|-----------|--------|
| CPU | 2 vCPU (AWS t3.medium) |
| RAM | 4 GB |
| Disk | 80 GB gp3 SSD (elastic) |
| Network | 1 GbE virtual (AWS ENI) |
| Tailscale IP | 100.98.214.53 |

#### Partitions

```
/dev/xvda1   1 MB   [BIOS boot]
/dev/xvda2   79 GB  LVM VG: vg_main
    ├── vg_main/lv_root     20 GB   /
    ├── vg_main/lv_swap      2 GB   swap
    ├── vg_main/lv_pgdata   40 GB   /var/lib/postgresql/16/main
    └── vg_main/lv_pgwal    10 GB   /var/lib/postgresql/16/wal
    (7 GB reserve)
```

## Network and connectivity

### Topology

```
┌──────────────────────────────────────────────────┐
│           Hospital LAN (192.168.4.0/24)           │
│                                                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐  │
│  │  Users   │   │  Users   │   │    Admin      │  │
│  │ (doctors)│   │ (recept) │   │ (IT staff)    │  │
│  └────┬─────┘   └────┬─────┘   └──────┬───────┘  │
│       │              │               │           │
└───────┼──────────────┼───────────────┼───────────┘
        │              │               │
        │     192.168.4.254            │
        │              │         (Tailscale VPN)
   ┌────┴──────────────┴───────────────┴────┐
   │               Briar                     │
   │   API + PostgreSQL PRIMARY              │
   └────────────┬────────────────────────────┘
                │ Tailscale (100.78.155.2 ↔ 100.98.214.53)
                │ (WAL streaming + rsync backups)
   ┌────────────┴────────────────────────────┐
   │               Sion (AWS)                 │
   │   PostgreSQL STANDBY (read-only)         │
   └──────────────────────────────────────────┘
```

The admin connects to both servers through **Tailscale** (access from anywhere, end-to-end encryption). Hospital users connect to **Briar** directly at **192.168.4.254** within the LAN.

Tailscale acts as a mesh VPN: Briar and Sion see each other via 100.x.x.x IPs, and the admin can access both from any device with Tailscale installed. All node-to-node traffic is automatically encrypted.

### Install Tailscale (on both nodes and your laptop)

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

### Firewall — Briar

```bash
# Open ports
ufw allow 22/tcp                   # SSH (admin via Tailscale)
ufw allow 5000/tcp                 # Flask API (LAN users)
ufw allow from 192.168.4.0/24 to any port 5000  # API LAN only
ufw allow from 100.98.214.53 to any port 5432   # replication from Sion over Tailscale
ufw allow in on tailscale0                    # all Tailscale traffic
ufw default deny incoming
ufw enable
```

### Firewall — Sion

```bash
ufw allow 22/tcp                   # SSH (admin via Tailscale)
ufw allow from 100.78.155.2 to any port 5432  # replication from Briar
ufw allow in on tailscale0                    # all Tailscale traffic
ufw default deny incoming
ufw enable
```

## PostgreSQL — configuration

### Briar (primary) — `postgresql.conf`

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

### Briar — `pg_hba.conf`

```
# Local admin (no SSL)
local   all             postgres                                peer

# Replication over Tailscale (automatic encryption, plus SSL on top)
hostssl replication     replicator      100.98.214.53/32        scram-sha-256

# Application from the hospital LAN
hostssl hsp_db          app_admin       192.168.4.0/24          scram-sha-256
hostssl hsp_db          app_doctor      192.168.4.0/24          scram-sha-256
hostssl hsp_db          app_nurse       192.168.4.0/24          scram-sha-256
hostssl hsp_db          app_receptionist 192.168.4.0/24         scram-sha-256
hostssl hsp_db          app_staff       192.168.4.0/24          scram-sha-256

# Application from Briar itself
hostssl hsp_db          app_admin       127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_doctor      127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_nurse       127.0.0.1/32            scram-sha-256
hostssl hsp_db          app_receptionist 127.0.0.1/32           scram-sha-256
hostssl hsp_db          app_staff       127.0.0.1/32            scram-sha-256

# Backup user (from Briar itself — no SSL required for local backup connections)
host    hsp_db          backup_user     127.0.0.1/32            scram-sha-256
host    hsp_db          backup_user     ::1/128                 scram-sha-256
```

All remote connections use **SSL** (`hostssl`). Connections over Tailscale have both Tailscale's own encryption **plus** PostgreSQL SSL (double layer).

### Sion (standby) — `postgresql.conf`

```ini
listen_addresses = '*'
port = 5432
max_connections = 50
shared_buffers = 1GB
wal_level = replica
hot_standby = on
primary_conninfo = 'host=100.78.155.2 port=5432 user=replicator password=**** sslmode=require'
primary_slot_name = 'standby_sion'
ssl = on
ssl_cert_file = '/etc/ssl/certs/postgresql.crt'
ssl_key_file = '/etc/ssl/private/postgresql.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'
```

### Sion — `standby.signal`

```bash
# On Sion
sudo touch /var/lib/postgresql/16/main/standby.signal
```

## TLS/SSL — certificate generation

### On Briar

```bash
mkdir -p ~/ssl && cd ~/ssl

# Own CA
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/C=ES/ST=Girona/L=Blanes/O=Hospital de Blanes/CN=CA Hospital"

# PostgreSQL certificate (with the name clients will use)
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

### On Sion (same but with CN=100.98.214.53)

Repeat the steps on Sion using `CN=100.98.214.53` (Sion's Tailscale IP) in the certificate.

## Replication — step by step

### 1. On Briar — create replication user

```bash
sudo -u postgres psql -c "CREATE ROLE replicator WITH LOGIN REPLICATION PASSWORD 'change_password';"
```

### 2. On Briar — create replication slot

```bash
sudo -u postgres psql -c "SELECT pg_create_physical_replication_slot('standby_sion');"
```

### 3. On Sion — perform base backup

```bash
# Stop PostgreSQL if it was initialised
sudo systemctl stop postgresql-16

# Delete existing data (if any)
sudo rm -rf /var/lib/postgresql/16/main/*

# Base backup from Briar over Tailscale
sudo -u postgres pg_basebackup -h 100.78.155.2 -D /var/lib/postgresql/16/main \
  -U replicator -P -v --slot=standby_sion --wal-method=stream

# Mark as standby
sudo touch /var/lib/postgresql/16/main/standby.signal
```

### 4. On Sion — start

```bash
sudo systemctl start postgresql-16
```

### 5. On Briar — verify replication

```bash
sudo -u postgres psql -c "SELECT slot_name, slot_type, active, restart_lsn FROM pg_replication_slots;"
sudo -u postgres psql -c "SELECT application_name, state, sync_state FROM pg_stat_replication;"
```

Or using the script:

```bash
./scripts/ops/check_replication.sh
```

## Backup

### Main script (`scripts/backup_database.py`)

Runs on **Briar** (it has the primary database):

```bash
# Manual backup (will prompt for password)
python scripts/backup_database.py

# Manual backup with password (no prompt)
HMS_DB_PASSWORD='<password>' python scripts/backup_database.py

# Daily full backup (with verify + rsync)
0 2 * * * HMS_DB_PASSWORD='<password>' cd /opt/hms/current && python scripts/backup_database.py >> /tmp/hms_backup_cron.log 2>&1

# Frequent backup every 15 min (minute-level RPO, skips verify + rsync)
*/15 * * * * HMS_DB_PASSWORD='<password>' cd /opt/hms/current && python scripts/backup_database.py --frequent >> /tmp/hms_backup_frequent.log 2>&1
```

> To avoid putting the password in the command line, create a `.pgpass` file:
> ```bash
> echo 'localhost:5432:hsp_db:backup_user:<password>' | sudo tee -a /root/.pgpass
> sudo chmod 600 /root/.pgpass
> ```

What the backup does:

1. Connects to `hsp_db`
2. `pg_dump -Fc` → `/backups/local/hsp_db_YYYYMMDD_HHMMSS.dump`
3. Verifies with `pg_restore -l`
4. Saves JSON metadata (date, size, checksum, result)
5. Cleans backups older than 5 days
6. Optionally rsyncs a copy to Sion (disabled by default — see below)

> **rsync to Sion is disabled by default.** To enable it you need:
> 1. SSH key access from Briar (root) to Sion
> 2. `HMS_STANDBY_HOST` and optionally `HMS_STANDBY_USER` set
>
> ### Setup
>
> **On Sion** — create the backup directory and fix ownership:
> ```bash
> sudo mkdir -p /backups/local
> sudo chown ubuntu:ubuntu /backups/local
> ```
>
> **On Briar** — generate SSH key and copy it to Sion:
> ```bash
> sudo ssh-keygen -t ed25519 -f /root/.ssh/id_ed25519 -N ""
> sudo cat /root/.ssh/id_ed25519.pub
> # Copy the output, then from your admin machine:
> # ssh -i <your.pem> ubuntu@100.98.214.53 "echo '<paste_key>' | sudo tee -a /home/ubuntu/.ssh/authorized_keys"
> ```
>
> **Run with rsync enabled** (STANDBY_USER defaults to `ubuntu` now):
> ```bash
> sudo HMS_STANDBY_HOST=100.98.214.53 python3 scripts/backup_database.py
> ```
>
> **Persist in crontab** (replace `<password>`):
> ```bash
> sudo crontab -e
> # Add:
> 0 2 * * * HMS_DB_PASSWORD='<password>' HMS_STANDBY_HOST=100.98.214.53 cd /opt/hms/current && python3 scripts/backup_database.py >> /tmp/hms_backup_cron.log 2>&1
> ```
>
> **Verify:**
> ```bash
> echo "STANDBY_HOST=$HMS_STANDBY_HOST"        # empty = disabled
> ls -la /backups/local/                       # on Sion — should show .dump files
> ```

### Restore (on Briar)

The same script can list backups and restore the database.

```bash
# List available backups
python scripts/backup_database.py --list

# List backups before a specific date/time
python scripts/backup_database.py --list --before "2026-05-20 14:30"

# List backups as JSON (for scripting)
python scripts/backup_database.py --list --json

# Restore from the most recent backup
python scripts/backup_database.py --restore latest

# Restore from a specific backup file
python scripts/backup_database.py --restore /backups/local/hsp_db_20260520_020000.dump

# Restore the latest backup before a point in time
python scripts/backup_database.py --restore latest --before "2026-05-20 14:30"

# Dry-run: see what would happen without touching the database
python scripts/backup_database.py --restore latest --dry-run
```

The script will:
1. Verify the backup integrity with `pg_restore -l`
2. **Drop** the current `hsp_db` database
3. Recreate it empty
4. Run `pg_restore --clean --if-exists`

Because this is destructive, the script asks for confirmation (`yes`) before proceeding.

> For a single-table restore, use `pg_restore` directly:
> ```bash
> sudo -u postgres pg_restore -d hsp_db --clean -t patients /backups/local/hsp_db_20260519_020001.dump
> ```

## Failover

### If Briar goes down — promote Sion to primary

```bash
# On Sion
sudo -u postgres pg_ctl promote -D /var/lib/postgresql/16/main

# In the API .env file (need to reconfigure where the API runs)
# Change DATABASE_URL to Sion's Tailscale IP
# DATABASE_URL=postgresql://postgres:xxx@100.98.214.53:5432/hsp_db
```

### Return to normal (rebuild standby)

```bash
# On Sion
sudo systemctl stop postgresql-16
sudo rm -rf /var/lib/postgresql/16/main/*
sudo -u postgres pg_basebackup -h 100.78.155.2 -D /var/lib/postgresql/16/main \
  -U replicator -P -v --slot=standby_sion --wal-method=stream
sudo touch /var/lib/postgresql/16/main/standby.signal
sudo systemctl start postgresql-16
```

## Monitoring

| What | Where to run | Tool |
|------|-------------|------|
| Replication lag | Briar | `scripts/ops/check_replication.sh` |
| SSL certificate | Briar and Sion | `scripts/ops/check_cert_expiry.sh` |
| Disk space | Briar and Sion | `df -h` |
| Audit logs | App (Admin) | Audit Logs section in the client |
| PostgreSQL logs | Briar and Sion | `journalctl -u postgresql-16` |
| API logs | Briar | `journalctl -u hms-api` |

## Errors we had

- **Plain text pg_dump**: sequences would restart from 0 on restore. We switched to `pg_dump -Fc` (custom format), which preserves sequences.
- **High replication lag**: `wal_keep_size` was 64 MB, not enough for the 100k visits. We raised it to 1024 MB.
- **pg_basebackup failed**: we needed `sslmode=require` in `primary_conninfo` because Sion connects to Briar over Tailscale and we want SSL as an extra layer.
- **Tailscale wouldn't route at first**: we forgot to open UDP port 41641 in Sion's AWS Security Group.
- **Datacenter firewall**: we had to coordinate with the hospital's network team to open port 5000 on the LAN.
