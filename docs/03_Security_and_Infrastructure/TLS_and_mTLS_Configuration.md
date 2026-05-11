# TLS and mTLS Configuration

## Document Control

| Field          | Value        |
|:-------------- |:------------ |
| Document Owner | Project Team |
| Status         | Active       |
| Version        | 2.2          |
| Last Updated   | 2026-05-07   |

## Purpose

Define the transport-security baseline for HMS communications, focusing on PostgreSQL encryption and replication security.

## Security Objective

All sensitive communication paths must be encrypted in transit.

## Scope

| Communication Path                          | Target Control                                   |
|:------------------------------------------- |:------------------------------------------------ |
| Desktop client to Flask API                 | TLS (HTTPS) - future implementation              |
| Flask API to PostgreSQL primary             | TLS                                              |
| PostgreSQL primary to PostgreSQL standby    | TLS (replication over encrypted channel)         |
| Administrative access to PostgreSQL nodes   | TLS + SSH                                       |
| Backup upload to AWS S3                     | HTTPS (native)                                  |

## Baseline Requirements

- Use TLS 1.2 or higher.
- Protect private keys and certificates outside version control.
- Validate server identity on all client connections.
- Disable obsolete protocols (SSLv2, SSLv3, TLS 1.0, TLS 1.1).

## Certificate Model

| Component               | Requirement                                                  |
|:----------------------- |:------------------------------------------------------------ |
| Certificate authority   | Private CA for internal PostgreSQL certificates              |
| Server certificates     | Required for PostgreSQL primary and standby nodes            |
| Client certificates     | Optional for mTLS (admin connections)                        |
| Renewal                 | Certificates renewed every 12 months                         |

---

## PostgreSQL TLS Configuration

### Step 1: Generate Certificates (Development/Lab)

On **each PostgreSQL node** (primary and standby):

```bash
# Generate self-signed certificate (development only)
cd /etc/ssl/certs
openssl req -new -x509 -days 365 -nodes -text -out server.crt \
  -keyout server.key -subj "/CN=postgresql.hms.internal"

# Set correct permissions
chmod 600 server.key
chmod 644 server.crt
```

**Note:** For production, use institutional CA instead of self-signed.

### Step 2: Configure PostgreSQL (`postgresql.conf`)

On **both primary and standby nodes**:

```ini
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ciphers = 'HIGH:!aNULL:!MD5'
ssl_prefer_server_ciphers = on
ssl_min_protocol_version = 'TLSv1.2'
```

### Step 3: Configure Client Authentication (`pg_hba.conf`)

On **primary node** (require TLS for remote connections):

```conf
# Require TLS for all remote connections
hostssl    all             all             0.0.0.0/0               md5
hostssl    replication     replicator      0.0.0.0/0               md5

# Reject non-TLS connections
hostnossl  all             all             0.0.0.0/0               reject
```

On **standby node** (require TLS for replication and admin):

```conf
hostssl    all             all             0.0.0.0/0               md5
hostssl    replication     replicator      0.0.0.0/0               md5
hostnossl  all             all             0.0.0.0/0               reject
```

### Step 4: Restart PostgreSQL

```bash
sudo systemctl restart postgresql
```

---

## TLS for Replication (Primary to Standby)

### Configure Primary for TLS Replication

The `primary_conninfo` on standby must specify TLS:

On **standby node**, edit `postgresql.conf` or `recovery.conf`:

```ini
primary_conninfo = 'host=<PRIMARY_IP> port=5432 user=replicator password=xxx sslmode=require'
```

### Verify TLS Replication

On **primary node**:

```sql
SELECT client_addr, ssl, ssl_version, ssl_cipher 
FROM pg_stat_ssl 
JOIN pg_stat_replication ON pg_stat_ssl.pid = pg_stat_replication.pid;
```

Expected output:

```
 client_addr | ssl | ssl_version | ssl_cipher
-------------+-----+-------------+--------------------
 10.0.1.10   | t   | TLSv1.2     | ECDHE-RSA-AES256-GCM-SHA384
```

---

## TLS for API to PostgreSQL

### Flask API Connection String

```python
# Use SSL/TLS for database connection
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@<PRIMARY_IP>:5432/hospital_management?sslmode=require'
```

### SSL Modes

| sslmode | Description |
|:--------|:------------|
| `disable` | No TLS (development only) |
| `require` | TLS required, no certificate validation |
| `verify-ca` | TLS + validate CA |
| `verify-full` | TLS + validate CA + hostname |

**Recommended for lab:** `require`

**Recommended for production:** `verify-full`

---

## TLS for Administrative Access

### Admin Client Connection (psql)

```bash
# With TLS
PGPASSWORD=xxx psql -h <PRIMARY_IP> -U postgres -d hospital_management --set=sslmode=require

# With TLS + certificate validation
PGPASSWORD=xxx psql -h <PRIMARY_IP> -U postgres -d hospital_management \
  --set=sslmode=verify-ca --set=sslrootcert=/etc/ssl/certs/ca.crt
```

### Optional mTLS for Admin Connections

For mTLS, clients must present a valid certificate:

In `postgresql.conf`:

```ini
ssl_ca_file = '/etc/ssl/certs/ca.crt'
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
```

In `pg_hba.conf`:

```conf
# Require client certificate
hostssl    all             all             0.0.0.0/0               cert
```

---

## Certificate Generation for Production (Private CA)

### Step 1: Create Certificate Authority (CA)

```bash
# On a secure management machine
mkdir ~/ca && cd ~/ca

# Generate CA private key
openssl genrsa -aes256 -out ca.key 4096

# Generate CA certificate (valid 10 years)
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
  -subj "/CN=HMS Internal CA"
```

### Step 2: Generate Server Certificate for PostgreSQL

```bash
# Generate server private key
openssl genrsa -out postgresql-server.key 2048

# Generate CSR
openssl req -new -key postgresql-server.key -out postgresql-server.csr \
  -subj "/CN=postgresql.hms.internal"

# Sign certificate with CA (valid 1 year)
openssl x509 -req -in postgresql-server.csr -CA ca.crt -CAkey ca.key \
  -CAcreateserial -out postgresql-server.crt -days 365
```

### Step 3: Distribute Certificates

| File | Destination | Permissions |
|:-----|:------------|:------------|
| `postgresql-server.crt` | `/etc/ssl/certs/server.crt` | 644 |
| `postgresql-server.key` | `/etc/ssl/private/server.key` | 600 |
| `ca.crt` | `/etc/ssl/certs/ca.crt` | 644 |

---

## Verification Commands

### Check PostgreSQL TLS Status

```bash
# Check if SSL is enabled
sudo -u postgres psql -c "SHOW ssl;"

# Check SSL configuration
sudo -u postgres psql -c "SHOW ssl_cert_file;"
sudo -u postgres psql -c "SHOW ssl_key_file;"
```

### Test TLS Connection

```bash
# Test from API node to PostgreSQL
openssl s_client -connect <PRIMARY_IP>:5432 -starttls postgres -CAfile /etc/ssl/certs/ca.crt
```

### Check Replication TLS

```sql
SELECT pid, usename, application_name, client_addr, ssl, ssl_cipher 
FROM pg_stat_ssl 
JOIN pg_stat_replication ON pg_stat_ssl.pid = pg_stat_replication.pid;
```

---

## Certificate Renewal Procedure

### Annual Renewal (30 days before expiry)

1. Generate new server certificate (Step 2)
2. Copy to PostgreSQL nodes
3. Reload PostgreSQL configuration:

```bash
sudo systemctl reload postgresql
```

4. Verify new certificate:

```sql
SELECT ssl_cert_valid_from, ssl_cert_valid_until 
FROM pg_stat_ssl 
WHERE pid = pg_backend_pid();
```

### Monitoring Certificate Expiry

Add to cron (daily check) referencing the canonical script in the repo:

```bash
0 9 * * * /bin/bash $(pwd)/scripts/ops/check_cert_expiry.sh
```

The canonical script is available at `scripts/ops/check_cert_expiry.sh` in the repository.
