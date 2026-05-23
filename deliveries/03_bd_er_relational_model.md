# 3. BD — Disseny ER i Model Relacional

## Visió general

La base de dades té **24 taules** que cobreixen pacients, personal mèdic, visites, cirurgies, admissions, farmàcia, radiologia, auditoria i generació de dades de prova. El disseny segueix els principis de normalització (3FN) per evitar redundàncies i garantir la integritat de les dades.

## Diagrama ER

El diagrama ER es va dissenyar amb Draw.io. Es pot consultar a:
`docs/01_planning/images/` (arxiu Draw.io)

## Model relacional

### Entitats principals i relacions

El model relacional s'estructura al voltant de les entitats principals STAFF i PATIENTS, amb múltiples entitats dependents que capturen les diferents operacions hospitalàries:

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

DUMMY_REGISTRY (rastreja dades generades per a neteja)
APP_USERS ──── STAFF (mapatge d'usuaris)
AUDIT_LOGS (traça d'auditoria per a 8 taules sensibles)
```

### Patrons de disseny

| Patró                | Exemple                                                     |
| -------------------- | ----------------------------------------------------------- |
| Base + subtipus      | `STAFF` → `MEDICAL_STAFF`, `NURSING_STAFF`, `GENERAL_STAFF` |
| Taula de junció      | `MEDICAL_STAFF_SPECIALTIES`, `SURGERY_ASSISTANTS`           |
| Taula d'auditoria    | `AUDIT_LOGS` amb valors abans/després                       |
| Taules de referència | `MEDICAL_SPECIALTIES`, `MEDICATIONS`, `FLOORS`              |
| Capçalera-detall     | `PHARMACY_DISPENSATIONS` → `DISPENSATION_ITEMS`             |

### Convencions de noms

- Taules: majúscules snake case (`PATIENTS`, `MEDICAL_STAFF_SPECIALTIES`)
- Columnes: minúscules snake case (`patient_id`, `created_at`)
- PK: `<entitat>_id` — FK: nom de la PK referenciada
- Índexs: `idx_<taula>_<columna>`
- Constraints: `uq_<descripció>`, `chk_<descripció>`

## Normalització (3FN)

El disseny compleix la **Tercera Forma Normal (3FN)**:

| Forma Normal | Compliment | Justificació                                                                  |
| ------------ | ---------- | ----------------------------------------------------------------------------- |
| **1FN**      | ✓          | Totes les columnes són atòmiques; no hi ha grups repetits ni arrays multivalor |
| **2FN**      | ✓          | Cada columna no clau depèn completament de la clau primària (no dependències parcials) |
| **3FN**      | ✓          | No hi ha dependències transitives: totes les columnes no clau depenen directament de la PK |

**Exemple de 3FN:** La taula `ADMISSIONS` conté `room_id` (FK a ROOMS), no el nom de l'habitació ni el número de planta. Per obtindre el nom de la planta es navega per `ADMISSIONS → ROOMS → FLOORS`, evitant redundància de dades.

## Diccionari de dades complet (24 taules)

### PATIENTS

| Columna               | Tipus        | Constraints                    | Notes                            |
| --------------------- | ------------ | ------------------------------ | -------------------------------- |
| patient_id            | SERIAL       | PK                             |                                  |
| national_id           | VARCHAR(50)  | UNIQUE, NOT NULL               | DNI/NIE                          |
| first_name            | VARCHAR(100) | NOT NULL                       | Suport ciríl·lic (UTF-8)         |
| last_name             | VARCHAR(100) | NOT NULL                       | Suport ciríl·lic (UTF-8)         |
| birth_date            | DATE         | NOT NULL                       |                                  |
| gender                | VARCHAR(10)  | CHECK ('MALE','FEMALE','OTHER')|                                  |
| phone                 | VARCHAR(20)  |                                |                                  |
| email                 | VARCHAR(100) |                                |                                  |
| address               | TEXT         |                                |                                  |
| blood_type            | VARCHAR(5)   | CHECK (valors vàlids)          | A+, A-, B+, B-, O+, O-, AB+, AB- |
| allergies             | TEXT         |                                | Text lliure                      |
| health_card           | VARCHAR(50)  | UNIQUE, NOT NULL               |                                  |
| created_at            | TIMESTAMP    | DEFAULT NOW()                  |                                  |
| updated_at            | TIMESTAMP    | DEFAULT NOW()                  |                                  |

### STAFF

| Columna               | Tipus        | Constraints                    | Notes                           |
| --------------------- | ------------ | ------------------------------ | ------------------------------- |
| staff_id              | SERIAL       | PK                             |                                 |
| national_id           | VARCHAR(50)  | UNIQUE, NOT NULL               |                                 |
| first_name            | VARCHAR(100) | NOT NULL                       |                                 |
| last_name             | VARCHAR(100) | NOT NULL                       |                                 |
| staff_type            | VARCHAR(50)  | NOT NULL, CHECK                | 'MEDICAL', 'NURSING', 'GENERAL' |
| phone                 | VARCHAR(20)  |                                |                                 |
| email                 | VARCHAR(100) |                                |                                 |
| created_at            | TIMESTAMP    | DEFAULT NOW()                  |                                 |
| updated_at            | TIMESTAMP    | DEFAULT NOW()                  |                                 |

### MEDICAL_STAFF

| Columna               | Tipus        | Constraints                    | Notes                           |
| --------------------- | ------------ | ------------------------------ | ------------------------------- |
| medical_staff_id      | INTEGER      | PK, FK → STAFF.staff_id        | Hereta de STAFF                 |
| license_number        | VARCHAR(50)  | UNIQUE                         |                                 |
| curriculum            | TEXT         |                                | Formació acadèmica              |

### MEDICAL_SPECIALTIES

| Columna               | Tipus        | Constraints                    | Notes                           |
| --------------------- | ------------ | ------------------------------ | ------------------------------- |
| specialty_id          | SERIAL       | PK                             |                                 |
| specialty_name        | VARCHAR(100) | UNIQUE, NOT NULL               | Cardiologia, Pediatria, etc.    |
| description           | TEXT         |                                |                                 |

### MEDICAL_STAFF_SPECIALTIES (junció N:M)

| Columna               | Tipus        | Constraints                    | Notes                           |
| --------------------- | ------------ | ------------------------------ | ------------------------------- |
| medical_staff_id      | INTEGER      | PK, FK → MEDICAL_STAFF         |                                 |
| specialty_id          | INTEGER      | PK, FK → MEDICAL_SPECIALTIES   |                                 |

### NURSING_STAFF

| Columna               | Tipus        | Constraints                    | Notes                           |
| --------------------- | ------------ | ------------------------------ | ------------------------------- |
| nursing_staff_id      | INTEGER      | PK, FK → STAFF.staff_id        | Hereta de STAFF                 |
| assigned_floor        | INTEGER      | FK → FLOORS.floor_id           | Planta assignada                |
| assigned_doctor       | INTEGER      | FK → MEDICAL_STAFF             | Metge de capçalera              |

### GENERAL_STAFF

| Columna               | Tipus        | Constraints                    | Notes                           |
| --------------------- | ------------ | ------------------------------ | ------------------------------- |
| general_staff_id      | INTEGER      | PK, FK → STAFF.staff_id        | Hereta de STAFF                 |
| department            | VARCHAR(100) |                                | Administració, Manteniment, etc.|

### VISITS

| Columna    | Tipus        | Constraints                    | Notes                           |
| ---------- | ------------ | ------------------------------ | ------------------------------- |
| visit_id   | SERIAL       | PK                             |                                 |
| patient_id | INTEGER      | FK → PATIENTS, NOT NULL        |                                 |
| doctor_id  | INTEGER      | FK → MEDICAL_STAFF, NOT NULL   |                                 |
| visit_date | DATE         | NOT NULL                       |                                 |
| diagnosis  | TEXT         |                                |                                 |
| notes      | TEXT         |                                |                                 |
| created_at | TIMESTAMP    | DEFAULT NOW()                  |                                 |

### PRESCRIPTIONS

| Columna       | Tipus        | Constraints                    | Notes                           |
| ------------- | ------------ | ------------------------------ | ------------------------------- |
| prescription_id | SERIAL     | PK                             |                                 |
| visit_id      | INTEGER      | FK → VISITS, NOT NULL          |                                 |
| medication_id | INTEGER      | FK → MEDICATIONS, NOT NULL     |                                 |
| dosage        | VARCHAR(100) | NOT NULL                       | e.g., "500mg/8h"                |
| duration_days | INTEGER      |                                |                                 |
| notes         | TEXT         |                                |                                 |
| created_at    | TIMESTAMP    | DEFAULT NOW()                  |                                 |

### MEDICATIONS

| Columna         | Tipus        | Constraints                    | Notes                           |
| --------------- | ------------ | ------------------------------ | ------------------------------- |
| medication_id   | SERIAL       | PK                             |                                 |
| medication_name | VARCHAR(200) | UNIQUE, NOT NULL               |                                 |
| brand_name      | VARCHAR(200) |                                |                                 |
| description     | TEXT         |                                |                                 |

### SCHEDULED_APPOINTMENTS

| Columna        | Tipus        | Constraints                    | Notes                           |
| -------------- | ------------ | ------------------------------ | ------------------------------- |
| appointment_id | SERIAL       | PK                             |                                 |
| patient_id     | INTEGER      | FK → PATIENTS, NOT NULL        |                                 |
| doctor_id      | INTEGER      | FK → MEDICAL_STAFF, NOT NULL   |                                 |
| scheduled_date | DATE         | NOT NULL                       |                                 |
| scheduled_time | TIME         | NOT NULL                       |                                 |
| status         | VARCHAR(20)  | DEFAULT 'SCHEDULED'            | SCHEDULED, COMPLETED, CANCELLED |
| notes          | TEXT         |                                |                                 |
| created_at     | TIMESTAMP    | DEFAULT NOW()                  |                                 |

### ADMISSIONS

| Columna          | Tipus        | Constraints                    | Notes                           |
| ---------------- | ------------ | ------------------------------ | ------------------------------- |
| admission_id     | SERIAL       | PK                             |                                 |
| patient_id       | INTEGER      | FK → PATIENTS, NOT NULL        |                                 |
| room_id          | INTEGER      | FK → ROOMS                     |                                 |
| admission_date   | TIMESTAMP    | NOT NULL                       |                                 |
| discharge_date   | TIMESTAMP    |                                | NULL si encara ingressat         |
| diagnosis        | TEXT         |                                |                                 |
| notes            | TEXT         |                                |                                 |
| created_at       | TIMESTAMP    | DEFAULT NOW()                  |                                 |

### ROOMS

| Columna     | Tipus        | Constraints                    | Notes                           |
| ----------- | ------------ | ------------------------------ | ------------------------------- |
| room_id     | SERIAL       | PK                             |                                 |
| room_number | VARCHAR(10)  | NOT NULL                       | e.g., "301A"                    |
| floor_id    | INTEGER      | FK → FLOORS, NOT NULL          |                                 |
| room_type   | VARCHAR(20)  | NOT NULL                       | INDIVIDUAL, DOUBLE, SUITE       |
| capacity    | INTEGER      | NOT NULL                       |                                 |
| is_active   | BOOLEAN      | DEFAULT TRUE                   |                                 |

### FLOORS

| Columna     | Tipus        | Constraints                    | Notes                           |
| ----------- | ------------ | ------------------------------ | ------------------------------- |
| floor_id    | SERIAL       | PK                             |                                 |
| floor_name  | VARCHAR(50)  | NOT NULL                       | e.g., "Planta 3 - Cirurgia"     |
| floor_number| INTEGER      | UNIQUE, NOT NULL               |                                 |

### SURGERIES

| Columna          | Tipus        | Constraints                    | Notes                           |
| ---------------- | ------------ | ------------------------------ | ------------------------------- |
| surgery_id       | SERIAL       | PK                             |                                 |
| patient_id       | INTEGER      | FK → PATIENTS, NOT NULL        |                                 |
| doctor_id        | INTEGER      | FK → MEDICAL_STAFF, NOT NULL   | Metge responsable               |
| theater_id       | INTEGER      | FK → OPERATING_THEATERS        |                                 |
| surgery_date     | TIMESTAMP    | NOT NULL                       |                                 |
| duration_minutes | INTEGER      |                                |                                 |
| description      | TEXT         |                                |                                 |
| status           | VARCHAR(20)  | DEFAULT 'SCHEDULED'            | SCHEDULED, IN_PROGRESS, DONE    |
| notes            | TEXT         |                                |                                 |
| created_at       | TIMESTAMP    | DEFAULT NOW()                  |                                 |

### SURGERY_ASSISTANTS (junció N:M)

| Columna          | Tipus        | Constraints                    | Notes                           |
| ---------------- | ------------ | ------------------------------ | ------------------------------- |
| surgery_id       | INTEGER      | PK, FK → SURGERIES             |                                 |
| nursing_staff_id | INTEGER      | PK, FK → NURSING_STAFF         | Infermer/a que assisteix        |

### OPERATING_THEATERS

| Columna      | Tipus        | Constraints                    | Notes                           |
| ------------ | ------------ | ------------------------------ | ------------------------------- |
| theater_id   | SERIAL       | PK                             |                                 |
| theater_name | VARCHAR(100) | NOT NULL                       | e.g., "Quiròfan 1"              |
| floor_id     | INTEGER      | FK → FLOORS                    |                                 |
| is_active    | BOOLEAN      | DEFAULT TRUE                   |                                 |

### MEDICAL_DEVICES

| Columna        | Tipus        | Constraints                    | Notes                           |
| -------------- | ------------ | ------------------------------ | ------------------------------- |
| device_id      | SERIAL       | PK                             |                                 |
| device_name    | VARCHAR(200) | NOT NULL                       |                                 |
| serial_number  | VARCHAR(100) | UNIQUE                         |                                 |
| theater_id     | INTEGER      | FK → OPERATING_THEATERS        |                                 |
| calibration_date| DATE        |                                |                                 |
| is_active      | BOOLEAN      | DEFAULT TRUE                   |                                 |

### PHARMACY_DISPENSATIONS

| Columna           | Tipus        | Constraints                    | Notes                           |
| ----------------- | ------------ | ------------------------------ | ------------------------------- |
| dispensation_id   | SERIAL       | PK                             |                                 |
| admission_id      | INTEGER      | FK → ADMISSIONS                | Dispensació durant ingrés       |
| visit_id          | INTEGER      | FK → VISITS                    | Dispensació ambulatoria         |
| dispensation_date | TIMESTAMP    | NOT NULL                       |                                 |
| notes             | TEXT         |                                |                                 |
| created_at        | TIMESTAMP    | DEFAULT NOW()                  |                                 |

> Nota: `admission_id` o `visit_id` són mutually exclusive — una dispensació pertany a un ingrés o a una visita, però no a tots dos.

### DISPENSATION_ITEMS

| Columna          | Tipus        | Constraints                    | Notes                           |
| ---------------- | ------------ | ------------------------------ | ------------------------------- |
| item_id          | SERIAL       | PK                             |                                 |
| dispensation_id  | INTEGER      | FK → PHARMACY_DISPENSATIONS    |                                 |
| medication_id    | INTEGER      | FK → MEDICATIONS               |                                 |
| quantity         | INTEGER      | NOT NULL                       |                                 |
| unit             | VARCHAR(20)  | NOT NULL                       | e.g., "comprimits", "ml"        |

### RADIOLOGY_EXAMS

| Columna       | Tipus        | Constraints                    | Notes                           |
| ------------- | ------------ | ------------------------------ | ------------------------------- |
| exam_id       | SERIAL       | PK                             |                                 |
| patient_id    | INTEGER      | FK → PATIENTS, NOT NULL        |                                 |
| doctor_id     | INTEGER      | FK → MEDICAL_STAFF             | Metge sol·licitant              |
| exam_type     | VARCHAR(100) | NOT NULL                       | RX, TAC, RMN, Ecografia, etc.   |
| exam_date     | TIMESTAMP    | NOT NULL                       |                                 |
| results       | TEXT         |                                | Informe radiològic              |
| notes         | TEXT         |                                |                                 |
| created_at    | TIMESTAMP    | DEFAULT NOW()                  |                                 |

### APP_USERS

| Columna       | Tipus        | Constraints                    | Notes                           |
| ------------- | ------------ | ------------------------------ | ------------------------------- |
| user_id       | SERIAL       | PK                             |                                 |
| username      | VARCHAR(50)  | UNIQUE, NOT NULL               |                                 |
| password_hash | VARCHAR(255) | NOT NULL                       | bcrypt hash                     |
| role          | VARCHAR(20)  | NOT NULL                       | ADMIN, DOCTOR, NURSE, STAFF, RECEPTIONIST |
| staff_id      | INTEGER      | FK → STAFF.staff_id            | Pot ser NULL (admin pur)        |
| is_active     | BOOLEAN      | DEFAULT TRUE                   |                                 |
| created_at    | TIMESTAMP    | DEFAULT NOW()                  |                                 |

### AUDIT_LOGS

| Columna      | Tipus        | Constraints                    | Notes                           |
| ------------ | ------------ | ------------------------------ | ------------------------------- |
| log_id       | BIGSERIAL    | PK                             |                                 |
| table_name   | VARCHAR(50)  | NOT NULL                       | Taula afectada                  |
| record_id    | INTEGER      | NOT NULL                       | ID del registre afectat         |
| action       | VARCHAR(10)  | NOT NULL                       | INSERT, UPDATE, DELETE          |
| old_data     | JSONB        |                                | Valors abans del canvi          |
| new_data     | JSONB        |                                | Valors després del canvi        |
| changed_by   | VARCHAR(50)  |                                | Usuari que va fer el canvi      |
| changed_at   | TIMESTAMP    | DEFAULT NOW()                  |                                 |

### DUMMY_REGISTRY

| Columna        | Tipus        | Constraints                    | Notes                           |
| -------------- | ------------ | ------------------------------ | ------------------------------- |
| registry_id    | SERIAL       | PK                             |                                 |
| table_name     | VARCHAR(50)  | NOT NULL                       | Taula on es van inserir dades   |
| record_count   | INTEGER      | NOT NULL                       | Nombre de registres inserits    |
| generated_at   | TIMESTAMP    | DEFAULT NOW()                  |                                 |
| batch_id       | VARCHAR(50)  |                                | Per a neteja massiva            |

### Relacions entre taules

| FK                          | Taula origen            | Taula destí                 | Tipus |
| --------------------------- | ----------------------- | --------------------------- | ----- |
| `medical_staff_id`          | MEDICAL_STAFF           | STAFF                       | 1:1   |
| `nursing_staff_id`          | NURSING_STAFF           | STAFF                       | 1:1   |
| `general_staff_id`          | GENERAL_STAFF           | STAFF                       | 1:1   |
| `patient_id`                | VISITS                  | PATIENTS                    | N:1   |
| `doctor_id`                 | VISITS                  | MEDICAL_STAFF               | N:1   |
| `patient_id`                | ADMISSIONS              | PATIENTS                    | N:1   |
| `room_id`                   | ADMISSIONS              | ROOMS                       | N:1   |
| `floor_id`                  | ROOMS                   | FLOORS                      | N:1   |
| `patient_id`                | SURGERIES               | PATIENTS                    | N:1   |
| `theater_id`                | SURGERIES               | OPERATING_THEATERS          | N:1   |
| `medical_staff_id`          | MEDICAL_STAFF_SPECIALTIES | MEDICAL_STAFF             | N:M   |
| `specialty_id`              | MEDICAL_STAFF_SPECIALTIES | MEDICAL_SPECIALTIES       | N:M   |
| `surgery_id`                | SURGERY_ASSISTANTS      | SURGERIES                   | N:M   |
| `nursing_staff_id`          | SURGERY_ASSISTANTS      | NURSING_STAFF               | N:M   |
| `dispensation_id`           | DISPENSATION_ITEMS      | PHARMACY_DISPENSATIONS      | N:1   |
| `medication_id`             | DISPENSATION_ITEMS      | MEDICATIONS                 | N:1   |
| `staff_id`                  | APP_USERS               | STAFF                       | N:1   |
| `assigned_floor`            | NURSING_STAFF           | FLOORS                      | N:1   |
| `assigned_doctor`           | NURSING_STAFF           | MEDICAL_STAFF               | N:1   |

## Indexació i optimització

Els índexs es defineixen per millorar el rendiment de les consultes més freqüents:

| Índex                          | Taula            | Columna(s)            | Justificació                                    |
| ------------------------------ | ---------------- | --------------------- | ----------------------------------------------- |
| `idx_patients_national_id`     | PATIENTS         | `national_id`         | Cerca per DNI (única)                           |
| `idx_patients_health_card`     | PATIENTS         | `health_card`         | Cerca per targeta sanitària                     |
| `idx_visits_patient`           | VISITS           | `patient_id`          | Historial de visites d'un pacient               |
| `idx_visits_date`              | VISITS           | `visit_date`          | Consultes per data                              |
| `idx_admissions_patient`       | ADMISSIONS       | `patient_id`          | Historial d'ingressos                           |
| `idx_admissions_active`        | ADMISSIONS       | `discharge_date`      | Pacients actualment ingressats (NULL filter)    |
| `idx_surgeries_patient`        | SURGERIES        | `patient_id`          | Historial quirúrgic                             |
| `idx_surgeries_date`           | SURGERIES        | `surgery_date`        | Programació quirúrgica                          |
| `idx_appointments_date`        | SCHEDULED_APPOINTMENTS | `scheduled_date` | Consultes de cites per dia                      |
| `idx_audit_logs_table`         | AUDIT_LOGS       | `table_name`          | Auditoria per taula                             |
| `idx_audit_logs_timestamp`     | AUDIT_LOGS       | `changed_at`          | Auditoria cronològica                           |

## Exemples SQL

### Creació de la taula PATIENTS

```sql
CREATE TABLE PATIENTS (
    patient_id   SERIAL PRIMARY KEY,
    national_id  VARCHAR(50) NOT NULL UNIQUE,
    first_name   VARCHAR(100) NOT NULL,
    last_name    VARCHAR(100) NOT NULL,
    birth_date   DATE NOT NULL,
    gender       VARCHAR(10) CHECK (gender IN ('MALE', 'FEMALE', 'OTHER')),
    phone        VARCHAR(20),
    email        VARCHAR(100),
    address      TEXT,
    blood_type   VARCHAR(5) CHECK (blood_type IN (
                     'A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'
                 )),
    allergies    TEXT,
    health_card  VARCHAR(50) NOT NULL UNIQUE,
    created_at   TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP DEFAULT NOW()
);
```

### Consulta: Pacients actualment ingressats

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

### Consulta: Visites d'un pacient amb diagnòstic

```sql
SELECT v.visit_date, v.diagnosis,
       s.first_name || ' ' || s.last_name AS doctor_name
FROM VISITS v
JOIN MEDICAL_STAFF ms ON v.doctor_id = ms.medical_staff_id
JOIN STAFF s ON ms.medical_staff_id = s.staff_id
WHERE v.patient_id = 1
ORDER BY v.visit_date DESC;
```

### Consulta: Ocupació de quiròfans

```sql
SELECT ot.theater_id, ot.theater_name,
       COUNT(s.surgery_id) AS total_surgeries
FROM OPERATING_THEATERS ot
LEFT JOIN SURGERIES s ON ot.theater_id = s.theater_id
    AND s.surgery_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY ot.theater_id, ot.theater_name
ORDER BY total_surgeries DESC;
```

## Scripts SQL

- `scripts/sql/schema.sql` — Esquema complet (24 taules amb índexs, constraints, FKs)
- `scripts/sql/security.sql` — Rols, permisos, RLS
- Les taules es creen automàticament via `db.create_all()` a l'inici de l'API

## Referències

- Diagrama ER: `docs/01_planning/images/` (Draw.io)
- Esquema SQL: `scripts/sql/schema.sql`
- Models Python: `server/src/app/models.py`
