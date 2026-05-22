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

## Row-Level Security (RLS)

RLS activat a les taules `PATIENTS` i `ADMISSIONS` per garantir que cada rol només vegi les dades que li corresponen:

- **Infermeres:** només veuen pacients ingressats a la seva planta
- **Metges i admins:** ho veuen tot
- **Personal general:** només nom i número d'habitació via vista restringida

Les variables de sessió (`app.current_user_id`, `app.current_staff_id`) s'estableixen al login mitjançant `SET_CONFIG` de PostgreSQL. Aquest mecanisme permet que les polítiques RLS sàpiguen qui és l'usuari actual en cada moment.

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

## Data masking

Control d'accés a nivell de columna per restringir dades sensibles segons el rol de l'usuari:

| Rol              | Pot veure                                                           |
| ---------------- | ------------------------------------------------------------------- |
| Metges           | Totes les dades del pacient                                         |
| Infermeres       | Columnes limitades (telèfon, email, adreça, al·lèrgies — no el DNI) |
| Personal general | Només nom + habitació actual (via vista `patient_directory`)        |

Per a producció real s'afegiria l'extensió `anon` de PostgreSQL per a dynamic masking.

> No implementat

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

### Registre d'auditoria

8 triggers de BD registren automàticament totes les operacions INSERT/UPDATE/DELETE a les taules sensibles (`PATIENTS`, `VISITS`, `PRESCRIPTIONS`, `ADMISSIONS`, `SURGERIES`, `RADIOLOGY_EXAMS`, `PHARMACY_DISPENSATIONS`, `SCHEDULED_APPOINTMENTS`) a la taula `AUDIT_LOGS`. Cada entrada registra: usuari, timestamp, tipus d'acció, taula, ID del registre, dades abans/després (JSON).

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/security/2026-05-22-17-23-17-image.png)

### Document AGPD

S'ha preparat un document complet per a l'Agència de Protecció de Dades:
`docs/02_database/agpd_compliance.md`
