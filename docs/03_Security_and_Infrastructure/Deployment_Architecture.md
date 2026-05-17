# Deployment Architecture

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 4.0          |
| Last Updated   | 2026-05-07   |

## Purpose

This document describes the deployment architecture for the Hospital Management System, including hardware infrastructure, node responsibilities, backup strategy, and recovery procedures.

**Scope:**

- Primary node in hospital datacenter
- Secondary replica node in AWS cloud
- Automated daily backups with local retention (5 copies)
- Daily backup upload to cloud storage
- Backup and restore scripts
- Replication diagram and administration manual

**Audience:** Infrastructure engineers, system administrators.

---

## System Architecture Context

The Hospital Management System consists of three main components:

1. **Desktop Client**: Python tkinter application running on user workstations
2. **Backend API**: Flask web service exposing REST endpoints
3. **PostgreSQL Database**: Persistent data store for all operational data

The deployment uses a two-node database cluster with active-passive replication.

---

## Deployment Nodes

| Node                   | Location                     | Role                    | Responsibility                                                      |
|:---------------------- |:---------------------------- |:----------------------- |:------------------------------------------------------------------- |
| Briar (hms-primary-node)   | Hospital datacenter (100.78.155.2) | Active database + API   | Handles all write operations, serves API requests, executes backups |
| Sion (hms-secondary-node)  | AWS EC2 (100.98.214.53)            | Standby database        | Receives streaming replication, read-only queries, DR target        |
| Backup Storage (Local) | Primary node disk            | Local backup retention  | Stores last 5 backup copies                                         |

---

## Replication Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HOSPITAL DATACENTER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         PRIMARY NODE                                │   │
│   │                         Briar (hms-primary-node)                    │   │
│   │                                                                     │   │
│   │   ┌─────────────┐      ┌─────────────────────────────────────────┐  │   │
│   │   │ Desktop     │─────►│ Gunicorn + Flask API (port 5000)        │  │   │
│   │   │ Client      │      └─────────────────┬───────────────────────┘  │   │
│   │   └─────────────┘                        │                          │   │
│   │                                          │ SQLAlchemy               │   │
│   │                                          ▼                          │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │              PostgreSQL Primary (port 5432)                 │   │   │
│   │   │              - Read-write operations                        │   │   │
│   │   │              - Accepts all client writes                    │   │   │
│   │   └─────────────────────────┬───────────────────────────────────┘   │   │
│   │                             │                                       │   │
│   │                             │ Streaming replication                 │   │
│   │                             │ (WAL transfer)                        │   │
│   │                             ▼                                       │   │
│   └─────────────────────────────┼───────────────────────────────────────┘   │
│                                 │                                           │
│                                 │ Tailscale                                 │
│                                 │                                           │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AWS CLOUD                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         REPLICA NODE                                │   │
│   │                         AWS EC2 Instance                            │   │
│   │                                                                     │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │              PostgreSQL Standby (port 5432)                 │   │   │
│   │   │              - Read-only operations                         │   │   │
│   │   │              - Continuous replication from primary          │   │   │
│   │   │              - Failover target                              │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         AWS S3 BUCKET (future)                     │   │
│   │                         hms-backups                                 │   │
│   │                                                                     │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │  Daily backup uploads from primary node (planned)           │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Hardware Infrastructure

### Briar — Primary Node (Hospital Datacenter)

| Component         | Specification                        | Justification                                                                  |
|:----------------- |:------------------------------------ |:------------------------------------------------------------------------------ |
| Hostname          | Briar                                | Named server in hospital datacenter                                            |
| OS                | Ubuntu Server 24.04 LTS              | LTS release with long-term support                                             |
| CPU               | 4 vCores                             | Flask API + PostgreSQL primary require moderate compute                        |
| RAM               | 8 GB                                 | PostgreSQL caching and API workers                                             |
| Storage           | 100 GB SSD                           | OS, application files, PostgreSQL data directory                               |
| Network           | 1 Gbps + Tailscale                   | Connectivity to hospital LAN and Tailscale overlay                             |

### Sion — Replica Node (AWS EC2)

| Component           | Specification                | Justification                                          |
|:------------------- |:---------------------------- |:------------------------------------------------------ |
| Hostname            | Sion                         | AWS EC2 standby instance                               |
| OS                  | Ubuntu Server 24.04 LTS      | Same OS as primary for compatibility                   |
| Instance Type       | t3.medium (or equivalent)    | 2 vCPU, 4 GB RAM — sufficient for standby PostgreSQL   |
| Storage (OS + Data) | 80 GB gp3                    | Root volume with PostgreSQL data directory             |
| Network             | Tailscale                    | Overlay connectivity to primary and hospital LAN       |

### Network Requirements

| Connection    | Source            | Destination        | Port | Protocol | Purpose                     |
|:------------- |:----------------- |:------------------ |:----:|:-------- |:--------------------------- |
| API traffic   | Desktop clients   | Briar (100.78.155.2) | 5000 | TCP      | Application requests        |
| Replication   | Briar             | Sion (100.98.214.53) | 5432 | TCP      | Streaming replication (WAL) |
| Admin access  | Admin workstation | Both nodes          | 22   | TCP      | SSH maintenance             |

**Connectivity:** Nodes communicate via Tailscale overlay + hospital internal LAN. No VPN required.

---

## Storage Layout

### Storage Layout

Default partitioning from Ubuntu Server 24.04 installation is used. Key paths:

| Path                  | Purpose                                          |
|:--------------------- |:------------------------------------------------ |
| `/opt/hms`            | Application releases, venv, operational scripts  |
| `/var/log/hms`        | Application logs (API access, error)             |
| `/var/lib/postgresql` | PostgreSQL 16 data directory                     |

---

## Backup Strategy

Backup strategy is documented in the canonical runbook at `docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md`.

---

## Backup Scripts and Restore Procedures

Operational scripts, cron examples, and the full restore procedure are maintained in the canonical runbook. To avoid duplication, the detailed scripts previously embedded here have been moved to:

docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md

Refer to that runbook for exact script contents, cron entries, encryption examples, verification steps, and safe restore procedures.

---

## Replication and High-Availability

Summary:

- The deployment uses PostgreSQL streaming replication (primary → standby) with WAL shipping and pg_basebackup for initial sync.
- Monitoring and promotion procedures are operationally sensitive and maintained in a canonical runbook.

For exact commands, scripts, cron examples and step-by-step procedures for configuring replication, promoting standbys, monitoring replication lag and running failover drills, see the canonical runbook:

docs/04_Operations_and_Manuals/Replication_and_HA_Runbook.md

Keep this file authoritative; infra-level docs should only summarize and link to it.
---

## Deployment Checklist

### Pre-Deployment

- [ ] Provision primary node hardware (hospital datacenter)
- [ ] Create AWS EC2 instance for replica node
- [ ] Create AWS S3 bucket for cloud backups
- [ ] Configure network connectivity between primary and AWS (VPN or direct)
- [ ] Install Ubuntu Server 24.04 LTS on both nodes
- [ ] Configure NTP/Chrony on both nodes
- [ ] Create partition layout on primary node

### Primary Node Setup

- [ ] Install PostgreSQL 16
- [ ] Install Python 3.12 and pip
- [ ] Clone HMS repository to `/opt/hms/repo`
- [ ] Install Flask dependencies
- [ ] Configure PostgreSQL for replication (replication user, `postgresql.conf`, `pg_hba.conf`)
- [ ] Create `/backups/local` directory with proper permissions
  - [ ] Deploy backup script as documented in docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md (recommended location: `/usr/local/bin/backup.sh`, chmod 700)
  - [ ] Deploy cloud upload script as documented in docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md (recommended location: `/usr/local/bin/upload_to_s3.sh`, chmod 700)
- [ ] Configure AWS CLI with IAM credentials
- [ ] Add cron jobs for backup and upload
- [ ] Start Flask API

### Replica Node Setup

- [ ] Install PostgreSQL 16 (same version as primary)
- [ ] Perform `pg_basebackup` from primary
- [ ] Configure `postgresql.conf` for standby
- [ ] Start PostgreSQL and verify replication
- [ ] Test read-only queries on replica

### Backup Verification

- [ ] Run backup script manually as documented: `sudo -u postgres /usr/local/bin/backup.sh` or use the canonical runbook example at docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md
- [ ] Verify backup file appears in `/backups/local/`
- [ ] Run cloud upload script manually
- [ ] Verify backup appears in S3 bucket
- [ ] Test full restore: `./restore_full.sh /backups/local/backup_*.sql.gz`
- [ ] Test table restore (patients + staff): `./restore_tables.sh /backups/local/backup_*.sql.gz`

### Client Setup

- [ ] Install Python 3.10+ with tkinter on user workstations
- [ ] Update API base URL to primary node IP
- [ ] Test client login and operations

---

## Troubleshooting

### Replication Not Working

| Symptom                     | Diagnosis                                             | Solution                                                |
|:--------------------------- |:----------------------------------------------------- |:------------------------------------------------------- |
| `pg_stat_replication` empty | Check network: `telnet <AWS_IP> 5432`                 | Open firewall port 5432                                 |
| Authentication failed       | Check logs: `tail /var/log/postgresql/*.log`          | Verify password in `pg_hba.conf` and `primary_conninfo` |
| Replication lag growing     | Check WAL size: `du -sh /var/lib/postgresql/*/pg_wal` | Increase `wal_keep_size`                                |

### Backup Fails

| Symptom                | Diagnosis                                   | Solution                               |
|:---------------------- |:------------------------------------------- |:-------------------------------------- |
| No backup file created | Check cron log: `grep CRON /var/log/syslog` | Verify script path and permissions     |
| Upload to S3 fails     | Check AWS CLI: `aws s3 ls`                  | Verify IAM credentials and bucket name |
