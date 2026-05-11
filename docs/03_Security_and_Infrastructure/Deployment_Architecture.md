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

| Node                   | Location            | Role                    | Responsibility                                                              |
|:---------------------- |:------------------- |:----------------------- |:--------------------------------------------------------------------------- |
| Primary Node           | Hospital datacenter | Active database + API   | Handles all write operations, serves API requests, executes backups         |
| Replica Node           | AWS Cloud           | Standby database        | Receives streaming replication, read-only queries, disaster recovery target |
| Backup Storage (Local) | Primary node disk   | Local backup retention  | Stores last 5 backup copies                                                 |
| Backup Storage (Cloud) | AWS S3              | Cloud backup repository | Receives one backup copy daily                                              |

---

## Replication Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          HOSPITAL DATACENTER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         PRIMARY NODE                                │   │
│   │                         vm-hms-primary                              │   │
│   │                                                                     │   │
│   │   ┌─────────────┐      ┌─────────────────────────────────────────┐  │   │
│   │   │ Desktop     │─────►│ Flask API (port 5000)                   │  │   │
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
│                                 │ Internet / VPN                            │
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
│   │                         AWS S3 BUCKET                               │   │
│   │                         hms-backups                                 │   │
│   │                                                                     │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │  Daily backup uploads from primary node                     │   │   │
│   │   │  Encrypted at rest, versioned, lifecycle policy (30 days)   │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   │                                                                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Hardware Infrastructure

### Primary Node (Hospital Datacenter)

| Component         | Specification                     | Justification                                                                            |
|:----------------- |:--------------------------------- |:---------------------------------------------------------------------------------------- |
| CPU               | 4 vCores (Intel Xeon or AMD EPYC) | Flask API + PostgreSQL primary require moderate compute; supports concurrent staff users |
| RAM               | 8 GB                              | PostgreSQL caching and API worker processes; sufficient for hospital workload            |
| Storage (OS)      | 40 GB SSD                         | Ubuntu Server OS and application files                                                   |
| Storage (Data)    | 100 GB SSD                        | PostgreSQL data directory (`/var/lib/postgresql`)                                        |
| Storage (Backups) | 50 GB SSD                         | Local backup retention (`/backups/local`) - holds 5 backup copies                        |
| Network           | 1 Gbps                            | Connectivity to hospital LAN and outbound internet to AWS                                |
| Power             | Redundant PSU                     | Hospital datacenter standard                                                             |
| Cooling           | Standard rack cooling             | Hospital datacenter standard                                                             |

**Total estimated cost (one-time):** $2,500 - $4,000 depending on supplier

### Replica Node (AWS Cloud)

| Component           | Specification                | Justification                                          |
|:------------------- |:---------------------------- |:------------------------------------------------------ |
| Instance Type       | t3.medium (or equivalent)    | 2 vCPU, 4 GB RAM - sufficient for standby PostgreSQL   |
| Storage (OS + Data) | 80 GB gp3 (SSD)              | Root volume with PostgreSQL data directory             |
| Network             | Up to 5 Gbps                 | Connectivity for replication stream from primary       |
| Region              | Closest to hospital location | Minimizes replication lag (e.g., eu-west-1, us-east-1) |

**Total estimated cost (monthly):** $40 - $60 (on-demand, Linux)

### AWS S3 Backup Storage

| Component | Specification        | Justification                           |
|:--------- |:-------------------- |:--------------------------------------- |
| Bucket    | Standard tier        | Daily backup upload (one per day)       |
| Storage   | 30 GB (growing)      | Compressed daily backups (~500 MB each) |
| Lifecycle | Delete after 30 days | Matches retention requirement           |

**Total estimated cost (monthly):** $1 - $3

### Network Requirements

| Connection    | Source            | Destination        | Port | Protocol | Purpose                     |
|:------------- |:----------------- |:------------------ |:----:|:-------- |:--------------------------- |
| Replication   | Primary node      | Replica node (AWS) | 5432 | TCP      | Streaming replication (WAL) |
| API traffic   | Desktop clients   | Primary node       | 5000 | TCP      | Application requests        |
| Backup upload | Primary node      | AWS S3             | 443  | HTTPS    | Daily backup upload         |
| Admin access  | Admin workstation | Both nodes         | 22   | TCP      | SSH maintenance             |

**VPN Recommendation:** Use site-to-site VPN or AWS Direct Connect for secure replication traffic. For lab environments, SSH tunneling or WireGuard is acceptable.

---

## Storage Layout

### Primary Node Partitioning

| Mount Point           | Size   | Filesystem | Purpose                                                  |
|:--------------------- |:------ |:---------- |:-------------------------------------------------------- |
| `/`                   | 40 GB  | ext4       | Operating system, PostgreSQL packages, Flask application |
| `/var/lib/postgresql` | 100 GB | ext4       | PostgreSQL data directory (WAL, database files)          |
| `/backups/local`      | 50 GB  | ext4       | Local backup retention (last 5 copies)                   |
| `/var/log`            | 5 GB   | ext4       | System and application logs                              |
| `swap`                | 2 GB   | -          | Swap space                                               |

### Replica Node (AWS) Storage

| Mount Point | Size  | Type    | Purpose                                      |
|:----------- |:----- |:------- |:-------------------------------------------- |
| `/`         | 80 GB | gp3 EBS | Operating system + PostgreSQL data directory |

### Local Backup Storage Calculation

- Compressed daily backup size: ~500 MB
- 5 backups retained: 5 × 500 MB = 2.5 GB
- Additional space for WAL archives and temp files: ~47 GB buffer
- **Total 50 GB is sufficient**

---

## Backup Strategy

### Backup Types

| Type               | Frequency       | Destination                    | Retention     | Tool                  |
|:------------------ |:--------------- |:------------------------------ |:------------- |:--------------------- |
| Full database dump | Daily (2:00 AM) | Local disk (`/backups/local/`) | Last 5 copies | `pg_dump` + gzip      |
| Cloud backup       | Daily (3:00 AM) | AWS S3                         | 30 days       | AWS CLI (`aws s3 cp`) |

### Local Backup Retention (Last 5 Copies)

The backup script automatically rotates copies:

```
/backups/local/
├── backup_20260501.sql.gz   # Day 1 (oldest, will be deleted when >5)
├── backup_20260502.sql.gz   # Day 2
├── backup_20260503.sql.gz   # Day 3
├── backup_20260504.sql.gz   # Day 4
├── backup_20260505.sql.gz   # Day 5 (most recent)
```

When a 6th backup is created, the oldest is automatically deleted.

### Backup Encryption

- **Local backups:** No encryption (inside hospital secure datacenter)
- **S3 backups:** Server-side encryption with AES-256 (SSE-S3)

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
- [ ] Install Ubuntu Server 22.04 LTS on both nodes
- [ ] Configure NTP/Chrony on both nodes
- [ ] Create partition layout on primary node

### Primary Node Setup

- [ ] Install PostgreSQL 14
- [ ] Install Python 3.10+ and pip
- [ ] Clone HMS repository to `/opt/hms`
- [ ] Install Flask dependencies
- [ ] Configure PostgreSQL for replication (replication user, `postgresql.conf`, `pg_hba.conf`)
- [ ] Create `/backups/local` directory with proper permissions
  - [ ] Deploy backup script as documented in docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md (recommended location: `/usr/local/bin/backup.sh`, chmod 700)
  - [ ] Deploy cloud upload script as documented in docs/04_Operations_and_Manuals/Backup_and_Restore_Runbook.md (recommended location: `/usr/local/bin/upload_to_s3.sh`, chmod 700)
- [ ] Configure AWS CLI with IAM credentials
- [ ] Add cron jobs for backup and upload
- [ ] Start Flask API

### Replica Node Setup

- [ ] Install PostgreSQL 14 (same version as primary)
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
