# Administrator Manual

## Table of Contents

1. [Users and roles](#users-and-roles)
2. [User management procedures](#user-management-procedures)
3. [Audit logs](#audit-logs)
4. [Backup and recovery](#backup-and-recovery)
5. [Backup verification](#backup-verification)
6. [Monitoring setup](#monitoring-setup)
7. [Maintenance checklists](#maintenance-checklists)
8. [Security best practices](#security-best-practices)

---

## Users and roles

### Role matrix

The system has 5 roles, each with different permissions:

| Role             | Patients | Visits | Surgeries | Admissions | Reports | User Mgmt | Audit Logs |
|------------------|----------|--------|-----------|------------|---------|-----------|------------|
| **ADMIN**        | CRUD     | CRUD   | CRUD      | CRUD       | View    | Full      | Full       |
| **DOCTOR**       | CRUD     | CRUD   | CRUD      | View       | View    | —         | —          |
| **NURSE**        | View/Edit| View   | Assist    | Manage     | View    | —         | —          |
| **RECEPTIONIST** | Create   | Create | —         | —          | —       | —         | —          |
| **STAFF**        | Read-only (name + room) | — | — | — | — | — | — |

**Legend:** CRUD = Create, Read, Update, Delete

---

## User management procedures

### Creating a new user

1. Go to **User Management** in the sidebar.

   ![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-28-34-image.png)

2. Click **Create User** and fill in the following fields:

   | Field        | Description                                   | Required |
   |--------------|-----------------------------------------------|----------|
   | Username     | Unique login name (3–32 characters)           | Yes      |
   | Password     | Minimum 8 characters, must contain letters and numbers | Yes |
   | Staff ID     | Must reference an existing record in the STAFF table | Yes |
   | Role         | Select from: ADMIN, DOCTOR, NURSE, RECEPTIONIST, STAFF | Yes |

   ![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-30-29-image.png)

3. Click **Save**. The new user can log in immediately.

> **Important:** The Staff ID must already exist in the STAFF table. Create the staff record first via **Maintenance** before creating the user account.

### Managing existing users

1. Navigate to **User Management**. A table lists all registered users.
2. Select a user to perform actions:

   | Action           | Description                                           |
   |------------------|-------------------------------------------------------|
   | **Toggle Active** | Disable a user account without deleting it. Disabled users cannot log in. |
   | **Reset Password** | Set a new password for any user. The user must change it on next login. |

   ![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-31-43-image.png)

### User deactivation policy

- Disable, do not delete, user accounts when an employee leaves the hospital. This preserves the audit trail.
- Reactivate accounts if the employee returns, avoiding the need to recreate associations.
- Review inactive accounts quarterly and archive those disabled for more than 6 months.

### Bulk user operations

The system currently supports individual user management. For bulk operations (e.g., importing multiple users), use the database directly:

```sql
-- Example: Insert multiple staff records
INSERT INTO staff (first_name, last_name, dni, staff_type)
VALUES ('Anna', 'Martínez', '12345678C', 'MEDICAL'),
       ('Pere', 'López', '87654321D', 'NURSING');
```

---

## Audit logs

All changes to sensitive tables (patients, visits, prescriptions, admissions, surgeries, exams) are automatically logged with before/after values for complete traceability.

### Viewing audit logs

1. Navigate to **Audit Logs** in the sidebar.
2. Apply filters to narrow down results:

   | Filter       | Description                                  |
   |--------------|----------------------------------------------|
   | **User**     | Filter by the user who performed the action  |
   | **Action**   | INSERT, UPDATE, DELETE                       |
   | **Table**    | The database table affected                  |
   | **Date Range** | Start and end dates for the log period    |

   ![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-33-08-image.png)

### Audit log fields

Each audit log entry contains:

| Field         | Description                                         |
|---------------|-----------------------------------------------------|
| Timestamp     | Date and time of the action                         |
| User          | Username who performed the action                   |
| Action        | INSERT / UPDATE / DELETE                            |
| Table         | Affected database table                             |
| Record ID     | Primary key of the affected record                  |
| Old Values    | Previous values (for UPDATE and DELETE)             |
| New Values    | New values (for INSERT and UPDATE)                  |

### Audit log retention

| Period                  | Storage          | Action                          |
|-------------------------|------------------|---------------------------------|
| 0–2 years               | Database (active)| Available in Audit Logs UI      |
| 2–7 years               | Compressed archive | Exported and stored in `/backups/audit/` |
| 7+ years                | Deleted          | Purged after legal retention    |

### Exporting audit logs

```bash
# Export audit logs to CSV for archival
psql -d hsp_db -c "\COPY (SELECT * FROM audit_log WHERE action_date >= '2024-01-01' AND action_date < '2025-01-01') TO '/backups/audit/audit_2024.csv' CSV HEADER;"
```

---

## Backup and recovery

### Three-layer strategy

| Layer        | Backs up                                                     | Restore when...                                  | RPO        | RTO        |
|--------------|--------------------------------------------------------------|--------------------------------------------------|------------|------------|
| **Physical** | Entire PGDATA (`/var/lib/postgresql/16/main`)                | Server disk fails, `/var/lib/postgresql` deleted | 24 hours   | 30 min     |
| **Logical**  | Full DB schema + data (`pg_dump -Fc`)                        | Database corrupted, accidental data loss         | 15 minutes | 15–60 min  |
| **Config**   | `.env`, systemd, logrotate, `postgresql.conf`, `pg_hba.conf` | `/opt/hms` lost, config corrupted                | 24 hours   | 5 min      |

### Automated schedule (on Briar)

| Time         | Backup type                         | Retention |
|--------------|-------------------------------------|-----------|
| 02:00 daily  | Logical dump + config               | 5 days    |
| 03:00 daily  | Physical PGDATA                     | 5 days    |
| Every 15 min | Frequent logical dump (lightweight) | 24 hours  |

Backups are stored in `/backups/local/`. Config backup includes:

- `postgresql.conf`, `pg_hba.conf`, `pg_ident.conf`
- `server/src/.env`, `desktop/src/.env`
- `hms-api.service` (systemd unit)
- `logrotate.d/hms`
- `/etc/hms.env`
- `inventory.ini`, `.deploy_meta`

### Restore commands

```bash
# List available backups
python scripts/backup_database.py --list

# Full logical restore (from pg_dump -Fc)
python scripts/backup_database.py --restore latest

# Point-in-time recovery
python scripts/backup_database.py --restore latest --before "2026-05-20 14:30"

# Config restore (app + postgresql.conf)
python scripts/backup_database.py --config-restore latest

# Physical PGDATA restore (for /var/lib/postgresql loss)
python scripts/backup_database.py --physical-restore latest

# Full bare-metal (PGDATA → config → logical)
python scripts/backup_database.py --full-restore latest

# Or use the disaster recovery script
sudo bash scripts/ops/restore_service.sh
```

### Single-table restore (via pg_restore)

```bash
pg_restore -d hsp_db --clean -t patients /backups/local/hsp_db_20260519_020001.dump
pg_restore -d hsp_db --clean -t visits /backups/local/hsp_db_20260519_020001.dump
```

---

## Backup verification

### Daily verification steps

1. **Check backup files exist:**

   ```bash
   ls -la /backups/local/
   # Should show files like:
   # hsp_db_20260520_020000.dump
   # config_20260520_020000.tar.gz
   # physical_20260520_030000.tar.gz
   ```

2. **Verify logical dump integrity:**

   ```bash
   pg_restore --list /backups/local/hsp_db_20260520_020000.dump | head -20
   # Should list TOC entries without errors
   ```

3. **Check backup log for errors:**

   ```bash
   tail -50 /tmp/hms_backup_cron.log
   # Look for "SUCCESS" or "ERROR" messages
   ```

4. **Verify config archive contents:**

   ```bash
   tar -tzf /backups/local/config_20260520_020000.tar.gz
   # Should list .env, conf files, etc.
   ```

5. **Test a dry-run restore:**

   ```bash
   python scripts/backup_database.py --restore latest --dry-run
   ```

### Weekly verification

1. **Perform a full restore on a test environment** (Sion standby can be used for this purpose).
2. **Verify data integrity** by running sample queries on the restored database.
3. **Check replication sync:** ensure the standby is caught up with the primary.

### Monthly verification

1. **Test the full bare-metal restore procedure** end-to-end.
2. **Document restore time** (RTO) and compare against SLA targets.
3. **Review backup retention** and purge old archives as needed.

---

## Monitoring setup

### Built-in monitoring tools

| Tool                              | Location           | Purpose                            |
|-----------------------------------|--------------------|------------------------------------|
| `check_replication.sh`            | Briar              | Monitor replication lag and status |
| `check_cert_expiry.sh`            | Briar and Sion     | SSL certificate expiry alerts      |
| `journalctl` (PostgreSQL)         | Briar and Sion     | PostgreSQL error logs              |
| `journalctl` (hms-api)            | Briar              | Flask API access/error logs        |
| Audit Logs UI                     | App (Admin)        | User activity audit trail          |

### Monitoring commands

```bash
# Check replication status
bash scripts/ops/check_replication.sh

# Check SSL certificate expiry
bash scripts/ops/check_cert_expiry.sh

# View real-time API logs
journalctl -u hms-api.service -f --since "5 min ago"

# View PostgreSQL logs
journalctl -u postgresql-16 -f | grep ERROR

# Check disk usage
df -h /backups /var/lib/postgresql /var/log

# Check memory usage
free -h

# Check system load
uptime
```

Screenshots:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-50-40-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-43-11-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-43-29-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-50-56-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-51-16-image.png)

### Alert thresholds

| Metric              | Warning          | Critical         | Action                               |
|---------------------|------------------|------------------|--------------------------------------|
| Replication lag     | > 10 MB          | > 100 MB         | Check network, WAL generation        |
| Disk usage          | > 80%            | > 95%            | Cleanup old backups, increase storage |
| SSL certificate     | < 30 days        | < 7 days         | Renew certificate immediately         |
| API response time   | > 2 seconds      | > 5 seconds      | Check database, restart service      |
| Failed backups      | 1 failure        | 3 consecutive    | Investigate and re-run manually      |
| Database connections| > 150            | > 190            | Check for connection leaks           |

---

## Maintenance checklists

### Daily tasks

- [ ] Verify backup cron jobs ran successfully (`tail -5 /tmp/hms_backup_cron.log`)
- [ ] Check API health endpoint (`curl http://localhost:5000/health`)
- [ ] Review audit logs for suspicious activity
- [ ] Check disk space on both nodes (`df -h`)

### Weekly tasks

- [ ] Verify replication status (`scripts/ops/check_replication.sh`)
- [ ] Rotate and review PostgreSQL logs
- [ ] Check SSL certificate expiry (`scripts/ops/check_cert_expiry.sh`)
- [ ] Test a dry-run restore from the latest backup
- [ ] Review user accounts (new, disabled, suspicious)

### Monthly tasks

- [ ] Perform a full restore test on the standby server
- [ ] Archive old audit logs (export and compress)
- [ ] Update system packages (`sudo apt update && sudo apt upgrade -y`)
- [ ] Review backup retention and purge old archives
- [ ] Check PostgreSQL performance (`pg_stat_statements`, slow query log)
- [ ] Verify firewall rules are still appropriate

### Quarterly tasks

- [ ] Rotate database passwords for all roles
- [ ] Review and update security policies
- [ ] Test full bare-metal recovery procedure
- [ ] Audit user accounts and disable inactive ones
- [ ] Review and update monitoring thresholds
- [ ] Check TLS certificates and renew if needed

### Annual tasks

- [ ] Full disaster recovery drill (simulate Briar failure)
- [ ] Review and update all documentation
- [ ] SSL certificate renewal (if using 1-year certificates)
- [ ] Security audit and penetration testing
- [ ] Review compliance with data protection regulations (GDPR, LOPDGDD)

---

## Security best practices

### Database security

- **Use SSL for all remote connections** — enforced via `hostssl` in `pg_hba.conf`.
- **Use role-based access** — each application role has its own database user with minimal privileges.
- **Double encryption over Tailscale** — Tailscale's WireGuard encryption + PostgreSQL SSL.
- **Regular password rotation** — rotate database passwords quarterly.
- **Restrict PostgreSQL to listen only on necessary interfaces** (`listen_addresses = '*'` is required for the standby, but bind to specific IPs where possible).

### Application security

- **JWT authentication** — all API endpoints (except `/health` and `/api/auth/login`) require a valid JWT token.
- **Password policies:**
  - Minimum 8 characters
  - Must contain letters and numbers
  - Passwords hashed with bcrypt or similar
- **Session management** — tokens expire after 24 hours. Users must re-authenticate after expiry.
- **Input validation** — all API inputs are validated server-side. The client sends data types and constraints for a better UX, but the server always re-validates.

### Infrastructure security

- **Firewall** — UFW on both nodes with strict inbound rules (see Installation Guide).
- **Tailscale VPN** — all inter-node traffic is encrypted. No open ports to the public internet except on Sion (Tailscale WireGuard UDP).
- **SSH access** — key-based only, no password authentication. Restrict to Tailscale IPs where possible.
- **AWS Security Groups** — Sion's security group only allows PostgreSQL from Briar's Tailscale IP and SSH from the admin's Tailscale IP.

### Backup security

- **Backup encryption** — backups stored on Briar's local disk. If rsync to Sion is enabled, transfer is over Tailscale (encrypted).
- **Access control** — backup files are owned by root with `600` permissions.
- **`.pgpass` file** — stored with `chmod 600` to prevent credential leakage.
- **No hardcoded passwords** — all credentials come from environment variables or `.env` files (excluded from version control via `.gitignore`).

### Audit and compliance

- **Full audit trail** — all CRUD operations on sensitive tables are logged with before/after values.
- **Retention policy** — 2 years active in the database, 7 years compressed archive.
- **Regular review** — administrators should review audit logs weekly for unauthorized access attempts.
- **Compliance** — the system is designed to align with Spanish data protection law (LOPDGDD) and GDPR requirements for medical data handling.

### Incident response

| Incident                        | Response                                                         |
|---------------------------------|------------------------------------------------------------------|
| **Failed login attempts**       | Review audit logs. Temporarily disable the account if brute-force is suspected. |
| **Suspicious data modification** | Identify the user via audit logs. Revert changes from backup if needed. |
| **API unavailable**              | Check `journalctl -u hms-api.service`. Restart service. Check database connectivity. |
| **Database corruption**          | Promote Sion to primary if corruption is severe. Restore logical backup to Briar. |
| **Security breach**              | Immediately disable all user accounts. Investigate via audit logs. Restore from pre-breach backup. |
