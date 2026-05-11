# Replication and High-Availability Runbook

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Complete     |
| Version        | 1.0          |
| Last Updated   | 2026-05-11   |

## Purpose

This runbook is the canonical operational reference for PostgreSQL streaming replication, failover and failback procedures, monitoring and verification for the Hospital Management System. It contains the exact commands and scripts operators should use when configuring replication, promoting a standby, validating replication health, and performing failover drills.

Keep this file authoritative; other infrastructure documents should link here rather than duplicating step-by-step commands.

## Prerequisites

- PostgreSQL installed (same major version) on primary and standby
- Network connectivity: TCP 5432 must be reachable from primary ↔ standby
- Time sync (NTP/Chrony) configured on both nodes
- A replication user created on primary with REPLICATION privilege

## Configure Primary Node

1. Create replication user (on primary):

```sql
sudo -u postgres psql
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE hospital_management TO replicator;
\q
```

2. Edit `/etc/postgresql/14/main/postgresql.conf` and enable replication settings:

```ini
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1024  # 1 GB
hot_standby = on
```

3. Edit `/etc/postgresql/14/main/pg_hba.conf` to allow replication from the standby IP(s):

```conf
# Allow replication from replica node (AWS IP)
```

4. Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

## Configure Replica Node (Base Backup)

1. Install PostgreSQL (same version as primary):

```bash
sudo apt update
sudo apt install postgresql postgresql-client -y
```

2. Stop PostgreSQL on the standby while preparing base backup:

```bash
sudo systemctl stop postgresql
```

3. Clear or prepare data directory (be careful):

```bash
sudo rm -rf /var/lib/postgresql/14/main/*
```

4. Perform base backup from primary:

```bash
sudo -u postgres pg_basebackup -h <PRIMARY_IP> -D /var/lib/postgresql/14/main \
  -U replicator -P -v -R
```

5. Ensure `primary_conninfo` is set in `/etc/postgresql/14/main/postgresql.conf` (example):

```ini
hot_standby = on
primary_conninfo = 'host=<PRIMARY_IP> port=5432 user=replicator password=strong_password'
```

6. Start PostgreSQL on the standby:

```bash
sudo systemctl start postgresql
```

## Verify Replication

On primary:

```sql
SELECT client_addr, state, sync_state, application_name 
FROM pg_stat_replication;
```

On standby:

```sql
SELECT pg_is_in_recovery();  -- should return 't'
SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;
```

Expected: streaming state on primary and small replication lag on standby.

## Promote Standby (Failover)

If the primary has failed and you must promote the standby to primary:

```bash
# On the standby node
sudo -u postgres pg_ctl promote -D /var/lib/postgresql/14/main/

# Verify promotion
sudo -u postgres psql -c "SELECT pg_is_in_recovery();"  # should return 'f'
```

After promotion, update application configuration (DATABASE_URL) to point to the new primary and restart API services.

## Failback (Rebuild Original Primary)

After repairing the original primary, re-create it as a standby from the new primary:

```bash
# On original primary (now to be standby)
sudo systemctl stop postgresql
sudo rm -rf /var/lib/postgresql/14/main/*
sudo -u postgres pg_basebackup -h <NEW_PRIMARY_IP> -D /var/lib/postgresql/14/main \
  -U replicator -P -v -R
sudo systemctl start postgresql
```

## Monitoring Script (check_replication.sh)

The canonical monitoring script is included in the repository at `scripts/ops/check_replication.sh`.

Make it executable and add to cron for periodic checks (every 5 minutes). For example, from the repository root:

```cron
*/5 * * * * /bin/bash $(pwd)/scripts/ops/check_replication.sh >> /var/log/replication_check.log 2>&1
```

## Testing and Validation

Monthly restore drills (validate backups):

```bash
# Select latest backup
BACKUP_FILE=$(ls -t /backups/local/backup_*.sql.gz | head -1)

# Create validation database
sudo -u postgres createdb hospital_management_test

# Restore
gunzip -c $BACKUP_FILE | sudo -u postgres psql hospital_management_test

# Run validation queries (row counts)
sudo -u postgres psql -d hospital_management_test -c "
  SELECT 'patients' as table, COUNT(*) FROM patients
  UNION ALL SELECT 'staff', COUNT(*) FROM staff
  UNION ALL SELECT 'surgeries', COUNT(*) FROM surgeries
"

# Clean up
sudo -u postgres dropdb hospital_management_test
```

Quarterly failover rehearsals:

1. Schedule downtime and notify users
2. Promote standby to primary
3. Update application configuration to point to new primary IP
4. Verify key workflows (login, patient creation, scheduling)
5. Document results and failback to original primary

## Troubleshooting

- `pg_stat_replication` empty: check network connectivity and firewall (telnet <AWS_IP> 5432).
- Authentication failed: verify replication user/password and pg_hba.conf entries.
- Replication lag growing: check WAL retention (`wal_keep_size`) and disk usage.

## Change Log

| Date | Version | Change Summary | Owner |
|:---|:---:|:---|:---|
| 2026-05-11 | 1.0 | Initial replication and HA runbook | Project Team |

## Quick Start: Deploy Replication (Step-by-step)

These steps enable an operator at Hospital Sa Palomera to create a primary and a standby node (AWS EC2) and confirm replication. Commands assume Ubuntu 22.04 on both nodes. Replace placeholders (e.g., <PRIMARY_IP>, <AWS_REPLICA_IP>, 'strong_password') with real values before running.

1) Install required packages on both primary and standby

```bash
sudo apt update
sudo apt install -y postgresql-14 postgresql-client-14 wget curl
```

2) Configure Primary (on hospital datacenter primary node)

a) Create replication user

```bash
sudo -u postgres psql -c "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'strong_password';"
sudo -u postgres psql -c "GRANT CONNECT ON DATABASE hospital_management TO replicator;"
```

b) Edit `/etc/postgresql/14/main/postgresql.conf` (use nano or sed) and add or change:

```ini
wal_level = replica
max_wal_senders = 3
wal_keep_size = 1024
hot_standby = on
listen_addresses = '*'
```

c) Edit `/etc/postgresql/14/main/pg_hba.conf` and add a replication entry for the standby IP:

```conf
host    replication    replicator    <AWS_REPLICA_IP>/32    md5
```

d) Restart PostgreSQL

```bash
sudo systemctl restart postgresql
```

3) Prepare Standby (on AWS EC2 replica)

a) Stop PostgreSQL

```bash
sudo systemctl stop postgresql
```

b) Clear existing data directory (BE CAREFUL: destructive)

```bash
sudo rm -rf /var/lib/postgresql/14/main/*
```

c) Run `pg_basebackup` from the standby to the primary

```bash
sudo -u postgres pg_basebackup -h <PRIMARY_IP> -D /var/lib/postgresql/14/main -U replicator -P -v -R
```

d) Ensure `primary_conninfo` is set (the pg_basebackup -R will typically create `standby.signal` and set `primary_conninfo` in `postgresql.auto.conf`; verify it contains the correct host/user/password).

e) Start PostgreSQL on standby

```bash
sudo systemctl start postgresql
```

4) Verify replication

On primary:

```sql
sudo -u postgres psql -c "SELECT client_addr, state, sync_state, application_name FROM pg_stat_replication;"
```

On standby:

```sql
sudo -u postgres psql -c "SELECT pg_is_in_recovery();"
sudo -u postgres psql -c "SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;"
```

Expected results: primary shows a `walreceiver` connection from the standby with `streaming` state; standby returns `t` from `pg_is_in_recovery()` and low lag.


5) Add monitoring (systemd timer recommended)

We recommend running the replication check via cron or a systemd timer on the primary. Using the deployed path:

```cron
*/5 * * * * /bin/bash /opt/hms/scripts/check_replication.sh >> /var/log/replication_check.log 2>&1
```

6) Promote standby (manual failover test)

On standby (when primary is intentionally taken offline for testing):

```bash
sudo -u postgres pg_ctl promote -D /var/lib/postgresql/14/main/
sudo -u postgres psql -c "SELECT pg_is_in_recovery();"  # should return 'f'
```

After promotion, update the Flask API `DATABASE_URL` on application hosts to point to the new primary IP and restart the API: `sudo systemctl restart hms-api`.

7) Failback procedure (rebuild original primary as standby)

Follow the Failback section above: re-run pg_basebackup from the new primary to the repaired old-primary and start postgres.

8) Validation checklist

- Confirm replication stream present: `SELECT * FROM pg_stat_replication;`
- Confirm WAL replay lag is within acceptable limits: `SELECT now() - pg_last_xact_replay_timestamp();`
- Confirm application can connect and perform writes to new primary after promotion
- Confirm backups run successfully after failover (run backup script)
