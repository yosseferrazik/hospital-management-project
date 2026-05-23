# 4. BD — Esquema de Seguretat

## Matriu de seguretat (RBAC)

Es van crear **5 rols de PostgreSQL** amb permisos granulars a nivell de taula i columna. Cada rol té un límit de connexions definit per evitar saturació del sistema:

| Rol                | Límit connexions | Permisos                                                                   |
| ------------------ | ---------------- | -------------------------------------------------------------------------- |
| `app_admin`        | 5                | Accés complet a tot                                                        |
| `app_doctor`       | 50               | CRUD a pacients, visites, prescripcions, cirurgies                         |
| `app_nurse`        | 100              | L/E en camps limitats de pacients, admissions a la seva planta             |
| `app_receptionist` | 10               | CRUD a pacients, programar visites                                         |
| `app_staff`        | 30               | Només lectura: nom del pacient + habitació (via vista `patient_directory`) |

**Implementació:** `scripts/sql/security.sql`

### SQL d'implementació RBAC

```sql
-- Creació de rols
CREATE ROLE app_admin LOGIN CONNECTION LIMIT 5;
CREATE ROLE app_doctor LOGIN CONNECTION LIMIT 50;
CREATE ROLE app_nurse LOGIN CONNECTION LIMIT 100;
CREATE ROLE app_receptionist LOGIN CONNECTION LIMIT 10;
CREATE ROLE app_staff LOGIN CONNECTION LIMIT 30;

-- Permisos per a app_admin (accés complet)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_admin;

-- Permisos per a app_doctor
GRANT SELECT, INSERT, UPDATE ON PATIENTS TO app_doctor;
GRANT SELECT, INSERT, UPDATE ON VISITS TO app_doctor;
GRANT SELECT, INSERT, UPDATE ON PRESCRIPTIONS TO app_doctor;
GRANT SELECT, INSERT, UPDATE ON SURGERIES TO app_doctor;
-- ... (permisos similars per a altres taules)

-- Permisos per a app_nurse (accés limitat en columnes)
GRANT SELECT (patient_id, first_name, last_name, birth_date,
              blood_type, allergies)
    ON PATIENTS TO app_nurse;
GRANT SELECT, INSERT, UPDATE ON ADMISSIONS TO app_nurse;

-- Permisos per a app_receptionist
GRANT SELECT, INSERT, UPDATE ON PATIENTS TO app_receptionist;
GRANT SELECT, INSERT, UPDATE ON SCHEDULED_APPOINTMENTS TO app_receptionist;

-- Permisos per a app_staff (només lectura via vista)
GRANT SELECT ON patient_directory TO app_staff;
```

## Row-Level Security (RLS)

RLS activat a les taules `PATIENTS` i `ADMISSIONS` per garantir que cada rol només vegi les dades que li corresponen:

- **Infermeres:** només veuen pacients ingressats a la seva planta
- **Metges i admins:** ho veuen tot
- **Personal general:** només nom i número d'habitació via vista restringida

Les variables de sessió (`app.current_user_id`, `app.current_staff_id`) s'estableixen al login mitjançant `SET_CONFIG` de PostgreSQL. Aquest mecanisme permet que les polítiques RLS sàpiguen qui és l'usuari actual en cada moment.

### Polítiques RLS

```sql
-- Activació de RLS
ALTER TABLE PATIENTS ENABLE ROW LEVEL SECURITY;
ALTER TABLE ADMISSIONS ENABLE ROW LEVEL SECURITY;

-- Política per a infermeres: només pacients de la seva planta
CREATE POLICY nurse_patients ON PATIENTS
    FOR SELECT
    USING (
        current_user = 'app_nurse' AND
        patient_id IN (
            SELECT a.patient_id
            FROM ADMISSIONS a
            JOIN ROOMS r ON a.room_id = r.room_id
            JOIN NURSING_STAFF ns ON ns.assigned_floor = r.floor_id
            JOIN APP_USERS u ON u.staff_id = ns.nursing_staff_id
            WHERE u.username = current_setting('app.current_user')
        )
    );

-- Política per a infermeres a ADMISSIONS
CREATE POLICY nurse_admissions ON ADMISSIONS
    FOR SELECT
    USING (
        current_user = 'app_nurse' AND
        room_id IN (
            SELECT r.room_id
            FROM ROOMS r
            JOIN NURSING_STAFF ns ON ns.assigned_floor = r.floor_id
            JOIN APP_USERS u ON u.staff_id = ns.nursing_staff_id
            WHERE u.username = current_setting('app.current_user')
        )
    );

-- Establir variables de sessió al login (en l'aplicació)
-- SELECT set_config('app.current_user', $1, false);
-- SELECT set_config('app.current_staff_id', $2::text, false);
```

## Configuració SSL

PostgreSQL configurat amb SSL utilitzant certificats autogenerats amb OpenSSL:

- Certificat amb validesa d'1 any
- Script de renovació: `scripts/ops/check_cert_expiry.sh`
- `pg_hba.conf` requereix `hostssl` per a totes les connexions remotes

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/security/2026-05-22-17-22-17-image.png)

### Generació del certificat

```bash
# A Briar (node primari)
mkdir -p /etc/ssl/postgresql
cd /etc/ssl/postgresql
openssl req -new -x509 -days 365 -nodes -out server.crt -keyout server.key
chmod 600 server.key
chown postgres:postgres server.key server.crt
```

Configuració a `postgresql.conf`:

```
ssl = on
ssl_cert_file = '/etc/ssl/postgresql/server.crt'
ssl_key_file = '/etc/ssl/postgresql/server.key'
```

### Configuració de `pg_hba.conf`

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     peer
host    all             all             127.0.0.1/32            scram-sha-256
hostssl all             all             10.147.17.0/24          scram-sha-256
hostssl all             all             100.64.0.0/10           scram-sha-256
host    all             all             0.0.0.0/0               reject
```

> Les connexions remotes (xarxa Tailscale `100.64.0.0/10` i xarxa local `10.147.17.0/24`) requereixen SSL. Les connexions locals per socket no.

## Data masking

Control d'accés a nivell de columna per restringir dades sensibles segons el rol de l'usuari:

| Rol              | Pot veure                                                           |
| ---------------- | ------------------------------------------------------------------- |
| Metges           | Totes les dades del pacient                                         |
| Infermeres       | Columnes limitades (telèfon, email, adreça, al·lèrgies — no el DNI) |
| Personal general | Només nom + habitació actual (via vista `patient_directory`)        |

### Vista patient_directory

```sql
CREATE VIEW patient_directory AS
SELECT
    p.patient_id,
    p.first_name || ' ' || p.last_name AS full_name,
    r.room_number,
    f.floor_name
FROM PATIENTS p
JOIN ADMISSIONS a ON p.patient_id = a.patient_id AND a.discharge_date IS NULL
JOIN ROOMS r ON a.room_id = r.room_id
JOIN FLOORS f ON r.floor_id = f.floor_id;
```

Per a producció real s'afegiria l'extensió `anon` de PostgreSQL per a dynamic masking.

> No implementat

## Auditoria via triggers

### Triggers d'auditoria

8 triggers de BD registren automàticament totes les operacions INSERT/UPDATE/DELETE a les taules sensibles (`PATIENTS`, `VISITS`, `PRESCRIPTIONS`, `ADMISSIONS`, `SURGERIES`, `RADIOLOGY_EXAMS`, `PHARMACY_DISPENSATIONS`, `SCHEDULED_APPOINTMENTS`) a la taula `AUDIT_LOGS`. Cada entrada registra: usuari, timestamp, tipus d'acció, taula, ID del registre, dades abans/després (JSON).

### Funció d'auditoria genèrica

```sql
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO AUDIT_LOGS (table_name, record_id, action, new_data, changed_by)
        VALUES (TG_TABLE_NAME, NEW.patient_id, 'INSERT',
                row_to_json(NEW)::jsonb,
                current_setting('app.current_user', true));
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO AUDIT_LOGS (table_name, record_id, action,
                                old_data, new_data, changed_by)
        VALUES (TG_TABLE_NAME, NEW.patient_id, 'UPDATE',
                row_to_json(OLD)::jsonb,
                row_to_json(NEW)::jsonb,
                current_setting('app.current_user', true));
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO AUDIT_LOGS (table_name, record_id, action,
                                old_data, changed_by)
        VALUES (TG_TABLE_NAME, OLD.patient_id, 'DELETE',
                row_to_json(OLD)::jsonb,
                current_setting('app.current_user', true));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Aplicació del trigger a PATIENTS

```sql
CREATE TRIGGER audit_patients
    AFTER INSERT OR UPDATE OR DELETE ON PATIENTS
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_func();
```

El patró es repeteix per a les 7 taules restants, canviant el nom del trigger i la columna d'identificació del registre (`record_id`) segons la PK de cada taula.

## Compliment AGPD

Document complet a `docs/02_database/agpd_compliance.md`. A continuació es resumeixen els punts principals.

### Categories de dades i risc

| Categoria             | Exemples                                    | Risc       |
| --------------------- | ------------------------------------------- | ---------- |
| Dades clíniques       | Diagnòstics, cirurgies, prescripcions       | **Crític** |
| Dades d'identitat     | DNI, nom, data naixement, targeta sanitària | **Alt**    |
| Dades de contacte     | Telèfon, email, adreça                      | Mig        |
| Dades laborals        | Registres de personal, llicències           | Mig        |
| Metadades d'auditoria | Accions d'usuari, timestamps, IPs           | Alt        |

### Mesures de seguretat aplicades

| Mesura                           | Implementació                                    |
| -------------------------------- | ------------------------------------------------ |
| Control d'accés (RBAC)           | 5 rols de BD amb permisos granulars              |
| Autenticació forta               | Contrasenyes hashejades amb bcrypt + JWT         |
| Xifrat en trànsit                | TLS configurat a PostgreSQL                      |
| Seguretat a nivell de fila (RLS) | Polítiques a PATIENTS i ADMISSIONS               |
| Minimització de dades            | Vista `patient_directory` per a `app_staff`      |
| Auditoria d'accessos             | 8 triggers automàtics a AUDIT_LOGS               |
| Còpies de seguretat xifrades     | Script diari amb retenció de 5 dies              |
| Aïllament de secrets             | Variables d'entorn, `.env` exclòs del repositori |

### Còpies de seguretat i xifrat

L'script de backup automàtic (`scripts/ops/backup.sh`) genera volcats comprimits i xifrats:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/postgres"
DB_NAME="hsp_db"
RETENTION_DAYS=5

pg_dump $DB_NAME | gzip > "$BACKUP_DIR/${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql.gz"

# Xifrat amb GPG (només per a backups enviats fora del node)
gpg --encrypt --recipient admin@hospital.cat \
    "$BACKUP_DIR/${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql.gz"

# Neteja de backups antics
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
```

### Registre d'auditoria

Taula `AUDIT_LOGS` amb estructura:

| Columna      | Tipus    | Descripció                                      |
| ------------ | -------- | ----------------------------------------------- |
| log_id       | BIGSERIAL| PK                                              |
| table_name   | VARCHAR  | Taula afectada (PATIENTS, VISITS, etc.)         |
| record_id    | INTEGER  | ID del registre afectat                         |
| action       | VARCHAR  | INSERT, UPDATE, DELETE                          |
| old_data     | JSONB    | Valors abans del canvi (NULL per INSERT)        |
| new_data     | JSONB    | Valors després del canvi (NULL per DELETE)      |
| changed_by   | VARCHAR  | Usuari que va realitzar l'acció                 |
| changed_at   | TIMESTAMP| Marca de temps de l'operació                    |

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/security/2026-05-22-17-23-17-image.png)

### Document AGPD

S'ha preparat un document complet per a l'Agència de Protecció de Dades:
`docs/02_database/agpd_compliance.md`

## Resum de compliment normatiu

| Requisit AGPD / LOPDGDD | Implementació                              |
| ----------------------- | ------------------------------------------ |
| Consentiment exprés     | Registre de nous usuaris amb acceptació    |
| Dret de supressió       | Funció `anonymize_patient()` que anonimitza dades |
| Notificació de bretxes  | Trigger d'auditoria + alerta per email     |
| Minimització de dades   | Vista `patient_directory` limita exposició |
| Retenció limitada       | Backup cíclic amb eliminació als 5 dies    |
| Seguretat tècnica       | RBAC + RLS + SSL + bcrypt + JWT            |

