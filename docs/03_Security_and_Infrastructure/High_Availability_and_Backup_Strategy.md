# High Availability and Backup Strategy

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 3.1          |
| Last Updated   | 2026-05-07   |

## Purpose

This document defines the availability and resilience planning for the Hospital Management System. It covers backup strategy, recovery objectives, standby topology, and validation procedures. This document is self-contained and does not depend on external references.

**Scope:**

- Availability objectives and recovery targets (RTO/RPO)
- Backup and recovery strategy
- Standby node and replication design
- Storage layout for resilience
- Node responsibilities during failures
- Testing and validation procedures
- Monitoring and alerting requirements

---

## Availability Objectives

- Reduce single points of failure in the application and database stack.
- Preserve clinical data integrity during operational incidents.
- Enable recovery procedures that are realistic for the current project scope.
- Keep the design compatible with a simulated lab deployment.

---

## Target Topology

| Node           | Location               | Role                     | Main Components                                           |
|:-------------- |:---------------------- |:------------------------ |:--------------------------------------------------------- |
| Primary node   | Hospital datacenter    | Active database + API    | PostgreSQL primary, Flask API, backup coordinator        |
| Secondary node | AWS Cloud (EC2)        | Standby database         | PostgreSQL standby (read-only), failover target           |
| Backup storage | Local (primary disk)   | Local backup retention   | `/backups/local` - last 5 backup copies                   |


---

## VMware Simulation Topology

The high-availability design is validated using the following nodes:

| VM / Instance             | HA Role      | Main Responsibilities                                                                                       |
|:------------------------- |:------------ |:----------------------------------------------------------------------------------------------------------- |
| `vm-hms-primary`          | Active node  | Hosts PostgreSQL primary, Flask API, local backup execution, rsync to standby coordinator                       |
| AWS EC2 (replica)         | Standby node | Hosts PostgreSQL standby, supports failover, restore validation                                             |
| `vm-admin-client`         | Admin node   | Monitors replication, validates backups, supports manual failover checks                                    |

---

## Strategy Overview

| Area                   | Approach                                                       |
|:---------------------- |:-------------------------------------------------------------- |
| Database resilience    | PostgreSQL streaming replication (active → standby)            |
| Application resilience | Manual restart or failover; API on primary node only           |
| Traffic distribution   | Clients point directly to primary node IP                      |
| Local backups          | Daily, retain last 5 copies on `/backups/local`                |
| Off-site replication   | Daily rsync to standby node (Sion)                            |
| Recovery operations    | Manual, documented promotion and restore procedures            |

---

## Resource and Storage Baseline

### Primary Node (Hospital Datacenter)

| Component | Specification | Justification |
|:----------|:--------------|:---------------|
| CPU | 4 vCores | Flask API + PostgreSQL primary |
| RAM | 8 GB | PostgreSQL caching and API workers |
| Storage (OS) | 40 GB SSD | Ubuntu Server and application files |
| Storage (Data) | 100 GB SSD | PostgreSQL data directory |
| Storage (Backups) | 50 GB SSD | Local backup retention (5 copies) |

### Replica Node (AWS EC2)

| Component | Specification | Justification |
|:----------|:--------------|:---------------|
| Instance Type | t3.medium (2 vCPU, 4 GB RAM) | Standby PostgreSQL |
| Storage | 80 GB gp3 | OS + PostgreSQL data directory |
| Region | Closest to hospital | Minimizes replication lag |

### Storage Separation Requirements

| Storage Area              | Location                  | HA Relevance                                                                   |
|:------------------------- |:------------------------- |:------------------------------------------------------------------------------ |
| Root filesystem           | `/` (40 GB)               | Hosts OS and base runtime only                                                 |
| PostgreSQL data partition | `/var/lib/postgresql`     | Isolates live database files; critical for replication and recovery            |
| Log partition             | `/var/log` (5 GB)         | Preserves diagnostics during incidents                                         |
| Backup partition          | `/backups/local` (50 GB)  | Supports local retention (5 copies) without mixing with active database files |

---

## Backup Strategy

Summary:

- Daily logical backups are performed and retained locally (default: last 5 copies).
- A daily off-site copy (rsynced to the standby node (Sion)) is retained for longer.

For operational scripts, cron schedules, encryption guidance and full restore procedures, see the canonical runbook: docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md. This document focuses on HA topology, failover and recovery scope; detailed backup tooling is handled in the runbook to avoid duplication.

---

## Recovery Scope

The operational model covers:

- Full database restoration from local backup or standby node
- Targeted restoration of critical tables (patients and staff)
- Standby promotion in case of primary database failure
- Validation steps after recovery

Refer to docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md for exact restore scripts and safe execution steps.

---

## Replication and High-Availability

Summary:

- Running and maintaining replication, promotion, monitoring and failback is operational work with precise commands and scripts.
- The complete, authoritative procedures (including check_replication.sh, cron examples, pg_basebackup commands, promotion and failback steps, and verification queries) live in the canonical runbook:

docs/04_Operations_and_Manuals/Replication_and_HA_Runbook.md

Refer to that runbook for exact steps and scripts; this document focuses on the architecture, RTO/RPO and testing cadence.

---

## Node Responsibilities During Failure Scenarios

### Primary Node Failure

- Client traffic to the main application path is interrupted.
- The standby database node (AWS EC2) becomes the recovery candidate.
- Manual promotion of the standby node is required.
- Application service must be redirected to the new primary IP.

### Database Corruption on Primary

- New writes should be stopped immediately.
- Restore validation performed from latest local backup or standby node.
- Standby node may be promoted if corruption has not replicated.

### Application Service Failure Only

- Database remains healthy.
- Service can be restarted on primary node: `sudo systemctl restart hms-api`.

### Network Partition (Split Brain)

- Do NOT promote both nodes.
- Check which side has application traffic.
- Keep primary as-is if reachable; promote standby only if primary unreachable.
- After network recovery, rebuild isolated standby from primary WAL.

---

## Recovery Time and Recovery Point Objectives

| Scenario                                        | RTO       | RPO        | Procedure                                       |
|:----------------------------------------------- |:---------:|:----------:|:----------------------------------------------- |
| **Critical Data** (Patients, Surgeries, Visits) | 1 hour    | 15 minutes | Standby promotion or restore from latest backup |
| **Core API** (Authentication, Operations)       | 2-4 hours | 1 hour     | Application restart + database validation       |
| **Full System Rebuild**                         | 4-8 hours | 1 hour     | Fresh deployment + restore from standby node       |
| **Non-Critical** (Reports, Analytics)           | 24 hours  | 24 hours   | Scheduled recovery window                       |

These targets are validated quarterly through drills.

---

## Testing and Validation

### Monthly Restore Drills

```bash
# Select latest backup
BACKUP_FILE=$(ls -t /backups/local/backup_*.sql.gz | head -1)

# Create validation database
sudo -u postgres createdb hospital_management_test

# Restore
gunzip -c $BACKUP_FILE | sudo -u postgres psql hospital_management_test

# Validate row counts
sudo -u postgres psql -d hospital_management_test -c "
  SELECT 'patients' as table, COUNT(*) FROM patients
  UNION ALL SELECT 'staff', COUNT(*) FROM staff
  UNION ALL SELECT 'surgeries', COUNT(*) FROM surgeries
"

# Clean up
sudo -u postgres dropdb hospital_management_test
```

### Quarterly Failover Rehearsals

1. Schedule downtime (inform users)
2. Promote AWS EC2 standby to primary
3. Update application configuration to new primary IP
4. Verify key workflows: login, patient creation, surgery scheduling
5. Document any issues
6. Failback to original primary (re-create standby)

### Semi-Annual Disaster Recovery Drills

1. Select reference date (1-2 weeks ago)
2. Provision fresh EC2 instance for testing
3. Restore database from standby node backup of reference date
4. Deploy fresh application instance
5. Verify full functionality
6. Calculate achieved RTO and RPO

---

## Monitoring and Alerting

### Key Metrics

| Metric                | Command / Source                     | Alert Threshold |
|:--------------------- |:------------------------------------ |:---------------:|
| Replication lag       | `pg_stat_replication`                | > 100 MB        |
| Standby recovery      | `pg_last_xact_replay_timestamp()`    | > 5 minutes lag |
| Disk space (local)    | `df -h /backups/local`               | < 20% free      |
| Disk space (data)     | `df -h /var/lib/postgresql`          | < 15% free      |
| Backup success        | Check `/var/log/hms-backup.log`      | Failure         |
| Rsync success         | Check `/var/log/hms-rsync.log`       | Failure         |

### Replication Monitoring Script

`scripts/ops/check_replication.sh` (canonical location):

```bash
#!/bin/bash
# See scripts/ops/check_replication.sh in the repository
psql -U postgres -d hospital_management -t -c \
  "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))::int \
   FROM pg_stat_replication;" 2>/dev/null || echo "No replication active"
```

Add to cron (every 5 minutes):

```cron
*/5 * * * * /bin/bash $(pwd)/scripts/ops/check_replication.sh >> /var/log/replication_check.log 2>&1
```

---

## Assumptions and Limitations

- The system is currently in design and validation scope, not production scope.
- Manual failover is acceptable for the current phase; future versions may implement automated failover.
- Infrastructure uses on-premise primary node + AWS EC2 replica.
- Backups use local retention (5 copies) + rsync to standby node (Sion).
- Split-brain prevention currently relies on manual intervention.
- Monitoring is optional but recommended; monitoring setup shown for reference.
