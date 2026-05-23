# 5. PRG — Bloc de Manteniment

## Operacions de manteniment (CRUD)

Des de la pestanya **Maintenance** de l'aplicació d'escriptori (5 subpestanyes: Doctor, Nursing, General Staff, Patient, Assignments) es poden realitzar totes les operacions de manteniment del sistema. Cada operació es tradueix en una crida a l'API REST corresponent, que al seu torn executa operacions CRUD sobre la base de dades PostgreSQL mitjançant SQLAlchemy.

### Endpoints CRUD

| Tasca                              | Mètode | Endpoint API                                   | Descripció                                            |
| ---------------------------------- | ------ | ---------------------------------------------- | ----------------------------------------------------- |
| Alta personal mèdic                | POST   | `/api/maintenance/staff/medical`               | Afegir un metge/ssa                                   |
| Alta personal d'infermeria         | POST   | `/api/maintenance/staff/nursing`               | Afegir un/a infermer/a                                |
| Alta personal general              | POST   | `/api/maintenance/staff/general`               | Afegir administratiu, neteja, etc.                    |
| Alta nous pacients                 | POST   | `/api/maintenance/patients`                    | Afegir un nou pacient                                 |
| Assignar infermer a metge/planta   | PUT    | `/api/maintenance/nursing/assign`              | Cos: `{nurse_id, doctor_id}` o `{nurse_id, floor_id}` |
| Consultar cirurgies per data       | GET    | `/api/maintenance/surgeries?date=X`            | Llistar cirurgies amb pacient, cirurgià, assistents   |
| Consultar visites per data         | GET    | `/api/maintenance/visits/scheduled?date=X`     | Llistar visites programades                           |
| Consultar dispositius per quiròfan | GET    | `/api/medical-devices?theater_id=X`            | Dispositius disponibles en un quiròfan                |
| Modificar personal                 | PUT    | `/api/maintenance/staff/{id}`                  | Actualitzar dades d'un treballador                    |
| Eliminar personal                  | DELETE | `/api/maintenance/staff/{id}`                  | Baixa d'un treballador (desactivació lògica)          |
| Modificar pacient                  | PUT    | `/api/maintenance/patients/{id}`               | Actualitzar dades d'un pacient                        |

### Exemple de flux: Alta d'un pacient

**Petició HTTP:**

```json
POST /api/maintenance/patients
Authorization: Bearer <JWT>
Content-Type: application/json

{
  "first_name": "Maria",
  "last_name": "Garcia Lopez",
  "date_of_birth": "1985-04-12",
  "phone": "+34 612 345 678",
  "email": "maria.garcia@example.com",
  "address": "Carrer Major 42, 17300 Blanes",
  "emergency_contact": "+34 622 987 654"
}
```

**Resposta (201 Created):**

```json
{
  "id": 50123,
  "message": "Pacient creat correctament",
  "patient": {
    "id": 50123,
    "first_name": "Maria",
    "last_name": "Garcia Lopez",
    "full_name": "Maria Garcia Lopez"
  }
}
```

**Codi Font (Python / SQLAlchemy):**

```python
class PatientCreate(Schema):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=200)
    date_of_birth: date
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-]{6,20}$')
    email: Optional[str] = Field(None, pattern=r'^[\w\.\-]+@[\w\-]+\.\w+$')
    address: Optional[str] = None
    emergency_contact: Optional[str] = None

@app.post("/api/maintenance/patients")
def create_patient(data: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return {"id": patient.id, "message": "Pacient creat correctament", "patient": patient}
```

### Validació de dades

El sistema implementa validació tant al frontend (abans d'enviar) com al backend (abans de persistir):

| Camp             | Validació                                              |
| ---------------- | ------------------------------------------------------ |
| `first_name`     | Requerit, 1–100 caràcters, només lletres i espais      |
| `last_name`      | Requerit, 1–200 caràcters                              |
| `phone`          | Opcional, format telefònic (`^\+?[\d\s\-]{6,20}$`)    |
| `email`          | Opcional, format email vàlid                           |
| `date_of_birth`  | Requerit, no pot ser una data futura                   |
| `emergency_contact` | Opcional, validat com a telèfon                     |

**Gestió d'errors:**

```json
HTTP 422 Unprocessable Entity
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "El camp email no té un format vàlid",
      "type": "value_error.email"
    }
  ]
}
```

---

## PL/pgSQL: Funcions i triggers

Es van crear **5 funcions/procediments** a PostgreSQL per garantir la integritat de les dades i automatitzar processos crítics. A continuació es detalla la implementació de cadascuna.

### 1. `check_surgery_overlap()`

**Trigger** (BEFORE INSERT/UPDATE a `SURGERIES`) que evita reservar el mateix quiròfan al mateix dia/hora. Si ja existeix una cirurgia al mateix quiròfan amb solapament d'horari, llança un error.

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
        RAISE EXCEPTION 'El quiròfan % ja està reservat per a la data % entre % i %',
            NEW.theater_id, NEW.surgery_date, NEW.start_time, NEW.end_time;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_surgery_overlap
BEFORE INSERT OR UPDATE ON SURGERIES
FOR EACH ROW EXECUTE FUNCTION check_surgery_overlap();
```

Aquesta funció cobreix tots els casos de solapament: una nova cirurgia que comença durant una existent, acaba durant una existent, o engloba completament una existent.

### 2. `validate_nurse_assignment()`

**Trigger** (BEFORE INSERT/UPDATE a `NURSING_STAFF`) que comprova que el metge o la planta assignada existeixin realment a la base de dades.

```sql
CREATE OR REPLACE FUNCTION validate_nurse_assignment()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.doctor_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM MEDICAL_STAFF WHERE id = NEW.doctor_id
    ) THEN
        RAISE EXCEPTION 'El metge amb ID % no existeix', NEW.doctor_id;
    END IF;

    IF NEW.floor_id IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM FLOORS WHERE id = NEW.floor_id
    ) THEN
        RAISE EXCEPTION 'La planta amb ID % no existeix', NEW.floor_id;
    END IF;

    IF NEW.doctor_id IS NOT NULL AND NEW.floor_id IS NOT NULL THEN
        RAISE EXCEPTION 'Una infermera no pot dependre d\'un metge i d\'una planta simultàniament';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_nurse
BEFORE INSERT OR UPDATE ON NURSING_STAFF
FOR EACH ROW EXECUTE FUNCTION validate_nurse_assignment();
```

Aquesta validació garanteix la integritat referencial i aplica la regla de negoci que una infermera depèn **o** d'un metge **o** d'una planta, no de tots dos alhora.

### 3. `audit_trigger_function()`

Registrador d'auditoria genèric per a **8 taules sensibles** (`PATIENTS`, `MEDICAL_STAFF`, `NURSING_STAFF`, `GENERAL_STAFF`, `SURGERIES`, `VISITS`, `ADMISSIONS`, `PRESCRIPTIONS`). S'activa amb AFTER INSERT/UPDATE/DELETE i guarda: usuari, timestamp, acció, taula, valors anteriors/nous (JSON).

```sql
CREATE TABLE IF NOT EXISTS AUDIT_LOG (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    changed_by INTEGER,
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    user_id INTEGER;
BEGIN
    user_id := get_current_app_user_id();

    IF TG_OP = 'INSERT' THEN
        INSERT INTO AUDIT_LOG (table_name, record_id, action, new_values, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, 'INSERT', row_to_json(NEW)::jsonb, user_id);
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO AUDIT_LOG (table_name, record_id, action, old_values, new_values, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, 'UPDATE',
                row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb, user_id);
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO AUDIT_LOG (table_name, record_id, action, old_values, changed_by)
        VALUES (TG_TABLE_NAME, OLD.id, 'DELETE', row_to_json(OLD)::jsonb, user_id);
    END IF;

    RETURN NULL; -- AFTER trigger
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Exemple d'aplicació a la taula PATIENTS:
CREATE TRIGGER trg_audit_patients
AFTER INSERT OR UPDATE OR DELETE ON PATIENTS
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

### 4. `get_current_app_user_id()`

Funció helper que retorna l'ID de l'usuari actual des del context de sessió (`SET_CONFIG`). Utilitzada per les polítiques RLS i els triggers d'auditoria.

```sql
CREATE OR REPLACE FUNCTION get_current_app_user_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_user_id', TRUE), '')::INTEGER;
END;
$$ LANGUAGE plpgsql STABLE;
```

### 5. `get_current_staff_id()`

Funció helper que retorna l'ID del treballador actual des del context de sessió.

```sql
CREATE OR REPLACE FUNCTION get_current_staff_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_staff_id', TRUE), '')::INTEGER;
END;
$$ LANGUAGE plpgsql STABLE;
```

Ambdues funcions s'invoquen des de l'aplicació en cada petició autenticada:

```python
# Middleware que estableix el context de sessió PostgreSQL
def set_session_context(db: Session, user_id: int, staff_id: int):
    db.execute(text(f"SELECT set_config('app.current_user_id', '{user_id}', TRUE)"))
    db.execute(text(f"SELECT set_config('app.current_staff_id', '{staff_id}', TRUE)"))
```

---

## Row-Level Security (RLS)

Per assegurar que cada usuari només accedeix a les dades que li pertoquen, es van implementar polítiques RLS a les taules sensibles:

```sql
ALTER TABLE PATIENTS ENABLE ROW LEVEL SECURITY;

CREATE POLICY patients_doctor_access ON PATIENTS
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM VISITS
            WHERE VISITS.patient_id = PATIENTS.id
              AND VISITS.doctor_id = get_current_staff_id()
        )
        OR get_current_app_user_id() IN (
            SELECT user_id FROM ADMIN_USERS
        )
    );
```

---

## Funcionalitats obligatòries implementades

- ✅ Alta de personal (metge/ssa, infermer/a, administratiu/va, neteja...)
- ✅ Alta de nous pacients
- ✅ Per personal d'infermeria: saber si depèn d'un metge/ssa o és de planta
- ✅ Per un dia determinat: operacions previstes per quiròfan (pacient, hora, metge, infermeria)
- ✅ Per un dia determinat: visites planificades (hora, metge, pacient)
- ✅ 2 procediments/funcions/triggers PL/pgSQL mínim (se'n van crear 5)

## Funcionalitats opcionals implementades

- ✅ Donada una habitació: reserves previstes (data ingrés, sortida, pacient)
- ✅ Donat un pacient: historial de visites, diagnòstics, medicaments, ingressos, quiròfan
- ✅ Donat un metge/ssa: visites i operacions programades + hores disponibles

## Funcionalitats top implementades

- ✅ Per cada quiròfan: quants aparells mèdics té i quantitat de cadascun

## Imatges

A continuació es mostren les pantalles de l'aplicació per a les operacions de manteniment:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/maintenance/2026-05-22-17-24-32-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/maintenance/2026-05-22-17-24-48-image.png)
