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

## Diccionari de dades

### PATIENTS

| Columna               | Tipus        | Notes                            |
| --------------------- | ------------ | -------------------------------- |
| patient_id            | SERIAL PK    |                                  |
| national_id           | VARCHAR(50)  | UNIQUE, DNI/NIE                  |
| first_name, last_name | VARCHAR(100) | Suport ciríl·lic (UTF-8)         |
| birth_date            | DATE         |                                  |
| gender                | VARCHAR(10)  | CHECK 'MALE'/'FEMALE'/'OTHER'    |
| phone, email, address | VARCHAR      | Contacte                         |
| blood_type            | VARCHAR(5)   | A+, A-, B+, B-, O+, O-, AB+, AB- |
| allergies             | TEXT         | Text lliure                      |
| health_card           | VARCHAR(50)  | UNIQUE                           |

### STAFF

| Columna               | Tipus        | Notes                           |
| --------------------- | ------------ | ------------------------------- |
| staff_id              | SERIAL PK    |                                 |
| national_id           | VARCHAR(50)  | UNIQUE                          |
| first_name, last_name | VARCHAR(100) |                                 |
| staff_type            | VARCHAR(50)  | 'MEDICAL', 'NURSING', 'GENERAL' |
| curriculum / license  | TEXT         | Només per a subtipus MEDICAL    |

### VISITS

| Columna    | Tipus                      | Notes |
| ---------- | -------------------------- | ----- |
| visit_id   | SERIAL PK                  |       |
| patient_id | INTEGER FK → PATIENTS      |       |
| doctor_id  | INTEGER FK → MEDICAL_STAFF |       |
| visit_date | DATE                       |       |
| diagnosis  | TEXT                       |       |
| notes      | TEXT                       |       |

### Altres taules destacades

| Taula                     | Descripció                                       |
| ------------------------- | ------------------------------------------------ |
| MEDICAL_SPECIALTIES       | Llistat d'especialitats mèdiques                 |
| MEDICAL_STAFF_SPECIALTIES | Assignació metge-especialitat (N:M)              |
| SCHEDULED_APPOINTMENTS    | Visites programades amb hora                     |
| SURGERIES                 | Intervencions quirúrgiques                       |
| SURGERY_ASSISTANTS        | Personal d'infermeria que assisteix una cirurgia |
| ADMISSIONS                | Ingressos hospitalaris                           |
| PHARMACY_DISPENSATIONS    | Dispensacions de farmàcia                        |
| DISPENSATION_ITEMS        | Articles d'una dispensació                       |
| RADIOLOGY_EXAMS           | Proves radiològiques                             |
| AUDIT_LOGS                | Registre d'auditoria                             |
| APP_USERS                 | Usuaris del sistema                              |

## Scripts SQL

- `scripts/sql/schema.sql` — Esquema complet (25 taules amb índexs, constraints, FKs)
- Les taules es creen automàticament via `db.create_all()` a l'inici de l'API

## Referències

- Diagrama ER: `docs/01_planning/images/` (Draw.io)
- Esquema SQL: `scripts/sql/schema.sql`
- Models Python: `server/src/app/models.py`
