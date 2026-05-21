# Administrator Manual

## Users and roles

The system has 5 roles:

| Role | Permissions |
|------|-------------|
| **ADMIN** | Full access to everything, including user management and audit logs |
| **DOCTOR** | CRUD on patients, visits, treatments, surgeries. View reports. |
| **NURSE** | View/edit patients on their floor, manage admissions, assist in surgeries |
| **RECEPTIONIST** | Register patients, schedule appointments |
| **STAFF** | Read-only: patient name + room only |

### Creating users

1. Go to **User Management** in the sidebar
2. Click **Create User** and fill in:
   - Username
   - Password
   - Staff ID (must already exist in the STAFF table)
   - Role
3. The new user can log in immediately

### Managing existing users

- **Toggle Active** — disable a user without deleting them
- **Reset Password** — set a new password for any user

## Audit logs

All changes to sensitive tables (patients, visits, prescriptions, admissions, surgeries, exams) are automatically logged. Administrators can view, filter, and purge these logs from the **Audit Logs** section.

## Backup and recovery

Backups run automatically at 02:00 daily via a cron job (`scripts/backup_database.py`):

- Custom-format `pg_dump` saved locally to `/backups/local/`
- 5 most recent backups retained
- Rsync to standby (Sion) is **disabled by default** — enable via `HMS_STANDBY_HOST`
- Backup integrity verified automatically

### Manual restore

```bash
# Full restore
pg_restore -d hsp_db --clean /path/to/backup.dump

# Single table (e.g., accidentally deleted patients)
pg_restore -d hsp_db --clean -t patients /path/to/backup.dump
```

## Monitoring

Check these regularly:

| What | How |
|------|-----|
| Replication status | `scripts/ops/check_replication.sh` |
| SSL cert expiry | `scripts/ops/check_cert_expiry.sh` |
| API health | `curl http://localhost:5000/health` |
| Disk space | `df -h` on both nodes |

## Maintenance tasks

- Rotate database passwords periodically
- Check that backups are completing successfully
- Review audit logs for suspicious activity
- Archive old audit logs (retention: 2 years active, 7 years compressed)
