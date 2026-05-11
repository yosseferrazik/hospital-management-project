# Network Architecture

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 1.1          |
| Last Updated   | 2026-05-07   |

## Purpose

Define the logical network zones, expected communication flows, and network-level security principles for HMS deployments.

## Scope

Includes:

- Logical network segmentation
- Service-to-service communication paths
- Intended exposure boundaries
- Port and protocol expectations
- Security controls at the network level
- Lab and future deployment assumptions

It does not replace the application architecture, deployment guide, or TLS-specific configuration documents.

---

## Current vs Target State

### Current State

The current implementation is primarily executed in a local or lab environment:

- The desktop client calls the backend API at `http://localhost:5000/api`.
- The backend connects to PostgreSQL using environment-based configuration.
- Network boundaries are minimal in the current development flow.

### Target State

The target architecture assumes a segmented deployment model where:

- Primary node (hospital datacenter) hosts the active database and API.
- Secondary node (AWS Cloud) hosts the standby database replica.
- Client devices access the application service on the primary node.
- PostgreSQL replication flows from primary to AWS over encrypted connection.
- Backup uploads flow from primary node to AWS S3.

---

## Network Design Principles

- Expose only the minimum number of services required for system operation.
- Separate client-facing, application, and database responsibilities into distinct trust zones.
- Restrict direct access to the database from user devices.
- Encrypt all sensitive traffic between zones, especially across the internet to AWS.
- Preserve a clear path toward redundancy and failover.

---

## Logical Network Zones

| Zone             | Purpose                               | Main Components                                                                  |
|:---------------- |:------------------------------------- |:-------------------------------------------------------------------------------- |
| Client Zone      | End-user access layer                 | Staff desktop clients running the HMS user interface (hospital LAN)              |
| Application Zone | Business and API processing           | Flask API on primary node (hospital datacenter)                                  |
| Data Zone        | Persistent storage layer              | PostgreSQL primary (hospital) + PostgreSQL standby (AWS)                         |
| Management Zone  | Administrative and maintenance access | Admin workstation, backup coordinators, AWS management console                   |
| Cloud Storage    | Backup repository                     | AWS S3 bucket for daily backup uploads                                           |

---

## High-Level Topology

```text
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              HOSPITAL DATACENTER                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌──────────────┐      ┌──────────────────┐      ┌──────────────────────────────┐   │
│  │ Client Zone  │      │ Application Zone │      │ Data Zone (Primary)          │   │
│  │ Desktop      │─────►│ Flask API        │─────►│ PostgreSQL Primary           │   │
│  │ Clients      │      │ (port 5000)      │      │ (port 5432)                  │   │
│  └──────────────┘      └────────┬─────────┘      └──────────────┬───────────────┘   │
│                                 │                                │                  │
│                                 │                                │ (replication)    │
│                                 │                                │                  │
│                                 │                                ▼                  │
│                                 │                        ┌──────────────────┐       │
│                                 │                        │ Backup Storage   │       │
│                                 │                        │ /backups/local/  │       │
│                                 │                        │ (5 copies)       │       │
│                                 │                        └──────────────────┘       │
│                                 │                                                   │
│  ┌──────────────┐               │                                                   │
│  │ Management   │               │                                                   │
│  │ Zone         │               │                                                   │
│  │ Admin Client │◄──────────────┘                                                   │
│  └──────────────┘                                                                   │
│                                                                                     │
└──────────────────────────────────────────┬──────────────────────────────────────────┘
                                           │
                                           │ Internet / VPN (encrypted)
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  AWS CLOUD                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │ Data Zone (Standby)                                                           │   │
│  │ ┌────────────────────────────────────────────────────────────────────────┐   │   │
│  │ │ PostgreSQL Standby (read-only)                                          │   │   │
│  │ │ (port 5432)                                                            │   │   │
│  │ └────────────────────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │ Cloud Storage                                                                │   │
│  │ ┌────────────────────────────────────────────────────────────────────────┐   │   │
│  │ │ AWS S3 Bucket (s3://hms-backups/)                                      │   │   │
│  │ │ Daily backup uploads, 30-day retention, AES-256 encryption             │   │   │
│  │ └────────────────────────────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Main Communication Flows

| Source                         | Destination                    | Purpose                                                       | Direction              | Encryption |
|:------------------------------ |:------------------------------ |:------------------------------------------------------------- |:---------------------- |:-----------|
| Desktop client                 | Flask API (primary node)       | User login, operations, queries                               | Client → Application   | TLS 1.2+   |
| Flask API (primary)            | PostgreSQL primary             | Read/write database operations                                | Application → Data     | TLS        |
| PostgreSQL primary             | PostgreSQL standby (AWS)       | Streaming replication (WAL transfer)                          | Data → Data            | TLS/SSH    |
| Primary node (backup script)   | AWS S3                         | Daily backup upload                                           | Application → Storage  | HTTPS      |
| Admin client                   | PostgreSQL primary             | Emergency database access, maintenance                        | Management → Data      | TLS        |
| Admin client                   | PostgreSQL standby (AWS)       | Restore testing, validation                                   | Management → Data      | TLS        |
| Admin client                   | AWS S3                         | Backup download for restore testing                           | Management → Storage   | HTTPS      |

---

## Network Exposure Model

### Allowed Exposure

| Service                          | Exposed To                          | Condition                                                      |
|:-------------------------------- |:----------------------------------- |:-------------------------------------------------------------- |
| Flask API (port 5000)            | Hospital LAN (client workstations)  | Internal hospital network only, not public internet           |
| PostgreSQL primary (port 5432)   | Flask API (primary node)            | Same datacenter, loopback or internal IP only                 |
| PostgreSQL primary (port 5432)   | PostgreSQL standby (AWS)            | Over VPN or encrypted tunnel only                             |
| PostgreSQL standby (port 5432)   | Admin client (hospital)             | Over VPN only, not publicly exposed                           |
| AWS S3 (HTTPS 443)               | Primary node (backup upload)        | Authenticated with IAM credentials, bucket not public         |

### Disallowed Exposure

- End-user devices must not connect directly to PostgreSQL (any node).
- PostgreSQL ports must not be publicly exposed on the internet.
- AWS S3 bucket must have block public access enabled.
- Management interfaces (SSH, admin tools) must not share exposure with application traffic.

---

## Ports and Protocols

| Source                | Destination                       | Protocol                           | Port        | Encryption                     |
|:--------------------- |:--------------------------------- |:---------------------------------- |:----------- |:------------------------------ |
| Desktop client        | Flask API (primary)               | HTTP / HTTPS                      | 5000 / 443  | TLS 1.2+ (target)              |
| Flask API             | PostgreSQL primary                | PostgreSQL over TCP                | 5432        | TLS (optional, recommended)    |
| PostgreSQL primary    | PostgreSQL standby (AWS)          | PostgreSQL replication (WAL)       | 5432        | TLS or SSH tunnel              |
| Primary node          | AWS S3                            | HTTPS (S3 API)                     | 443         | TLS 1.2+                       |
| Admin client          | PostgreSQL primary                | PostgreSQL over TCP                | 5432        | TLS + SSH key                  |
| Admin client          | PostgreSQL standby (AWS)          | PostgreSQL over TCP                | 5432        | TLS + SSH key + VPN            |
| Admin client          | AWS S3                            | HTTPS (AWS CLI)                    | 443         | TLS 1.2+                       |
| Backup script         | Local backup directory            | Filesystem I/O                     | N/A         | Filesystem permissions (700)   |

---

## Security Controls

### Segmentation

| Control                        | Implementation                                                                 |
|:------------------------------ |:------------------------------------------------------------------------------- |
| Database isolation            | PostgreSQL primary accessible only from Flask API and admin client             |
| AWS security groups           | Restrict PostgreSQL standby to accept connections only from primary IP and VPN |
| S3 bucket policy              | Block all public access; allow only authenticated IAM users/roles              |
| Hospital firewall             | Allow client → API (port 5000), deny client → database (port 5432)              |
| VPN requirement               | All access to AWS resources (standby, S3) from hospital requires VPN           |

### Traffic Protection

| Path                           | Protection Method                                                                 |
|:------------------------------ |:--------------------------------------------------------------------------------- |
| Client → API                   | HTTPS (TLS 1.2+) in target deployment; HTTP only in development                  |
| API → PostgreSQL primary       | PostgreSQL TLS (configure `ssl = on` in `postgresql.conf`)                        |
| Replication (primary → standby)| SSH tunnel or PostgreSQL TLS + VPN                                               |
| Backup upload → S3             | HTTPS + SSE-S3 encryption (AES-256) at rest                                       |
| Admin → any database           | TLS + SSH key authentication; VPN required for AWS resources                     |

### Access Control

| Principle                      | Implementation                                                                 |
|:------------------------------ |:------------------------------------------------------------------------------- |
| Least privilege network exposure | Allow only required source-destination pairs via firewall/Security Groups      |
| Default deny                   | All traffic blocked unless explicitly permitted                                 |
| No direct user database access | Client workstations cannot reach port 5432 on any database node                 |
| Separate admin paths           | Management access uses distinct network paths or jump hosts                     |

---

## Target Deployment Pattern

The target deployment model aligns with the high-availability planning baseline:

| Node                     | Location               | Network Role                                                         |
|:------------------------ |:---------------------- |:-------------------------------------------------------------------- |
| Primary node             | Hospital datacenter    | Hosts Flask API (port 5000) and PostgreSQL primary (port 5432)       |
| Secondary node (standby) | AWS Cloud (EC2)        | Hosts PostgreSQL standby (port 5432), reachable only via VPN         |
| Backup storage           | AWS S3                 | Receives daily backup uploads from primary node via HTTPS            |
| Admin client             | Hospital management LAN| Manages both database nodes via VPN to AWS                           |

In this model:

- Client traffic reaches the API endpoint on the primary node only.
- Replication traffic flows from primary to AWS standby over encrypted connection.
- Backup traffic follows separate controlled route from primary to S3.
- Administrative access requires VPN for AWS resources.

---

## Trust Boundaries

| Boundary                                | Risk Focus                                                     | Mitigation                                                    |
|:--------------------------------------- |:-------------------------------------------------------------- |:------------------------------------------------------------- |
| Client Zone → Application Zone          | Authentication, transport security, endpoint exposure          | JWT tokens, TLS, API rate limiting                            |
| Application Zone → Data Zone (primary)  | Confidentiality, integrity, least privilege                    | Database credentials, TLS, connection pooling                 |
| Data Zone (primary) → Data Zone (AWS)   | Replication security, data interception, latency               | TLS or SSH tunnel, VPN, replication monitoring                |
| Application Zone → Cloud Storage (S3)   | Backup data leakage, unauthorized access                       | IAM authentication, SSE-S3 encryption, HTTPS                  |
| Management Zone → Data Zone (both)      | Administrative misuse, overexposure, privileged access control | Separate credentials, audit logging, VPN requirement, SSH keys |
| Client Zone → Data Zone (any)           | Direct data access bypassing application logic                 | Firewall rule: block port 5432 from client subnet             |

---

## Network Configuration Checklist

When deploying HMS to the target two-node + S3 environment:

### Pre-Deployment

- [ ] Assign private IP addresses to primary node (hospital LAN)
- [ ] Launch AWS EC2 instance in private subnet (no public IP)
- [ ] Create AWS S3 bucket with block public access enabled
- [ ] Establish VPN or encrypted tunnel between hospital and AWS VPC
- [ ] Configure security groups in AWS:
  - Allow PostgreSQL (5432) from primary node IP only
  - Allow SSH (22) from hospital admin subnet only
- [ ] Configure hospital firewall:
  - Allow client → primary API (port 5000)
  - Block client → any database (port 5432)
  - Allow primary → AWS standby (port 5432 over VPN)
  - Allow primary → AWS S3 (port 443)

### Deployment Verification

- [ ] Verify client can reach API: `curl http://<primary_ip>:5000/api/dummy/health`
- [ ] Verify API can reach primary database
- [ ] Verify replication from primary to AWS standby: `SELECT * FROM pg_stat_replication;`
- [ ] Verify backup upload to S3: `aws s3 ls s3://hms-backups/daily/`
- [ ] Verify admin client can reach both database nodes over VPN
- [ ] Test failover: promote standby, update API connection, verify functionality

### Documentation

- [ ] Document all firewall rules and security group configurations
- [ ] Record IP addresses and DNS names for all nodes
- [ ] Save VPN configuration and credentials in secure location
- [ ] Document S3 bucket name and IAM roles

---

## Security Considerations for Network Design

| Consideration              | Implementation                                                                 |
|:-------------------------- |:------------------------------------------------------------------------------- |
| Segmentation               | Use VLANs in hospital, AWS Security Groups, and VPC private subnets            |
| Firewall Rules             | Stateful firewalls with explicit allow lists; default deny                     |
| VPN Access                 | All AWS resource access requires VPN (no direct internet exposure)             |
| Replication Security       | PostgreSQL streaming replication over VPN or TLS                               |
| Backup Security            | S3 with SSE-S3 encryption, IAM least privilege, lifecycle policy (30 days)     |
| Monitoring                 | Alert on replication lag > 1 minute, backup failures, unusual S3 access        |
| Audit Logging              | S3 access logs, PostgreSQL connection logs, firewall logs                      |

---

## Development and Lab Assumptions

- The current development model may run all services on a single host for convenience.
- Even in local mode, the architecture is documented as if services were separable.
- The hardcoded `localhost:5000` client configuration is a temporary development detail.
- VMware lab simulations respect network zone separation even if implemented on one physical machine.
- For lab environments without AWS, MinIO on a local VM can simulate S3.
- For lab environments without VPN, SSH tunneling can simulate encrypted replication.
