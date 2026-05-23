<div style="text-align: center; padding-top: 120px; page-break-after: always;">
<p style="font-size: 14pt; color: #666;">Institut Sa Palomera · ASIX</p>
<h1 style="font-size: 32pt; color: #1a5276; border: none;">Hospital Management System</h1>
<h2 style="font-size: 18pt; color: #555; font-weight: normal;">Sistema de Gestió Hospitalària per a l'Hospital de Blanes</h2>
<hr style="width: 50%; margin: 30px auto; border: 1px solid #1a5276;">
<p style="font-size: 12pt;"><strong>Projecte Intermodular</strong></p>
<p style="font-size: 12pt;">Autor: <strong>Yossef Errazik</strong></p>
<p style="font-size: 12pt;">Curs: 2025–2026</p>
<p style="font-size: 12pt;">Data: Maig de 2026</p>
<p style="font-size: 12pt;">Repositori: <a href="https://github.com/yosseferrazik/hospital-management-project">github.com/yosseferrazik/hospital-management-project</a></p>
</div>

<div style="page-break-before: always;"></div>

# Índex de continguts

- **Part I: Resum Executiu / Executive Summary**
- **Part II: Lliuraments (Deliveries)**
  - [1. Planificació del Projecte i GitHub](#1-planificacio-del-projecte-i-github)
  - [2. PRG — Bloc de Connectivitat i Login](#2-prg--bloc-de-connectivitat-i-login)
  - [3. BD — Disseny ER i Model Relacional](#3-bd--disseny-er-i-model-relacional)
  - [4. BD — Esquema de Seguretat](#4-bd--esquema-de-seguretat)
  - [5. PRG — Bloc de Manteniment](#5-prg--bloc-de-manteniment)
  - [6. BD — Esquema d'Alta Disponibilitat](#6-bd--esquema-dalta-disponibilitat)
  - [7. PRG — Bloc de Consultes](#7-prg--bloc-de-consultes)
  - [8. BD — Dummy Data](#8-bd--dummy-data)
  - [9. PRG — Bloc d'Exportació de Dades](#9-prg--bloc-dexportacio-de-dades)
  - [10. Manual d'Instal·lació](#10-manual-dinstal-lacio)
  - [11. Manual d'Usuari](#11-manual-dusuari)
  - [12. Manual d'Administrador](#12-manual-dadministrador)
- **Part III: Technical Documentation**
- **Part IV: Final Summary**

---

# Part I: Resum Executiu / Executive Summary

## Visió General (CAT)

El **Hospital Management System** és un sistema de gestió hospitalària dissenyat per a l'Hospital de Blanes. Desenvolupat com a projecte intermodular del cicle ASIX a l'Institut Sa Palomera, el sistema cobreix la gestió completa de pacients, personal mèdic, visites, cirurgies, admissions, farmàcia i radiologia. Consta d'un backend Python/Flask amb PostgreSQL 16, un client d'escriptori Tkinter, un dashboard web Chart.js i un esquema d'alta disponibilitat amb replicació entre dos nodes (Briar i Sion).

## Project Overview (ENG)

The **Hospital Management System** is a hospital management solution designed for Hospital de Blanes. Developed as a cross-module project for the ASIX program at Institut Sa Palomera, the system covers full management of patients, medical staff, visits, surgeries, admissions, pharmacy, and radiology. It consists of a Python/Flask backend with PostgreSQL 16, a Tkinter desktop client, a Chart.js web dashboard, and a high-availability setup with replication across two nodes (Briar and Sion).

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HOSPITAL LAN (192.168.4.0/24)                │
│                                                                     │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────────┐   │
│  │  Doctor   │  │ Reception │  │   Nurse   │  │  Admin Laptop  │   │
│  │  (Tkinter)│  │ (Tkinter) │  │ (Tkinter) │  │  (Tailscale)   │   │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └───────┬────────┘   │
│        └──────────────┼──────────────┼─────────────────┘            │
│                       │              │                               │
│              ┌────────▼──────────────▼──────────────┐               │
│              │         BRIAR (Primary)              │               │
│              │  Flask API + PostgreSQL 16           │               │
│              │  192.168.4.254  |  100.78.155.2      │               │
│              └───────────────────┬──────────────────┘               │
└──────────────────────────────────┼───────────────────────────────────┘
                                   │ Tailscale VPN 
                          ┌────────▼────────┐
                          │  SION (AWS EC2)  │
                          │  PostgreSQL 16   │
                          │  STANDBY         │
                          │  100.98.214.53   │
                          └─────────────────┘
```

## Technology Stack

| Layer            | Technology                  | Purpose                                  |
| ---------------- | --------------------------- | ---------------------------------------- |
| Backend          | Python 3.12 + Flask 3.1     | REST API and business logic              |
| Database         | PostgreSQL 16               | Relational data with Cyrillic/SSL/rep    |
| ORM              | SQLAlchemy 2.0              | SQL injection prevention, abstraction    |
| Client           | Tkinter                     | Desktop GUI (included with Python)       |
| Dashboard        | Chart.js                    | Real-time web charts (free alternative)  |
| Authentication   | JWT + bcrypt                | Stateless auth with hashed passwords     |
| VPN              | Tailscale                   | Secure node interconnectivity            |
| PDF Generation   | fpdf2                       | On-demand report PDF export              |
| Validation       | jsonschema + lxml           | XSD and JSON Schema validation           |

## Node Overview

| Node      | Location              | LAN IP        | Tailscale IP  | Role                               |
| --------- | --------------------- | ------------- | ------------- | ---------------------------------- |
| **Briar** | Hospital server room  | 192.168.4.254 | 100.78.155.2  | Flask API + PostgreSQL PRIMARY     |
| **Sion**  | AWS EC2 (eu-west-3)   | —             | 100.98.214.53 | PostgreSQL STANDBY (disaster rec.) |

## C4 Context Diagram

![C4 Context Diagram](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/C4_Context_Diagram.drawio.png)

<div style="page-break-before: always;"></div>

# Part II: Lliuraments (Deliveries)

## 1. Planificació del Projecte i GitHub

### Resum

Projecte individual desenvolupat per Yossef Errazik amb un total de **91 hores reals** (77 hores estimades, desviació +18.2%). S'ha seguit un enfocament de desenvolupament continu a la branca `main` amb commits atòmics seguint la convenció **Conventional Commits**.

### Tasques principals

| Tasca                       | Hores est. | Hores reals | Desviació |
| --------------------------- | ---------- | ----------- | --------- |
| Planificació                | 4          | 5           | +1h       |
| Connectivitat i login       | 6          | 7           | +1h       |
| ER - Model Relacional       | 5          | 6           | +1h       |
| Esquema de seguretat        | 8          | 9           | +1h       |
| Bloc de manteniment         | 10         | 12          | +2h       |
| Alta disponibilitat         | 10         | 14          | +4h       |
| Bloc de consultes           | 8          | 8           | 0h        |
| Dummy Data                  | 6          | 7           | +1h       |
| Exportació de dades         | 8          | 10          | +2h       |
| Documentació i manuals      | 12         | 13          | +1h       |

### Tecnologies escollides

Les tecnologies es van seleccionar per criteris de cost zero, coneixements previs i requisits tècnics: Python/Flask per al backend, PostgreSQL 16 per la base de dades (suport ciríl·lic, SSL, replicació), SQLAlchemy com a ORM, Tkinter pel client d'escriptori, Chart.js per al dashboard, JWT + bcrypt per a autenticació i Tailscale per a la xarxa privada entre nodes.

### Convenció de commits

| Tipus     | Ús                     |
| --------- | ---------------------- |
| `feat:`   | Nova funcionalitat     |
| `fix:`    | Correcció d'error      |
| `docs:`   | Documentació           |
| `refactor:` | Canvi intern         |
| `test:`   | Tests                  |
| `db:`     | Migracions d'esquema   |

> **Lliçons apreses:** Les desviacions es concentren en tasques amb tecnologies no cobertes a classe (Tailscale, replicació, Chart.js). Per a futures planificacions caldria augmentar el marge de contingència en aquestes àrees.

> 📄 Document complet: [01_planning_and_github.md](./01_planning_and_github.md)

<div style="page-break-before: always;"></div>

## 2. PRG — Bloc de Connectivitat i Login

### Resum

Mòdul d'autenticació basat en JWT amb contrasenyes hashejades amb bcrypt. L'aplicació es connecta a PostgreSQL 16 via psycopg2-binary + SQLAlchemy 2.0 amb connection pooling.

### Connection Pooling

| Paràmetre      | Valor | Descripció                                     |
| -------------- | ----- | ---------------------------------------------- |
| `pool_size`    | 5     | Connexions mantingudes obertes                 |
| `max_overflow` | 10    | Connexions addicionals sota demanda            |
| `pool_timeout` | 30    | Temps d'espera màxim (s)                       |
| `pool_recycle` | 1800  | Temps màxim de vida d'una connexió (s)         |
| `pool_pre_ping`| True  | Verifica salut de la connexió abans d'usar-la  |

### Flux d'autenticació

1. L'usuari introdueix credencials al client Tkinter
2. Petició `POST /api/auth/login`
3. El servidor valida contra `APP_USERS` (bcrypt)
4. Retorna JWT token amb `role` i `staff_id`
5. El client emmagatzema el token en un singleton de sessió
6. Peticions posteriors inclouen `Authorization: Bearer <token>`

### Estructura del JWT

```json
{
  "sub": "admin",
  "role": "ADMIN",
  "staff_id": 1,
  "iat": 1716388800,
  "exp": 1716475200,
  "type": "access"
}
```

### Endpoints d'autenticació

| Mètode | Endpoint                        | Autenticació | Descripció                          |
| ------ | ------------------------------- | ------------ | ----------------------------------- |
| POST   | `/api/auth/login`               | No           | Inici de sessió                     |
| POST   | `/api/auth/register`            | No           | Crear nou usuari                    |
| GET    | `/api/auth/users`               | JWT          | Llistar usuaris                     |
| PUT    | `/api/auth/change-password`     | JWT          | Canviar pròpia contrasenya          |
| PUT    | `/api/auth/users/<id>/password` | JWT+ADMIN    | Resetear contrasenya d'un altre usuari |

### Singleton de sessió (client)

```python
class SessionManager:
    _instance = None
    _token = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def login(self, token, user, role, staff_id):
        self._token = token
        self._user = user
        self._role = role
        self._staff_id = staff_id

    @property
    def auth_header(self):
        return {"Authorization": f"Bearer {self._token}"}
```

### Seguretat aplicada

| Mesura                   | Implementació                                           |
| ------------------------ | ------------------------------------------------------- |
| Hashing de contrasenyes  | bcrypt — `hashpw()` + `checkpw()` (work factor 12)      |
| Tokens JWT               | Flask-JWT-Extended 4.7.1 — clau de 256 bits             |
| Secrets en fitxer extern | `/etc/hms.env` — exclòs del repositori (permisos 600)   |
| Rols                     | ADMIN, DOCTOR, NURSE, STAFF, RECEPTIONIST               |

> 📄 Document complet: [02_prg_connectivity_login.md](./02_prg_connectivity_login.md)

<div style="page-break-before: always;"></div>

## 3. BD — Disseny ER i Model Relacional

### Resum

Base de dades amb **24 taules** que cobreixen pacients, personal mèdic, visites, cirurgies, admissions, farmàcia, radiologia, auditoria i generació de dades de prova. El disseny segueix els principis de normalització (3FN).

### Model Relacional (entitats principals)

```
STAFF ──┬── MEDICAL_STAFF ──┬── MEDICAL_STAFF_SPECIALTIES
        │                   └── MEDICAL_SPECIALTIES
        ├── NURSING_STAFF ──┬── FLOORS (assigned_floor)
        │                   └── MEDICAL_STAFF (assigned_doctor)
        └── GENERAL_STAFF

PATIENTS ──┬── VISITS ──┬── PRESCRIPTIONS ── MEDICATIONS
           │            └── SCHEDULED_APPOINTMENTS
           ├── ADMISSIONS ──┬── ROOMS ── FLOORS
           │                └── PHARMACY_DISPENSATIONS ── DISPENSATION_ITEMS
           ├── SURGERIES ──┬── OPERATING_THEATERS ── MEDICAL_DEVICES
           │               └── SURGERY_ASSISTANTS
           └── RADIOLOGY_EXAMS
```

### Patrons de disseny

| Patró                | Exemple                                                  |
| -------------------- | -------------------------------------------------------- |
| Base + subtipus      | `STAFF` → `MEDICAL_STAFF`, `NURSING_STAFF`, `GENERAL_STAFF` |
| Taula de junció      | `MEDICAL_STAFF_SPECIALTIES`, `SURGERY_ASSISTANTS`        |
| Taula d'auditoria    | `AUDIT_LOGS` amb valors abans/després                    |
| Capçalera-detall     | `PHARMACY_DISPENSATIONS` → `DISPENSATION_ITEMS`          |

### Normalització (3FN)

| Forma Normal | Compliment | Justificació                                                   |
| ------------ | ---------- | -------------------------------------------------------------- |
| **1FN**      | ✓          | Totes les columnes són atòmiques; no hi ha grups repetits      |
| **2FN**      | ✓          | Cada columna no clau depèn completament de la PK               |
| **3FN**      | ✓          | No hi ha dependències transitives                              |

### Exemple SQL: Consulta de pacients ingressats

```sql
SELECT p.patient_id, p.first_name, p.last_name,
       r.room_number, f.floor_name, a.admission_date
FROM ADMISSIONS a
JOIN PATIENTS p ON a.patient_id = p.patient_id
JOIN ROOMS r ON a.room_id = r.room_id
JOIN FLOORS f ON r.floor_id = f.floor_id
WHERE a.discharge_date IS NULL
ORDER BY a.admission_date;
```

### Indexació

| Índex                          | Taula            | Justificació                          |
| ------------------------------ | ---------------- | ------------------------------------- |
| `idx_patients_national_id`     | PATIENTS         | Cerca per DNI                         |
| `idx_visits_patient`           | VISITS           | Historial de visites d'un pacient     |
| `idx_admissions_active`        | ADMISSIONS       | Pacients actualment ingressats        |
| `idx_audit_logs_timestamp`     | AUDIT_LOGS       | Auditoria cronològica                 |

> 📄 Document complet: [03_bd_er_relational_model.md](./03_bd_er_relational_model.md)

<div style="page-break-before: always;"></div>

## 4. BD — Esquema de Seguretat

### Resum

Implementació de seguretat amb 5 rols PostgreSQL (RBAC), Row-Level Security (RLS), SSL amb certificats, data masking, triggers d'auditoria i compliment AGPD.

### Matriu de rols (RBAC)

| Rol                | Lím. con. | Permisos                                                         |
| ------------------ | --------- | ---------------------------------------------------------------- |
| `app_admin`        | 5         | Accés complet a tot                                              |
| `app_doctor`       | 50        | CRUD a pacients, visites, prescripcions, cirurgies               |
| `app_nurse`        | 100       | L/E en camps limitats de pacients, admissions a la seva planta   |
| `app_receptionist` | 10        | CRUD a pacients, programar visites                               |
| `app_staff`        | 30        | Només lectura: nom pacient + habitació (via vista)               |

### Row-Level Security

```sql
ALTER TABLE PATIENTS ENABLE ROW LEVEL SECURITY;

CREATE POLICY nurse_patients ON PATIENTS
    FOR SELECT
    USING (
        current_user = 'app_nurse' AND
        patient_id IN (
            SELECT a.patient_id FROM ADMISSIONS a
            JOIN ROOMS r ON a.room_id = r.room_id
            JOIN NURSING_STAFF ns ON ns.assigned_floor = r.floor_id
            JOIN APP_USERS u ON u.staff_id = ns.nursing_staff_id
            WHERE u.username = current_setting('app.current_user')
        )
    );
```

### SSL Configuration

PostgreSQL configurat amb certificats OpenSSL. `pg_hba.conf` requereix `hostssl` per a totes les connexions remotes:

```
hostssl all all 10.147.17.0/24    scram-sha-256
hostssl all all 100.64.0.0/10     scram-sha-256
host    all all 0.0.0.0/0         reject
```

### Data Masking

| Rol              | Pot veure                                                        |
| ---------------- | ---------------------------------------------------------------- |
| Metges           | Totes les dades del pacient                                      |
| Infermeres       | Columnes limitades (no DNI)                                      |
| Personal general | Només nom + habitació (via vista `patient_directory`)            |

### Auditoria via triggers

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
    -- UPDATE i DELETE similars...
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Compliment AGPD

| Requisit AGPD / LOPDGDD    | Implementació                               |
| -------------------------- | ------------------------------------------- |
| Consentiment exprés        | Registre amb acceptació                     |
| Dret de supressió          | Funció `anonymize_patient()`                |
| Minimització de dades      | Vista `patient_directory` limita exposició  |
| Retenció limitada          | Backup cíclic amb eliminació als 5 dies     |
| Seguretat tècnica          | RBAC + RLS + SSL + bcrypt + JWT             |

> 📄 Document complet: [04_bd_security_scheme.md](./04_bd_security_scheme.md)

<div style="page-break-before: always;"></div>

## 5. PRG — Bloc de Manteniment

### Resum

Operacions CRUD completes per a personal mèdic, pacients, visites i cirurgies. Implementació de 5 funcions/triggers PL/pgSQL per garantir la integritat de les dades.

### Endpoints CRUD principals

| Tasca                            | Mètode | Endpoint API                                  |
| -------------------------------- | ------ | --------------------------------------------- |
| Alta personal mèdic              | POST   | `/api/maintenance/staff/medical`              |
| Alta personal d'infermeria       | POST   | `/api/maintenance/staff/nursing`              |
| Alta personal general            | POST   | `/api/maintenance/staff/general`              |
| Alta nous pacients               | POST   | `/api/maintenance/patients`                   |
| Assignar infermer a metge/planta | PUT    | `/api/maintenance/nursing/assign`             |
| Modificar personal               | PUT    | `/api/maintenance/staff/{id}`                 |
| Eliminar personal                | DELETE | `/api/maintenance/staff/{id}`                 |

### Exemple: Creació de pacient

```python
class PatientCreate(Schema):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=200)
    date_of_birth: date
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-]{6,20}$')
    email: Optional[str] = Field(None, pattern=r'^[\w\.\-]+@[\w\-]+\.\w+$')

@router.post("/api/maintenance/patients")
def create_patient(data: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return {"id": patient.id, "message": "Pacient creat correctament"}
```

### PL/pgSQL: Trigger anti-solapament de quiròfans

```sql
CREATE OR REPLACE FUNCTION check_surgery_overlap()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM SURGERIES
        WHERE theater_id = NEW.theater_id
          AND surgery_date = NEW.surgery_date
          AND id <> COALESCE(NEW.id, -1)
          AND (
            (NEW.start_time BETWEEN start_time AND end_time)
            OR (NEW.end_time BETWEEN start_time AND end_time)
            OR (start_time BETWEEN NEW.start_time AND NEW.end_time)
          )
    ) THEN
        RAISE EXCEPTION 'El quiròfan % ja està reservat per a % entre % i %',
            NEW.theater_id, NEW.surgery_date, NEW.start_time, NEW.end_time;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Funcionalitats implementades

- ✅ Alta de personal (metge/ssa, infermer/a, administratiu)
- ✅ Alta de nous pacients
- ✅ Assignació d'infermeres a metge o planta
- ✅ Consulta d'operacions per quiròfan en un dia
- ✅ Consulta de visites planificades per dia
- ✅ Historial complet de pacient (visites, diagnòstics, medicaments, ingressos, quiròfan)
- ✅ Dispositius mèdics per quiròfan

> 📄 Document complet: [05_prg_maintenance.md](./05_prg_maintenance.md)

<div style="page-break-before: always;"></div>

## 6. BD — Esquema d'Alta Disponibilitat

### Resum

Arquitectura de dos nodes amb replicació *streaming* asíncrona de PostgreSQL, LVM per a snapshots i backups, sistema de backup de 3 capes, i procediment de failover documentat.

### Nodes

| Node      | CPU                | RAM   | Disc                  | IP LAN        | Tailscale IP  |
| --------- | ------------------ | ----- | --------------------- | ------------- | ------------- |
| **Briar** | Xeon E-2336 (6C)   | 16 GB | NVMe 240GB + SSD 480GB | 192.168.4.254 | 100.78.155.2  |
| **Sion**  | AWS t3.medium (2vCPU) | 4 GB | 100 GB gp3 EBS        | —             | 100.98.214.53 |

### Partions LVM (Briar)

```
Disc 2 — /dev/sdb (480 GB SATA SSD)
└── vg_postgres
    ├── lv_pgdata    350 GB   /var/lib/postgresql/16/main
    └── lv_pgwal      80 GB   /var/lib/postgresql/16/wal
    (25 GB reserva per a snapshots LVM)
```

### Topologia de replicació

```
BRIAR (PRIMARY) ──── WAL streaming ────► SION (STANDBY read-only)
     │                                        │
  LAN: 192.168.4.254                     AWS EC2 (eu-west-3)
  TS:  100.78.155.2                     TS:  100.98.214.53
```

### Configuració del primari (postgresql.conf)

```ini
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1024
max_replication_slots = 2
hot_standby = on
shared_buffers = 4GB
effective_cache_size = 8GB
```

### Script de backup (3 capes)

```python
def backup_physical(tag=""):
    """Backup físic consistent amb pg_basebackup."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"physical_{tag}{ts}.tar.gz"
    subprocess.run(["pg_basebackup", "-D", "-", "-Ft", "-z", "-P", "-X", "fetch"],
                   stdout=open(os.path.join(BACKUP_DIR, filename), "wb"), check=True)
    return filename

def backup_logical(tag=""):
    """Dump lògic del schema complet."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hsp_db_{tag}{ts}.dump"
    subprocess.run(["pg_dump", "--format=custom", "--compress=9",
                    "--dbname=hospital_db", f"--file={os.path.join(BACKUP_DIR, filename)}"], check=True)
    return filename
```

### Programació de backups (cron)

```
0 2 * * *     Backup complet (lògic + config) diari
0 3 * * *     Backup físic PGDATA diari
*/15 * * * *  Backup lògic freqüent (RPO de 15 minuts)
```

### Failover

```bash
# Promocionar Sion a primari
sudo -u postgres pg_ctl promote -D /var/lib/postgresql/16/main
```

### Verificació

| Test              | Comanda                                                  |
| ----------------- | -------------------------------------------------------- |
| API funciona      | `curl http://192.168.4.254:5000/health`                  |
| Replicació activa | `psql -c "SELECT state FROM pg_stat_replication;"`       |
| Lag de replicació | `psql -c "SELECT now() - pg_last_xact_replay_timestamp() AS lag;"` |

> 📄 Document complet: [06_bd_high_availability.md](./06_bd_high_availability.md)

<div style="page-break-before: always;"></div>

## 7. PRG — Bloc de Consultes

### Resum

Sistema d'informes obligatoris, opcionals i top accessibles des del client d'escriptori i via API REST. Inclou dashboard amb estadístiques en temps real i exportació PDF.

### Informes obligatoris

| Informe            | Endpoint API                                      | Descripció                                 |
| ------------------ | ------------------------------------------------- | ------------------------------------------ |
| Dades d'una planta | `GET /api/reports/summary?floor_id=X`             | Habitacions, quiròfans i infermeres        |
| Tot el personal    | `GET /api/reports/summary?report=staff`           | Llistat complet de treballadors            |
| Visites per dia    | `GET /api/reports/visits?start_date=X&end_date=Y` | Nombre de visites ateses per dia           |

### SQL: Visites per dia

```sql
SELECT
    DATE(v.visit_date) AS day,
    COUNT(*) AS total_visits,
    COUNT(DISTINCT v.patient_id) AS unique_patients,
    COUNT(DISTINCT v.doctor_id) AS active_doctors
FROM VISITS v
WHERE v.visit_date BETWEEN :start_date AND :end_date
GROUP BY DATE(v.visit_date)
ORDER BY day;
```

### Informe opcional: Ranking de metges

```sql
SELECT ms.id, CONCAT(ms.first_name, ' ', ms.last_name) AS doctor_name,
       ms.specialty, COUNT(v.id) AS total_visits,
       RANK() OVER (ORDER BY COUNT(v.id) DESC) AS ranking
FROM MEDICAL_STAFF ms
LEFT JOIN VISITS v ON v.doctor_id = ms.id
    AND v.visit_date BETWEEN :start_date AND :end_date
GROUP BY ms.id
ORDER BY total_visits DESC LIMIT 10;
```

### Informe top: Malalties més comunes

```json
{
  "diseases": [
    { "diagnosis": "Hipertensió arterial", "occurrences": 215, "percentage": 8.24 },
    { "diagnosis": "Infecció respiratòria aguda", "occurrences": 198, "percentage": 7.59 },
    { "diagnosis": "Diabetes tipus 2", "occurrences": 167, "percentage": 6.40 }
  ]
}
```

### Reports complets via API

| Report      | Endpoint                       | Filtres                                          |
| ----------- | ------------------------------ | ------------------------------------------------ |
| Summary     | `GET /api/reports/summary`     | start_date, end_date                             |
| Visites     | `GET /api/reports/visits`      | start_date, end_date, specialty, doctor_id       |
| Cirurgies   | `GET /api/reports/surgeries`   | start_date, end_date, procedure_type, surgeon_id |
| Admissions  | `GET /api/reports/admissions`  | start_date, end_date, floor_id                   |

### Dashboard API

`GET /api/dashboard/stats` retorna: visites avui, cirurgies avui, admissions actives, totals de pacients/personal, visites per especialitat, tendència 7 dies, top 5 metges.

### Exportació PDF (fpdf2)

```python
class HospitalPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Hospital de Blanes - Informe de Sumari", ln=True, align="C")

@app.get("/api/reports/summary/pdf")
def generate_summary_pdf(db: Session = Depends(get_db), user=Depends(get_current_user)):
    pdf = HospitalPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    # ... dades ...
    return Response(pdf.output(dest="S").encode("latin-1"), media_type="application/pdf")
```

> 📄 Document complet: [07_prg_queries.md](./07_prg_queries.md)

<div style="page-break-before: always;"></div>

## 8. BD — Dummy Data

### Resum

Generació de ~325.000 registres de prova amb Faker (locale `es_ES` i `ru_RU`), optimitzada de 20 minuts a ~5 minuts mitjançant insercions per lots i SQL directe.

### Volums de dades

| Entitat          | Registres  | Mida estimada |
| ---------------- | ---------- | ------------- |
| Pacients         | 50.000     | ~25 MB        |
| Visites          | 100.000    | ~80 MB        |
| Metges           | 100        | ~80 KB        |
| Infermeres       | 200        | ~120 KB       |
| Cirurgies        | 25.000     | ~45 MB        |
| Admissions       | 25.000     | ~40 MB        |
| Prescripcions    | 80.000     | ~35 MB        |

### Implementació amb Faker

```python
fake_es = Faker('es_ES')
fake_ru = Faker('ru_RU')   # 5% en ciríl·lic

def generate_patients(count: int, batch_size: int = 20, commit_every: int = 400):
    patients = []
    for i in range(1, count + 1):
        faker = fake_ru if i % 20 == 0 else fake_es
        patient = Patient(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            date_of_birth=faker.date_of_birth(minimum_age=0, maximum_age=95),
            phone=faker.phone_number(),
            email=faker.email(),
            address=faker.address().replace('\n', ', ')
        )
        db.add(patient)
        patients.append(patient)
        if i % batch_size == 0:
            db.flush()
        if i % commit_every == 0:
            db.commit()
    db.commit()
    return patients
```

### Dades en ciríl·lic

5% dels pacients amb noms en alfabet ciríl·lic (Faker locale `ru_RU`):

| Locale   | First Name     | Last Name       | Alfabet   |
| -------- | -------------- | --------------- | --------- |
| `es_ES`  | María          | García López    | Llatí     |
| `ru_RU`  | Екатерина      | Иванова         | Ciríl·lic |
| `ru_RU`  | Дмитрий        | Соколов         | Ciríl·lic |

### Optimització de rendiment

| Tècnica                    | Millora |
| -------------------------- | ------- |
| Insercions per lots        | ~3x     |
| Pools de diagnòstics       | ~2x     |
| Batch insert amb SQL       | ~2x     |
| Desactivar índexs          | ~1.5x   |

### Neteja

Taula `DUMMY_REGISTRY` rastreja tots els registres generats. L'opció **Cleanup dummy data** elimina en ordre invers de dependències.

> 📄 Document complet: [08_bd_dummy_data.md](./08_bd_dummy_data.md)

<div style="page-break-before: always;"></div>

## 9. PRG — Bloc d'Exportació de Dades

### Resum

Exportació de visites en XML/JSON amb validació XSD/JSON Schema, enviament automàtic a l'API de la Seguretat Social, i dashboard web amb Chart.js.

### Endpoints d'exportació

```bash
# Exportació XML
GET /api/export/visits?start_date=2026-05-01&end_date=2026-05-20&format=xml

# Exportació JSON
GET /api/export/visits?start_date=2026-05-01&end_date=2026-05-20&format=json
```

### Exemple de sortida XML

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<visits>
    <visit>
        <visit_id>1</visit_id>
        <visit_date>2026-05-15</visit_date>
        <doctor>
            <name>Dr. Martínez</name>
            <license_number>12345</license_number>
        </doctor>
        <patient>
            <dni>12345678A</dni>
            <first_name>Joan</first_name>
            <last_name>Garcia</last_name>
            <health_card>CAT123456789</health_card>
        </patient>
    </visit>
</visits>
```

### Validació XSD i JSON Schema

```python
def validate_xml(xml_string: str, xsd_path: str) -> bool:
    xsd_doc = etree.parse(xsd_path)
    xsd_schema = etree.XMLSchema(xsd_doc)
    xml_doc = etree.fromstring(xml_string.encode("utf-8"))
    return xsd_schema.validate(xml_doc)

def validate_json(json_string: str, schema_path: str) -> bool:
    with open(schema_path) as f:
        schema = json.load(f)
    data = json.loads(json_string)
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False
```

### API Seguretat Social

Enviament automàtic a API externa amb autenticació Basic Auth:

```python
def send_to_external_api(export_data: str, file_format: str) -> dict:
    url = os.getenv("EXTERNAL_API_URL")
    auth = HTTPBasicAuth(os.getenv("EXTERNAL_API_USERNAME"), os.getenv("EXTERNAL_API_PASSWORD"))
    response = requests.post(url, data=export_data,
        headers={"Content-Type": f"application/{file_format}"},
        auth=auth, timeout=30)
    return {"status_code": response.status_code, "success": response.ok}
```

### Dashboard Chart.js

| Gràfic                   | Tipus       | Dades                     |
| ------------------------ | ----------- | ------------------------- |
| Visites avui             | Mètrica     | `visits_today`            |
| Cirurgies avui           | Mètrica     | `surgeries_today`         |
| Visites per especialitat | Barres      | `by_specialty`            |
| Tendència 7 dies         | Línies      | `visits_trend`            |
| Top 5 metges             | Barres hor. | `top_doctors`             |

### Connectivitat PowerBI

URL per a PowerBI Desktop: `http://192.168.4.254:5000/api/dashboard/stats`

> 📄 Document complet: [09_prg_export.md](./09_prg_export.md)

<div style="page-break-before: always;"></div>

## 10. Manual d'Instal·lació

### Resum

Guia completa d'instal·lació pas a pas: des de la instal·lació d'Ubuntu Server 24.04 en ambdós nodes fins a la configuració de Tailscale, PostgreSQL 16 amb replicació, SSL, firewall, desplegament de l'API com a servei systemd, client d'escriptori, backups automatitzats i procediments de failover.

### Prerequisits

- Dos servidors Ubuntu 24.04 LTS (Briar i Sion) amb accés root
- Compte de Tailscale per a la xarxa mesh VPN
- Python 3.12, PostgreSQL 16, Git

### Passos principals

1. Instal·lació d'Ubuntu Server 24.04 amb LVM
2. Configuració de Tailscale entre nodes
3. Configuració del firewall (UFW)
4. Instal·lació de PostgreSQL 16
5. Generació de certificats TLS
6. Configuració de replicació primari-standby
7. Clonació del repositori i entorn Python
8. Variables d'entorn (`/etc/hms.env`)
9. Creació de la BD i càrrega d'esquemes
10. Servei systemd per a l'API
11. Client d'escriptori Tkinter
12. Backups automatitzats amb cron
13. Procediment de failover

### Credencials per defecte

| Username | Password                  |
| -------- | ------------------------- |
| `yossef` | `ChangeMePleaseChange!`   |

### Systemd unit

```ini
[Unit]
Description=Hospital Management System API
After=network.target postgresql-16.service
Requires=postgresql-16.service

[Service]
Type=simple
WorkingDirectory=/opt/hms/current/server/src
EnvironmentFile=/opt/hms/current/server/src/.env
ExecStart=/opt/hms/current/server/src/.venv/bin/python run.py
Restart=always
RestartSec=5
```

### Verificació

```bash
curl http://192.168.4.254:5000/health
# {"status":"healthy","database":"connected","timestamp":"..."}
```

> 📄 Document complet: [10_installation_manual.md](./10_installation_manual.md)

<div style="page-break-before: always;"></div>

## 11. Manual d'Usuari

### Resum

Guia d'ús de l'aplicació d'escriptori: login, dashboard, manteniment de personal i pacients, Data Workspace, informes operatius i estadístiques, generació de dades de prova, i gestió de contrasenya.

### Seccions de l'aplicació

| Secció                | Descripció                                         |
| --------------------- | -------------------------------------------------- |
| Dashboard             | Resum de l'activitat hospitalària del dia          |
| Maintenance           | Alta i gestió de personal i pacients               |
| Data Workspace        | Navegació i edició directa de totes les taules     |
| Operational Reports   | Visites i cirurgies programades per data           |
| Statistics            | Visió analítica: planta, personal, rankings        |
| Advanced Reports      | Visor multi-pestanya amb filtres i exportació PDF  |
| Dummy Data            | Generació de dades de prova                        |
| User Management       | Gestió d'usuaris (només ADMIN)                     |
| Audit Logs            | Registre d'auditoria (només ADMIN)                 |

### Tasques comunes

**Donar d'alta un pacient:**
1. Maintenance → Add Patient
2. Omplir DNI, nom, cognoms, data naixement, gènere
3. Afegir telèfon, adreça, email
4. Seleccionar grup sanguini i al·lèrgies
5. Save

**Programar una visita:**
1. Data Workspace → Visits → Add
2. Seleccionar pacient, metge, data i motiu
3. Save

**Generar informe mensual:**
1. Advanced Reports → Visit Summary + Surgery Log
2. Seleccionar rang de dates
3. Generate → Export PDF

> 📄 Document complet: [11_user_manual.md](./11_user_manual.md)

<div style="page-break-before: always;"></div>

## 12. Manual d'Administrador

### Resum

Guia per a administradors del sistema: gestió d'usuaris i rols, revisió de logs d'auditoria, backups i restauració, monitorització, checklists de manteniment i millors pràctiques de seguretat.

### Matriu de rols

| Rol             | Pacients | Visites | Cirurgies | Admissions | Reports | User Mgmt |
| --------------- | -------- | ------- | --------- | ---------- | ------- | --------- |
| **ADMIN**       | CRUD     | CRUD    | CRUD      | CRUD       | View    | Full      |
| **DOCTOR**      | CRUD     | CRUD    | CRUD      | View       | View    | —         |
| **NURSE**       | View/Edit| View    | Assist    | Manage     | View    | —         |
| **RECEPTIONIST**| Create   | Create  | —         | —          | —       | —         |
| **STAFF**       | Read-only (nom + habitació) | — | — | — | — | — |

### Procediments d'usuari

- **Crear usuari:** User Management → Create User → username, password, staff_id, role
- **Desactivar compte:** Toggle Active (preserva audit trail)
- **Reset password:** El sistema obliga a canviar-la al proper login

### Auditoria

| Camp         | Descripció                              |
| ------------ | --------------------------------------- |
| Timestamp    | Data i hora de l'acció                  |
| User         | Usuari que va realitzar l'acció         |
| Action       | INSERT / UPDATE / DELETE                |
| Old Values   | Valors previs (JSONB)                   |
| New Values   | Valors nous (JSONB)                     |

### Retenció de logs d'auditoria

| Període     | Emmagatzematge    | Acció                         |
| ----------- | ----------------- | ----------------------------- |
| 0–2 anys    | BD (actiu)        | Disponible al UI              |
| 2–7 anys    | Arxiu comprimit   | Exportat a `/backups/audit/`  |
| 7+ anys     | Eliminat          | Purgat després de retenció legal |

### Backups

| Capa        | RPO       | RTO       |
| ----------- | --------- | --------- |
| Física      | 24 hores  | 30 min    |
| Lògica      | 15 minuts | 15–60 min |
| Configuració| 24 hores  | 5 min     |

### Llindars de monitorització

| Mètrica             | Warning     | Critical    |
| ------------------- | ----------- | ----------- |
| Replication lag     | > 10 MB     | > 100 MB    |
| Disk usage          | > 80%       | > 95%       |
| SSL certificate     | < 30 dies   | < 7 dies    |
| Failed backups      | 1 failure   | 3 consec.   |

> 📄 Document complet: [12_administrator_manual.md](./12_administrator_manual.md)

<div style="page-break-before: always;"></div>

# Part III: Technical Documentation

## Project Overview

The **Hospital Management System** is a comprehensive hospital management platform developed for Hospital de Blanes, Girona. It provides end-to-end management of patient records, medical staff, clinical visits, surgeries, admissions, prescriptions, and radiology exams. The system is built with a Python/Flask REST API backend, PostgreSQL 16 database, Tkinter desktop client, and Chart.js web dashboard.

The project was developed as a cross-module project for the ASIX program (Administració de Sistemes Informàtics en Xarxa) at Institut Sa Palomera during the 2025–2026 academic year.

## System Context

The system operates across two physical nodes:
- **Briar** (on-premise at the hospital) — hosts both the Flask API and the PostgreSQL primary database
- **Sion** (AWS EC2, eu-west-3 Paris) — hosts a PostgreSQL standby for disaster recovery

Hospital users (doctors, nurses, receptionists, admin staff) connect to Briar over the hospital LAN (192.168.4.0/24). The two nodes communicate over a Tailscale encrypted mesh VPN. All inter-node traffic is doubly encrypted (Tailscale WireGuard + PostgreSQL SSL).

## ER / Relational Model

The database consists of **24 tables** designed in Third Normal Form (3NF). Key patterns include:

- **Generalization/Specialization:** `STAFF` → `MEDICAL_STAFF`, `NURSING_STAFF`, `GENERAL_STAFF`
- **Junction tables:** `MEDICAL_STAFF_SPECIALTIES`, `SURGERY_ASSISTANTS`
- **Header-detail:** `PHARMACY_DISPENSATIONS` → `DISPENSATION_ITEMS`
- **Audit trail:** `AUDIT_LOGS` with before/after JSONB snapshots

## Security and Compliance

### RBAC (Role-Based Access Control)

Five PostgreSQL roles with granular table/column-level permissions:

| Role | Connections | Scope |
|------|-------------|-------|
| `app_admin` | 5 | Full access |
| `app_doctor` | 50 | CRUD on patients, visits, prescriptions, surgeries |
| `app_nurse` | 100 | Limited read on patients, manage admissions on own floor |
| `app_receptionist` | 10 | CRUD on patients, schedule appointments |
| `app_staff` | 30 | Read-only (name + room via `patient_directory` view) |

### Row-Level Security (RLS)

RLS policies ensure nurses only see patients on their assigned floor. Session variables (`app.current_user`, `app.current_staff_id`) are set at login via PostgreSQL `SET_CONFIG`.

### SSL/TLS

PostgreSQL uses self-signed SSL certificates (OpenSSL) with `hostssl` required for all remote connections in `pg_hba.conf`.

### Data Masking

Column-level access control restricts sensitive data by role. The `patient_directory` view exposes only name and room to non-medical staff.

## AGPD Compliance

The system aligns with Spanish data protection law (LOPDGDD) and GDPR requirements:

| Requirement | Implementation |
|-------------|----------------|
| Explicit consent | User registration with acceptance |
| Right to erasure | `anonymize_patient()` function |
| Data minimization | `patient_directory` view limits exposure |
| Limited retention | 5-day cyclic backup rotation |
| Technical security | RBAC + RLS + SSL + bcrypt + JWT |
| Audit trail | 8 automatic triggers on sensitive tables |

## High Availability and Disaster Recovery

### Replication Topology

- **Method:** PostgreSQL native streaming replication (asynchronous WAL shipping)
- **Role:** Active-passive (Briar = primary R/W, Sion = standby read-only)
- **Network:** Tailscale overlay network + hospital LAN
- **Replication user:** `replicator`

### Backup Strategy (Three Layers)

| Layer | Type | RPO | RTO |
|-------|------|-----|-----|
| Physical | `pg_basebackup` (PGDATA) | 24 hours | 30 minutes |
| Logical | `pg_dump -Fc` (full DB) | 15 minutes | 15–60 minutes |
| Config | `.env`, systemd, conf files | 24 hours | 5 minutes |

### Failover Procedure

```bash
# Promote Sion to primary
sudo -u postgres pg_ctl promote -D /var/lib/postgresql/16/main
# Reconfigure .env to point to Sion
# DATABASE_URL=postgresql://postgres:password@100.98.214.53:5432/hsp_db
```

## Test Data Generation

The system generates ~325,000 records across 12 tables using Faker:

- 50,000 patients (5% with Cyrillic names via `ru_RU` locale)
- 100,000 visits (80% past, 20% future for scheduling)
- 25,000 surgeries, 25,000 admissions, 80,000 prescriptions

Optimizations (batch inserts, SQL direct inserts, index disabling) reduced generation time from ~20 to ~5 minutes.

## Authentication

JWT-based authentication with bcrypt password hashing:

1. Client sends `POST /api/auth/login` with credentials
2. Server validates bcrypt hash against `APP_USERS` table
3. Returns signed JWT (1-hour expiry) containing `sub`, `role`, `staff_id`
4. Client stores token in memory (singleton pattern)
5. All subsequent requests include `Authorization: Bearer <token>`

## Maintenance Operations

Full CRUD operations via REST API:

- Staff management (medical, nursing, general)
- Patient registration
- Nurse-to-doctor/floor assignment
- Surgery scheduling with overlap prevention (PL/pgSQL trigger)
- Visit scheduling
- Medical device inventory per operating theater

## Queries and Reports

Three mandatory reports, one optional, one top:

| Report | Endpoint | Description |
|--------|----------|-------------|
| Floor data | `GET /api/reports/summary?floor_id=X` | Rooms, theaters, nurses |
| All staff | `GET /api/reports/summary?report=staff` | Complete personnel list |
| Visits per day | `GET /api/reports/visits` | Daily visit counts |
| Doctor ranking | `GET /api/reports/doctor-workload` | Top doctors by volume |
| Common diseases | `GET /api/reports/summary?report=diseases` | Most frequent diagnoses |

## Data Export and Dashboard

### Export Formats

- **XML:** Pretty-printed with `xml.dom.minidom.toprettyxml()` (2-space indent)
- **JSON:** Formatted with `json.dumps(data, indent=2)`
- **Validation:** XSD and JSON Schema validation before transmission
- **External API:** Automatic submission to Social Security API (Basic Auth)

### Dashboard

Built with **Chart.js** (free alternative to PowerBI), accessible at `http://192.168.4.254:5000/api/dashboard/view`.

| Chart | Type | Data Source |
|-------|------|-------------|
| Visits today | Metric | `visits_today` |
| Surgeries today | Metric | `surgeries_today` |
| Active admissions | Metric | `active_admissions` |
| Visits by specialty | Bar chart | `by_specialty` |
| 7-day trend | Line chart | `visits_trend` |
| Top 5 doctors | Horizontal bar | `top_doctors` |

PowerBI Desktop can also consume the JSON endpoint at `http://192.168.4.254:5000/api/dashboard/stats`.

## Installation Guide

Complete steps documented in [10_installation_manual.md](./10_installation_manual.md). Summary:

1. Install Ubuntu Server 24.04 on both nodes with LVM partitioning
2. Install and configure Tailscale
3. Configure UFW firewall
4. Install PostgreSQL 16 on both nodes
5. Generate TLS certificates
6. Configure primary (Briar) and standby (Sion) replication
7. Clone repository at `/opt/hms/releases/v1.0` with symlink at `/opt/hms/current`
8. Create Python virtual environment and install dependencies
9. Configure environment variables in `/etc/hms.env`
10. Create database and load schemas
11. Run API as systemd service (`hms-api.service`)
12. Deploy desktop client on LAN workstations

## Configuration

Key configuration files:

- `/opt/hms/current/server/src/.env` — Database URL, JWT secret, external API credentials
- `/etc/hms.env` — System-wide environment variables (root:root, permissions 600)
- `/etc/postgresql/16/main/postgresql.conf` — PostgreSQL configuration
- `/etc/postgresql/16/main/pg_hba.conf` — Access control rules
- `/etc/systemd/system/hms-api.service` — systemd unit for Flask API

## User Manual

Full user guide in [11_user_manual.md](./11_user_manual.md). Covers:

- Login and session management
- Dashboard overview
- Maintenance operations (staff, patients, assignments)
- Data Workspace (table browser with search, edit, delete)
- Operational Reports (daily visits and surgeries)
- Statistics (floor overview, staff directory, doctor/disease ranking)
- Advanced Reports (multi-tab with PDF export)
- Dummy Data generation
- Password change
- Common task walkthroughs

## Administrator Manual

Full administrator guide in [12_administrator_manual.md](./12_administrator_manual.md). Covers:

- User and role management (5 roles with distinct permissions)
- Audit log review and retention policy (2 years active, 7 years archive)
- Backup and recovery procedures (three-layer strategy)
- Monitoring setup with alert thresholds
- Daily/weekly/monthly/quarterly/annual maintenance checklists
- Security best practices (SSL, RBAC, firewalls, password policies)
- Incident response procedures

<div style="page-break-before: always;"></div>

# Part IV: Final Summary

## Technologies Used

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| Backend Framework | Python / Flask | 3.12 / 3.1 | REST API |
| Database | PostgreSQL | 16 | Relational storage |
| ORM | SQLAlchemy | 2.0 | Data abstraction |
| Desktop Client | Tkinter | (built-in) | GUI |
| Dashboard | Chart.js | 4.x | Web charts |
| Auth | JWT + bcrypt | — | Authentication |
| VPN | Tailscale | — | Secure networking |
| PDF Library | fpdf2 | — | Report export |
| Test Data | Faker | 22.x | Dummy generation |
| Cloud | AWS EC2 | t3.medium | Standby node |

## Achievements

| Area | Achievement |
|------|-------------|
| **Database** | 24-table relational model in 3NF, supporting patients, staff, visits, surgeries, admissions, pharmacy, radiology, and audit |
| **Security** | 5-role RBAC, RLS on sensitive tables, SSL encryption, bcrypt hashing, audit triggers on 8 tables |
| **High Availability** | Streaming replication between Briar (primary) and Sion (standby), 3-layer backup strategy, documented failover |
| **Data Volume** | 325,000 test records generated in ~5 minutes with Cyrillic support |
| **Export** | XML/JSON export with XSD/JSON Schema validation, Social Security API integration |
| **Dashboard** | Real-time Chart.js dashboard with 6 visualizations, PowerBI-compatible endpoint |
| **DevOps** | systemd service, automated deployment script, cron-based backups, monitoring scripts |
| **Documentation** | 12 delivery documents + this final document covering installation, user, and admin manuals |
| **Project Management** | 91 hours of work, 60+ atomic commits, Conventional Commits convention |
| **Compliance** | AGPD/LOPDGDD alignment with data minimization, audit trail, consent, and retention policies |

## Conclusió (CAT)

El **Hospital Management System** compleix tots els requisits funcionals i tècnics establerts per al projecte intermodular ASIX 2025–2026. El sistema ofereix una solució completa de gestió hospitalària amb un backend escalable, una base de dades segura i normalitzada, alta disponibilitat mitjançant replicació, i eines de visualització i exportació de dades.

Les principals fortaleses del projecte són la seguretat multicapa (RBAC + RLS + SSL + bcrypt), l'arquitectura d'alta disponibilitat amb dos nodes, la generació massiva de dades de prova, i la documentació exhaustiva de tot el sistema.

## Conclusion (ENG)

The **Hospital Management System** meets all functional and technical requirements established for the ASIX 2025–2026 cross-module project. The system delivers a complete hospital management solution with a scalable backend, a secure and normalized database, high availability through replication, and data visualization and export tools.

The project's main strengths are its multi-layer security (RBAC + RLS + SSL + bcrypt), the two-node high-availability architecture, massive test data generation, and comprehensive documentation covering the entire system.

---

<div style="text-align: center; margin-top: 50px;">
<hr style="width: 50%; margin: 30px auto;">
<p><em>Document generated on May 2026</em></p>
<p><em>Yossef Errazik · ASIX · Institut Sa Palomera · Hospital de Blanes</em></p>
<p><a href="https://github.com/yosseferrazik/hospital-management-project">github.com/yosseferrazik/hospital-management-project</a></p>
</div>
