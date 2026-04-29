# 🛡️High Availability & Backup Strategy

> This document describes the high‑availability architecture and backup procedures planned for the Hospital Sa Palomera informatics system. It aligns with the infrastructure requirements stated in the intermodular project statement and is intended to serve as the blueprint for implementation in the `docs/03_Infrastructure/` folder.

## Purpose

The hospital requires the system to be available **24 × 7** with no single point of failure. The proposed architecture provides:

* **Database redundancy** via PostgreSQL streaming replication (active‑passive).
* **Application redundancy** using a load‑balanced pair of Flask API instances.
* **Automated daily backups** with local retention (5 copies) and cloud off‑site storage.
* **Recovery procedures** to restore either the whole database or selected critical tables.

All components are designed to be simulated on **two VMware virtual machines** (one acting as the on‑premise node, the other as a cloud replica) so the entire setup can be documented and tested in a lab environment before any physical deployment.

## Current Infrastructure Documentation

The project already contains foundational infrastructure files that will be extended with this HA strategy:

* [`docs/03_Infrastructure/TLS_Configuration.md`](https://github.com/yosseferrazik/hospital-management-project/blob/main/docs/03_Infrastructure/TLS_Configuration.md) – details the SSL/ TLS setup for PostgreSQL and the Flask API.
* [`docs/03_Infrastructure/GDPR_Compliance.md`](https://github.com/yosseferrazik/hospital-management-project/blob/main/docs/03_Infrastructure/GDPR_Compliance.md) – covers data protection and security measures required by the AEPD (Spanish Data Protection Agency).

The planned HA and backup configurations will be placed alongside these files.

## Planned Architecture

The final infrastructure will consist of two nodes:

| Node | Role | Components | Network (VM simulation) |
|------|------|------------|--------------------------|
| **Node A (on‑premise)** | Primary | PostgreSQL (primary), Flask API #1, HAProxy, backup scripts, MinIO (cloud storage simulation) | 192.168.1.101 |
| **Node B (cloud / secondary)** | Replica | PostgreSQL (standby), Flask API #2 | 192.168.1.102 |

All components will be **containerised with Docker** for reproducibility, except the Tkinter client, which remains a native executable communicating with the exposed API endpoints.

## Database High Availability

### Replication Type

**PostgreSQL streaming replication (asynchronous, active‑passive).**  
This meets the hospital’s requirement for a replica in a different site while keeping the implementation manageable for the project’s scope.

### Configuration Overview

1. **Primary node (Node A)**
   - `wal_level = replica`
   - `max_wal_senders = 5`
   - `listen_addresses = '*'`
   - `ssl = on` (TLS certificates already documented)
   - Create a dedicated replication user:
     ```sql
     CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'secure_password';
     ```

2. **Standby node (Node B)**
   - Run `pg_basebackup` from Node A to obtain the initial data copy.
   - Create a `standby.signal` file in the data directory.
   - Set `primary_conninfo` in `postgresql.conf`:
     ```
     primary_conninfo = 'host=192.168.1.101 port=5432 user=replicator password=secure_password'
     ```
   - Enable `hot_standby = on` to allow read‑only queries on the replica.

3. **Failover**
   - Manual promotion is used for the project (simpler, fully documentable).
   - On failure of the primary, promote the standby with:
     ```bash
     pg_ctl promote -D /path/to/data
     ```
   - A future enhancement could implement automatic failover with **repmgr** or **Patroni**.

### Replication Monitoring

A simple periodic query on the primary checks replication status:

```sql
SELECT pid, state, sync_state, replay_lag 
FROM pg_stat_replication;
```

Logging will be configured to alert the administrator if the replica falls behind by more than 5 minutes.

## Application (API) High Availability

The Flask API runs on both nodes because:

* It is stateless (all session data is stored in the JWT token, not in memory).
* It allows the load balancer to distribute traffic and provides redundancy.

### Load Balancer: HAProxy

- Deployed on Node A (or as a dedicated container) listening on port 80.
- Configuration in `haproxy.cfg`:
  ```
  frontend api_front
      bind *:80
      default_backend api_back

  backend api_back
      balance roundrobin
      server node-a 192.168.1.101:5000 check
      server node-b 192.168.1.102:5000 check
  ```
- The Tkinter client will be configured to send all requests to `http://192.168.1.101/api` (the HAProxy endpoint).

## Backup Strategy

The hospital requires **daily backups**, keeping the **five most recent copies locally** and uploading one copy each day to a cloud service.

### Local Backup Script

A Python script (`backup_manager.py`) will be scheduled via **cron** on Node A:

- Run `pg_dump` to create a plain SQL dump (or custom format).
- Rotate old backups: keep only the 5 newest files.
- Store backups in `/backups/local/`.

Example core logic:

```python
import subprocess, glob, os
from datetime import datetime

DB_NAME = "hospital_management"
BACKUP_DIR = "/backups/local"
KEEP = 5

date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
dump_file = f"{BACKUP_DIR}/{DB_NAME}_{date_str}.sql"

subprocess.run(f"pg_dump -U postgres -h localhost {DB_NAME} > {dump_file}", shell=True, check=True)

backups = sorted(glob.glob(f"{BACKUP_DIR}/{DB_NAME}_*.sql"))
while len(backups) > KEEP:
    os.remove(backups.pop(0))
```

### Cloud Upload (Simulated S3 with MinIO)

A **MinIO** container will run on Node A, emulating an S3‑compatible cloud object store. The backup script will upload the newly created dump to a bucket named `hospital-backups` using `boto3`.

If the hospital later moves to a real cloud provider (AWS, GCP, Azure), only the endpoint and credentials need to change.

### Backup Restoration Scripts

Two dedicated scripts will be provided:

1. **`restore_full.sh`**
   ```bash
   pg_restore -U postgres -d hospital_management /backups/local/hospital_management_latest.sql
   ```
   (or `psql` for plain SQL dumps).

2. **`restore_tables.sh`** – restores only the two most critical tables (to be decided, e.g. `visits` and `patients`).  
   Uses `pg_restore --table=visits --table=patients`.

These scripts will be documented in the final installation manual.

## Security Considerations (High Availability Context)

All replication traffic and API‑to‑API communication will be encrypted using the **already configured SSL/TLS certificates** (see `TLS_Configuration.md`).

- PostgreSQL replication uses the same SSL certificates – encryption is required.
- HAProxy will be configured to use TLS for backend connections if the APIs run on HTTPS.

The `login_credentials.enc` file used by the Flask backend remains on each node; it must be replicated manually in the active‑passive scenario. A future improvement could store credentials in a shared secret manager.

## Relationship With the Rest of the Project

This HA and backup plan is the blueprint for:

* The **infrastructure documentation** (to be placed in `docs/03_Infrastructure/`).
* The **installation manual** (final deliverable) which will include step‑by‑step commands for setting up replication, HAProxy, and backups.
* The **server deployment** instructions for both the on‑premise and cloud (simulated) nodes.

The current `server/README.md` already describes the single‑instance Flask configuration. This HA document extends that into a production‑ready, two‑node setup.

## Next Steps for Implementation

1. **Draft the detailed configuration files** for PostgreSQL replication (`postgresql.conf`, `pg_hba.conf`, `standby.signal`).
2. **Create the Docker Compose definitions** for both nodes, including environment variables.
3. **Write and test `backup_manager.py`** with local rotation and MinIO upload.
4. **Simulate failure scenarios** (stop Node A, promote Node B) and document the recovery procedure.
5. **Consolidate all instructions** into the final installation manual (`docs/04_Manuals/installation_manual.md`).

---

This document will be expanded and moved into `docs/03_Infrastructure/High_Availability.md` once the actual configurations have been tested in the VMware environment.