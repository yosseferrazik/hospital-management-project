
# 🔒 SSL Configuration: PostgreSQL Encryption with Mutual TLS (mTLS)

> This document details the setup and enforcement of SSL/TLS encryption with mutual authentication (mTLS) for the PostgreSQL database used by the Hospital Management System. Both the server and the client application present certificates signed by a trusted Certificate Authority (CA), ensuring maximum security and compliance with healthcare data protection standards.

## 1. Overview

All communication between the Python/Tkinter application and the PostgreSQL database server will be encrypted using **TLS 1.2 or higher** with **mutual authentication (mTLS)** . This requires the client to present a valid certificate signed by the same CA trusted by the server, providing two-way verification and eliminating reliance on passwords over the network.

**Key objectives:**
- Enable SSL with client certificate authentication on the PostgreSQL server.
- Generate a private CA, server certificate, and individual client certificates for each application instance/user.
- Configure `psycopg2` connections to present the client certificate and verify the server certificate.
- Enforce a strict security posture suitable for HIPAA/GDPR compliance.

## 2. Certificate Generation for Mutual TLS

For mTLS, a private Certificate Authority (CA) is established to sign both server and client certificates. In a production environment, the CA's private key must be stored securely (e.g., in a Hardware Security Module).

### 2.1. Create a Private Certificate Authority (CA)

```bash
# 1. Generate CA private key
openssl genrsa -out ca.key 2048

# 2. Create self-signed CA certificate (valid for 10 years)
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/C=ES/ST=Catalonia/L=Barcelona/O=Hospital CA/CN=Hospital Root CA"

# 3. Secure the CA private key
chmod 400 ca.key
```

### 2.2. Generate Server Certificate (Signed by CA)

```bash
# 1. Generate server private key
openssl genrsa -out server.key 2048
chmod 600 server.key

# 2. Create Certificate Signing Request (CSR) for server
openssl req -new -key server.key -out server.csr -subj "/C=ES/ST=Catalonia/L=Barcelona/O=Hospital/CN=db.hospital.local"

# 3. Sign the server CSR with our CA
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt
```

### 2.3. Generate Client Certificate(s) (Signed by CA)

Each client machine (or application user) requires its own certificate. In the context of a Tkinter desktop application, one certificate per installation or per authenticated staff member may be issued.

```bash
# 1. Generate client private key
openssl genrsa -out client.key 2048

# 2. Create CSR for client (Common Name should identify the client, e.g., staff_id)
openssl req -new -key client.key -out client.csr -subj "/C=ES/ST=Catalonia/L=Barcelona/O=Hospital/CN=app_user"

# 3. Sign the client CSR with our CA
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt
```

**File placement:**
- **Server:** `server.key`, `server.crt`, and `ca.crt` (CA certificate) go in the PostgreSQL data directory.
- **Client:** `client.key`, `client.crt`, and `ca.crt` must be accessible to the Python application (e.g., in a `certs/` folder within the project directory).

## 3. PostgreSQL Server Configuration

### 3.1. `postgresql.conf`

Add or modify the following directives to enable SSL and client certificate verification.

```ini
# Enable SSL
ssl = on

# Server certificate and key
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'

# CA certificate used to verify client certificates
ssl_ca_file = 'ca.crt'

# Optional: Revocation list (if needed)
# ssl_crl_file = 'crl.pem'

# Restrict cipher suites to strong, modern algorithms
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on

# Minimum TLS version allowed
ssl_min_protocol_version = 'TLSv1.2'
```

After editing, restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 3.2. Host-Based Authentication (`pg_hba.conf`)

Configure `pg_hba.conf` to require SSL with client certificate authentication (`cert` method) for all remote connections.

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
# Remote connections: SSL + client certificate
hostssl all             all             0.0.0.0/0               cert
hostssl all             all             ::/0                    cert

# Local Unix socket connections may still use password or trust
local   all             all                                     scram-sha-256
```

**Important:** The `cert` method requires that the `CN` (Common Name) field of the client certificate matches the PostgreSQL database username. In our setup, we will use a consistent database user (e.g., `app_user`) and set the client certificate's `CN` to that same username.

Reload configuration:
```sql
SELECT pg_reload_conf();
```

## 4. Python/psycopg2 mTLS Connection Configuration

The `psycopg2` connection must provide the client certificate, client private key, and the CA certificate used to verify the server.

### 4.1. Connection Code with Client Certificate

```python
import psycopg2
import os

def get_db_connection():
    """Establishes a secure, mutually authenticated connection to PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", 5432),
            dbname=os.environ.get("DB_NAME", "hospital_management"),
            user=os.environ.get("DB_USER", "app_user"),
            # No password needed when using cert authentication
            sslmode="verify-full",
            sslrootcert=os.environ.get("DB_SSLROOTCERT", "./certs/ca.crt"),
            sslcert=os.environ.get("DB_SSLCERT", "./certs/client.crt"),
            sslkey=os.environ.get("DB_SSLKEY", "./certs/client.key")
        )
        # Test connection
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return conn
    except psycopg2.OperationalError as e:
        raise ConnectionError(f"Database connection failed: {e}")
```

### 4.2. Environment Variables / Configuration File

For security, the paths to certificate files and other connection parameters should be stored in environment variables or a protected configuration file.

```
# .env file example
DB_HOST=db.hospital.local
DB_PORT=5432
DB_NAME=hospital_management
DB_USER=app_user
DB_SSLROOTCERT=./certs/ca.crt
DB_SSLCERT=./certs/client.crt
DB_SSLKEY=./certs/client.key
```

**Security note:** The client private key (`client.key`) must have restrictive file permissions (`600` on Unix) to prevent unauthorized reading.

## 5. Client Certificate Management and Distribution

- **Unique certificates per user/installation:** Each deployment of the Tkinter application should have its own client certificate. This can be tied to the `staff_id` or the machine's unique identifier.
- **Revocation:** In case a client machine is compromised, its certificate should be revoked using a Certificate Revocation List (CRL) referenced in `ssl_crl_file`.
- **Rotation:** Certificates should have a limited validity (e.g., 365 days) and be renewed before expiration.

## 6. Troubleshooting mTLS Connections

| Symptom                                          | Likely Cause                                                                        | Resolution                                                                                               |
|:-------------------------------------------------|:------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------|
| `psycopg2.OperationalError: SSL error: certificate verify failed` | Server certificate not trusted by provided CA, or hostname mismatch.                 | Ensure `sslrootcert` points to the correct CA certificate and that server hostname matches `CN` in server cert. |
| `psycopg2.OperationalError: FATAL: certificate authentication failed for user "app_user"` | Client certificate `CN` does not match database username.                            | Re‑issue client certificate with `CN=app_user` (or the exact database user).                              |
| `psycopg2.OperationalError: SSL error: sslv3 alert bad certificate` | Client certificate is invalid, expired, or not signed by the CA trusted by the server. | Verify `ca.crt` on server is the same CA that signed the client certificate. Check certificate expiration. |
| Connection succeeds but performance is degraded   | SSL encryption overhead on localhost; using mTLS locally.                            | Use `hostnossl` for `local` entries in `pg_hba.conf` and connect via Unix socket.                         |

## 7. Compliance Notes

- **HIPAA Security Rule §164.312(e)(1):** Transmission security – mutual TLS provides strong encryption and mutual authentication of endpoints, exceeding the minimum requirement.
- **GDPR Article 32:** Security of processing – mTLS ensures that only authorized client applications can connect, reducing the risk of unauthorized access.

This configuration, when deployed with properly managed certificates, meets the stringent security expectations of modern healthcare IT environments. All production deployments must use this mTLS setup.