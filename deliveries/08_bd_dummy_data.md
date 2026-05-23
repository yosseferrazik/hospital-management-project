# 8. BD — Dummy Data

## Visió general

Generació de dades falses per a proves de rendiment i validació de l'aplicació utilitzant la llibreria **Faker** (locale `es_ES` i `ru_RU`). El sistema de generació de dades de prova permet poblar la base de dades amb grans volums d'informació realista per verificar el comportament de l'aplicació sota càrrega.

**Ubicació del generador:** `server/src/app/services/dummy_service.py`

**Activació:** Des de l'aplicació d'escriptori: menú **Dummy Data** → configurar quantitat → **Generate**

---

## Implementació amb Faker

### Inicialització dels providers

```python
from faker import Faker

fake_es = Faker('es_ES')   # Dades espanyoles realistes
fake_ru = Faker('ru_RU')   # Dades en ciríl·lic (5% dels registres)

# Providers personalitzats per a dades mèdiques
SPECIALTIES = [
    "Cardiologia", "Pediatria", "Traumatologia",
    "Medicina General", "Oftalmologia", "Dermatologia"
]

DIAGNOSES_BY_SPECIALTY = {
    "Cardiologia": [
        "Hipertensió arterial", "Insuficiència cardíaca",
        "Arítmia", "Cardiopatia isquèmica"
    ],
    "Pediatria": [
        "Infecció respiratòria aguda", "Otitis",
        "Gastroenteritis", "Al·lèrgia alimentària"
    ],
    "Traumatologia": [
        "Fractura de turmell", "Luxació d'espatlla",
        "Esquinç de genoll", "Fractura de canell"
    ],
    "Medicina General": [
        "Infecció urinària", "Hipertensió arterial",
        "Diabetes tipus 2", "Refredat comú"
    ],
    "Oftalmologia": [
        "Miopia", "Cataractes", "Glaucoma",
        "Conjuntivitis", "Ull sec"
    ],
    "Dermatologia": [
        "Acne", "Dermatitis atòpica", "Psoriasi",
        "Infecció fúngica cutània"
    ]
}
```

### Generació de pacients per lots

```python
def generate_patients(count: int, batch_size: int = 20, commit_every: int = 400):
    """
    Genera 'count' pacients utilitzant Faker.
    El 5% dels pacients reben noms en ciríl·lic (ru_RU).
    Utilitza flush() cada 'batch_size' i commit() cada 'commit_every' registres.
    """
    patients = []
    for i in range(1, count + 1):
        # 5% de pacients en ciríl·lic
        faker = fake_ru if i % 20 == 0 else fake_es

        patient = Patient(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            date_of_birth=faker.date_of_birth(minimum_age=0, maximum_age=95),
            phone=faker.phone_number(),
            email=faker.email(),
            address=faker.address().replace('\n', ', '),
            emergency_contact=faker.phone_number()
        )
        db.add(patient)
        patients.append(patient)

        # Flush parcial per alliberar memòria de l'ORM
        if i % batch_size == 0:
            db.flush()

        # Commit periòdic per no saturar la transacció
        if i % commit_every == 0:
            db.commit()
            print(f"  → Commit parcial: {i} pacients generats")

    db.commit()
    return patients
```

---

## Volums de dades

Requisits del projecte i valors assolits:

| Entitat          | Quantitat objectiu   | Generat                             |
| ---------------- | -------------------- | ----------------------------------- |
| Pacients         | 50.000               | 50.000                              |
| Visites          | 100.000              | 100.000+ (2× pacients)              |
| Metges           | 100                  | 100                                 |
| Infermeres       | 200                  | 200                                 |
| Personal general | 100                  | 100 (50 administratius + 50 neteja) |
| Cirurgies        | ~25.000              | ~25.000                             |
| Admissions       | ~25.000              | ~25.000                             |
| Prescripcions    | Enllaçades a visites | Generades proporcionalment          |

### Anàlisi de volums

La generació completa insereix aproximadament **325.000 registres** distribuïts en 12 taules. La mida total estimada de la base de dades amb índexs és d'aproximadament **2.8 GB**.

| Taula            | Registres   | Mida estimada | Índexs principals                          |
| ---------------- | ----------- | ------------- | ------------------------------------------ |
| PATIENTS         | 50.000      | ~25 MB        | PK, idx_patient_name                       |
| MEDICAL_STAFF    | 100         | ~80 KB        | PK, idx_staff_specialty                    |
| NURSING_STAFF    | 200         | ~120 KB       | PK, idx_nurse_doctor, idx_nurse_floor      |
| GENERAL_STAFF    | 100         | ~60 KB        | PK                                         |
| VISITS           | 100.000     | ~80 MB        | PK, idx_visit_date, idx_visit_doctor       |
| SURGERIES        | 25.000      | ~45 MB        | PK, idx_surgery_date, idx_surgery_theater  |
| ADMISSIONS       | 25.000      | ~40 MB        | PK, idx_admission_dates, idx_admission_room|
| PRESCRIPTIONS    | ~80.000     | ~35 MB        | PK, idx_prescription_visit                |

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/dummy_data/2026-05-22-18-29-38-image.png)

---

## Procés de generació

L'ordre de generació segueix estrictament les dependències de claus foranes:

1. **Dades de suport** (especialitats, medicaments, plantes, habitacions, quiròfans, dispositius) es creen primer
2. **Staff**: metges amb especialitats, infermeres amb metge/planta assignat, personal general
3. **Pacients**: noms, adreces i telèfons realistes espanyols (amb un 5% en ciríl·lic)
4. **Visites**: distribuïdes en els últims 60 dies (algunes al futur per a visites programades), amb diagnòstics per especialitat
5. **Cirurgies, admissions, prescripcions, dispensacions, radiologia**: generades proporcionalment

### Generació de visites amb distribució temporal

```python
def generate_visits(patients, doctors, count: int):
    visits = []
    for _ in range(count):
        patient = random.choice(patients)
        doctor = random.choice(doctors)

        # Distribució temporal: 80% passat, 20% futur
        if random.random() < 0.8:
            visit_date = fake_es.date_between(start_date="-60d", end_date="today")
        else:
            visit_date = fake_es.date_between(start_date="today", end_date="+30d")

        diagnosis = random.choice(DIAGNOSES_BY_SPECIALTY.get(doctor.specialty, ["Consulta general"]))

        visit = Visit(
            patient_id=patient.id,
            doctor_id=doctor.id,
            visit_date=visit_date,
            diagnosis=diagnosis,
            notes=fake_es.text(max_nb_chars=200)
        )
        db.add(visit)
        visits.append(visit)
    return visits
```

---

## Dades en ciríl·lic

Aproximadament el **5%** dels pacients i staff tenen noms en alfabet ciríl·lic (generats amb Faker locale `ru_RU`) per complir el requisit de suport a pacients de l'Europa de l'Est. Aquesta característica demostra la capacitat de la base de dades per treballar amb caràcters multibyte (UTF-8).

**Exemples de noms generats:**

| Locale   | First Name     | Last Name       | Alfabet |
| -------- | -------------- | --------------- | ------- |
| `es_ES`  | María          | García López    | Llatí   |
| `es_ES`  | José Antonio   | Martínez Ruiz   | Llatí   |
| `ru_RU`  | Екатерина      | Иванова         | Ciríl·lic |
| `ru_RU`  | Дмитрий        | Соколов         | Ciríl·lic |
| `ru_RU`  | Ольга          | Кузнецова       | Ciríl·lic |

La base de dades utilitza `UTF8` (`LC_COLLATE = 'es_ES.UTF-8'`), que emmagatzema correctament qualsevol caràcter Unicode sense necessitat de configuracions especials.

---

## Optimització de rendiment

La generació inicial de 50.000 pacients i 100.000 visites era lenta (~20 minuts). Es va optimitzar amb diverses tècniques:

| Tècnica                    | Descripció                                                                 | Millora |
| -------------------------- | -------------------------------------------------------------------------- | ------- |
| **Insercions per lots**    | `flush()` cada 20 registres i `commit()` cada 400, evitant transaccions massa grans | ~3x     |
| **Pools de diagnòstics**   | Llistes de diagnòstics pre-calculades per especialitat en memòria, evitant consultes repetitives a BD | ~2x     |
| **Mostreig aleatori**      | `random.choice()` i `random.sample()` en lloc d'iteració seqüencial, millorant la distribució | ~1.5x   |
| **Desactivar índexs**      | Eliminar índexs no crítics abans de la càrrega i recrear-los després        | ~1.5x   |
| **Batch insert amb SQL**   | Ús de `INSERT INTO ... VALUES (...), (...)` en lloc d'insercions ORM individuals | ~2x     |

**Temps final aconseguit:** ~5 minuts per a la generació completa.

### Exemple de batch insert optimitzat

```python
def batch_insert_visits(visits_data: list[dict], batch_size: int = 500):
    """Insereix visites en lots utilitzant SQL directe per a més rendiment."""
    for i in range(0, len(visits_data), batch_size):
        batch = visits_data[i:i + batch_size]

        values = ", ".join(
            f"({v['patient_id']}, {v['doctor_id']}, "
            f"'{v['visit_date']}', '{v['diagnosis']}', "
            f"'{v['notes'].replace(chr(39), chr(39)+chr(39))}')"
            for v in batch
        )

        db.execute(text(f"""
            INSERT INTO VISITS (patient_id, doctor_id, visit_date, diagnosis, notes)
            VALUES {values}
        """))
        db.commit()
```

---

## Neteja

Una taula `DummyRegistry` rastreja tots els registres generats:

```sql
CREATE TABLE IF NOT EXISTS DUMMY_REGISTRY (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_ids INTEGER[] NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    batch_id UUID NOT NULL
);
```

L'opció **Cleanup dummy data** de l'aplicació d'escriptori executa l'eliminació en ordre invers de dependències:

```python
def cleanup_dummy_data(batch_id: UUID):
    """Elimina totes les dades de prova generades en un batch."""
    tables_in_order = [
        "RADIOLOGY", "DISPENSATIONS", "PRESCRIPTIONS",
        "ADMISSIONS", "SURGERIES", "VISITS",
        "PATIENTS", "GENERAL_STAFF", "NURSING_STAFF",
        "MEDICAL_STAFF"
    ]

    registry_entries = db.query(DummyRegistry).filter(
        DummyRegistry.batch_id == batch_id
    ).order_by(
        # Ordenar per l'índex invers de tables_in_order
        case(
            *[(DummyRegistry.table_name == t, len(tables_in_order) - i)
              for i, t in enumerate(tables_in_order)],
            else_=0
        ).desc()
    ).all()

    for entry in registry_entries:
        ids_str = ", ".join(str(rid) for rid in entry.record_ids)
        db.execute(text(f"DELETE FROM {entry.table_name} WHERE id IN ({ids_str})"))

    # Netejar el registre
    db.query(DummyRegistry).filter(
        DummyRegistry.batch_id == batch_id
    ).delete()
    db.commit()
```

Aquest procés garanteix que:
- No quedin restes de dades de prova al sistema
- S'elimini respectant les claus foranes (ordre invers de creació)
- El registre `DummyRegistry` també es netegi

---

## Com executar

Des de l'aplicació d'escriptori:

1. Iniciar sessió com a admin
2. Obrir **Dummy Data** des de la barra lateral
3. Introduir nombre de pacients (màx. 50.000)
4. Fer clic a **Generate**

També des de l'API:

```bash
POST /api/dummy/generate
Content-Type: application/json

{
  "patient_count": 50000,
  "include_cyrillic": true,
  "visits_per_patient": 2
}
```

**Resposta:**

```json
{
  "batch_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "patients": 50000,
  "visits": 100000,
  "surgeries": 25134,
  "admissions": 24891,
  "elapsed_seconds": 312.4
}
```

---

## Referències

- `docs/02_database/test_data.md` — Documentació completa
- `server/src/app/services/dummy_service.py` — Codi font del generador
- `scripts/sql/schema.sql` — Esquema amb índexs per a rendiment
