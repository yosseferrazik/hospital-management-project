# Administrator Manual

## Users and roles

The system has 5 roles, each with different permissions:

| Role             | Permissions                                                               |
| ---------------- | ------------------------------------------------------------------------- |
| **ADMIN**        | Full access to everything, including user management and audit logs       |
| **DOCTOR**       | CRUD on patients, visits, treatments, surgeries. View reports.            |
| **NURSE**        | View/edit patients on their floor, manage admissions, assist in surgeries |
| **RECEPTIONIST** | Register patients, schedule appointments                                  |
| **STAFF**        | Read-only: patient name + room only                                       |

### Creating users

1. Go to **User Management** in the sidebar
   
   ![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-28-34-image.png)

2. Click **Create User** and fill in:
   - Username
   - Password
   - Staff ID (must already exist in the STAFF table)
   - Role
     
   ![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-30-29-image.png)

3. The new user can log in immediately

### Managing existing users

- **Toggle Active** — disable a user without deleting them
- **Reset Password** — set a new password for any user

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-31-43-image.png)

## Audit logs

All changes to sensitive tables (patients, visits, prescriptions, admissions, surgeries, exams) are automatically logged. Administrators can view, filter, and purge these logs from the **Audit Logs** section. The audit trail includes before/after values for complete traceability.

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-33-08-image.png)

## Backup and recovery

### Three-layer strategy

| Layer        | Backs up                                                     | Restore when...                                  |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------ |
| **Physical** | Entire PGDATA (`/var/lib/postgresql/`)                       | Server disk fails, `/var/lib/postgresql` deleted |
| **Logical**  | Full DB schema + data (`pg_dump -Fc`)                        | Database corrupted, accidental data loss         |
| **Config**   | `.env`, systemd, logrotate, `postgresql.conf`, `pg_hba.conf` | `/opt/hms` lost, postgresql.conf corrupted       |

### Automated schedule (on Briar)

| Time         | Backup type                         | Retention |
| ------------ | ----------------------------------- | --------- |
| 02:00 daily  | Logical dump + config               | 5 days    |
| 03:00 daily  | Physical PGDATA                     | 5 days    |
| Every 15 min | Frequent logical dump (lightweight) | 24 hours  |

Backups stored in `/backups/local/`. Config backup includes `postgresql.conf`, `pg_hba.conf`, `.env`, systemd unit, logrotate config, and deploy metadata.

### Restore commands (admin)

```bash
# List available backups
python scripts/backup_database.py --list

# Full logical restore (from pg_dump)
python scripts/backup_database.py --restore latest

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
```

## Monitoring

Check these regularly to ensure the system is running smoothly:

| What               | How                                 |
| ------------------ | ----------------------------------- |
| Replication status | `scripts/ops/check_replication.sh`  |
| SSL cert expiry    | `scripts/ops/check_cert_expiry.sh`  |
| API health         | `curl http://localhost:5000/health` |
| Disk space         | `df -h` on both nodes               |

Screenshots of monitoring tools:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-50-40-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-43-11-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-43-29-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-50-56-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/administrator_manual/2026-05-22-14-51-16-image.png)

## Maintenance tasks

- Rotate database passwords periodically
- Check that backups are completing successfully
- Review audit logs for suspicious activity
- Archive old audit logs (retention: 2 years active, 7 years compressed)
- Monitor disk usage on both nodes to prevent storage issues
