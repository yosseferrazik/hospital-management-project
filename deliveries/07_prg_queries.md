# 7. PRG — Bloc de Consultes

## Informes disponibles

Tots accessibles des de l'aplicació d'escriptori (pestanyes **Operational Reports**, **Statistics**, **Advanced Reports**) o via API REST. El sistema ofereix informes obligatoris, opcionals i top que cobreixen totes les necessitats de gestió hospitalària.

### Obligatoris

| Informe            | Endpoint API                                      | Descripció                                     |
| ------------------ | ------------------------------------------------- | ---------------------------------------------- |
| Dades d'una planta | `GET /api/reports/summary?floor_id=X`             | Habitacions, quiròfans i personal d'infermeria |
| Tot el personal    | `GET /api/reports/summary?report=staff`           | Llistat complet de treballadors                |
| Visites per dia    | `GET /api/reports/visits?start_date=X&end_date=Y` | Nombre de visites ateses per dia               |

#### SQL dels informes obligatoris

**Dades d'una planta:**

```sql
SELECT
    f.id AS floor_id,
    f.name AS floor_name,
    (SELECT json_agg(json_build_object('id', r.id, 'room_number', r.room_number, 'beds', r.beds))
     FROM ROOMS r WHERE r.floor_id = f.id) AS rooms,
    (SELECT json_agg(json_build_object('id', t.id, 'name', t.name, 'equipment_count', t.equipment_count))
     FROM THEATERS t WHERE t.floor_id = f.id) AS theaters,
    (SELECT json_agg(json_build_object('id', ns.id, 'name', CONCAT(ns.first_name, ' ', ns.last_name)))
     FROM NURSING_STAFF ns WHERE ns.floor_id = f.id) AS nurses
FROM FLOORS f
WHERE f.id = :floor_id;
```

**Tot el personal:**

```sql
SELECT 'medical' AS staff_type, id, first_name, last_name, specialty AS department
FROM MEDICAL_STAFF
UNION ALL
SELECT 'nursing', id, first_name, last_name, 'Infermeria' AS department
FROM NURSING_STAFF
UNION ALL
SELECT 'general', id, first_name, last_name, position AS department
FROM GENERAL_STAFF
ORDER BY staff_type, last_name;
```

**Visites per dia:**

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

Captures dels informes obligatoris:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-22-02-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-22-16-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-22-28-image.png)

### Opcionals

| Informe           | Endpoint API                       | Descripció                     |
| ----------------- | ---------------------------------- | ------------------------------ |
| Ranking de metges | `GET /api/reports/doctor-workload` | Metges que atenen més pacients |

**SQL:**

```sql
SELECT
    ms.id,
    CONCAT(ms.first_name, ' ', ms.last_name) AS doctor_name,
    ms.specialty,
    COUNT(v.id) AS total_visits,
    COUNT(DISTINCT v.patient_id) AS unique_patients,
    RANK() OVER (ORDER BY COUNT(v.id) DESC) AS ranking
FROM MEDICAL_STAFF ms
LEFT JOIN VISITS v ON v.doctor_id = ms.id
    AND v.visit_date BETWEEN :start_date AND :end_date
GROUP BY ms.id, ms.first_name, ms.last_name, ms.specialty
ORDER BY total_visits DESC
LIMIT 10;
```

**Resposta JSON:**

```json
{
  "ranking": [
    {
      "id": 32,
      "doctor_name": "Dr. Martinez Ruiz",
      "specialty": "Cardiologia",
      "total_visits": 184,
      "unique_patients": 142,
      "ranking": 1
    },
    {
      "id": 87,
      "doctor_name": "Dra. Lopez Garcia",
      "specialty": "Pediatria",
      "total_visits": 167,
      "unique_patients": 131,
      "ranking": 2
    }
  ],
  "period": { "start": "2026-04-01", "end": "2026-05-22" }
}
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-22-44-image.png)

### Top

| Informe               | Endpoint API                               | Descripció                |
| --------------------- | ------------------------------------------ | ------------------------- |
| Malalties més comunes | `GET /api/reports/summary?report=diseases` | Diagnòstics més freqüents |

**SQL:**

```sql
SELECT
    v.diagnosis,
    COUNT(*) AS occurrences,
    COUNT(DISTINCT v.patient_id) AS affected_patients,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM VISITS v
WHERE v.diagnosis IS NOT NULL
GROUP BY v.diagnosis
ORDER BY occurrences DESC
LIMIT 15;
```

**Resposta JSON:**

```json
{
  "diseases": [
    { "diagnosis": "Hipertensió arterial", "occurrences": 215, "affected_patients": 180, "percentage": 8.24 },
    { "diagnosis": "Infecció respiratòria aguda", "occurrences": 198, "affected_patients": 172, "percentage": 7.59 },
    { "diagnosis": "Diabetes tipus 2", "occurrences": 167, "affected_patients": 143, "percentage": 6.40 }
  ]
}
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-22-59-image.png)

---

## Reports complets via API

| Report      | Endpoint                       | Filtres                                          |
| ----------- | ------------------------------ | ------------------------------------------------ |
| Summary     | `GET /api/reports/summary`     | start_date, end_date                             |
| Visites     | `GET /api/reports/visits`      | start_date, end_date, specialty, doctor_id       |
| Cirurgies   | `GET /api/reports/surgeries`   | start_date, end_date, procedure_type, surgeon_id |
| Admissions  | `GET /api/reports/admissions`  | start_date, end_date, floor_id                   |
| Medicacions | `GET /api/reports/medications` | start_date, end_date                             |

### Lògica de generació de reports (Python)

```python
@app.get("/api/reports/visits")
def get_visits_report(
    start_date: date,
    end_date: date,
    specialty: Optional[str] = None,
    doctor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(
        Visit.visit_date,
        func.count(Visit.id).label("total"),
        func.count(distinct(Visit.patient_id)).label("unique_patients")
    ).filter(Visit.visit_date.between(start_date, end_date))

    if specialty:
        query = query.join(MedicalStaff).filter(MedicalStaff.specialty == specialty)
    if doctor_id:
        query = query.filter(Visit.doctor_id == doctor_id)

    results = query.group_by(Visit.visit_date).order_by(Visit.visit_date).all()

    return {
        "report": "visits",
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "data": [
            {
                "date": r.visit_date.isoformat(),
                "total_visits": r.total,
                "unique_patients": r.unique_patients
            }
            for r in results
        ]
    }
```

### Exemple de resposta: Report de cirurgies

```json
GET /api/reports/surgeries?start_date=2026-05-01&end_date=2026-05-22

{
  "report": "surgeries",
  "period": { "start": "2026-05-01", "end": "2026-05-22" },
  "total_surgeries": 847,
  "by_type": {
    "Cirurgia general": 302,
    "Traumatologia": 215,
    "Cardiovascular": 98,
    "Oftalmologia": 134,
    "Altres": 98
  },
  "data": [
    {
      "id": 10234,
      "date": "2026-05-15",
      "patient": "Joan Puig Soler",
      "surgeon": "Dr. Garcia Lopez",
      "procedure": "Colecistectomia laparoscòpica",
      "theater": "Quiròfan 3",
      "duration_minutes": 75
    }
  ]
}
```

Captures de pantalla dels reports disponibles:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-23-55-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-24-09-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-24-27-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-24-41-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-24-53-image.png)

---

## Exportació PDF

L'informe de sumari es pot descarregar com a PDF professional (generat amb **fpdf2**) via `GET /api/reports/summary/pdf`. Requereix JWT amb rol ADMIN, DOCTOR o NURSE.

### Codi de generació PDF

```python
from fpdf import FPDF

class HospitalPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Hospital de Blanes - Informe de Sumari", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")

@app.get("/api/reports/summary/pdf")
def generate_summary_pdf(db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Obtenir dades
    floors = db.query(Floor).all()
    total_staff = db.query(MedicalStaff).count() + db.query(NursingStaff).count()
    total_patients = db.query(Patient).count()

    # Generar PDF
    pdf = HospitalPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    pdf.cell(0, 10, f"Total personal: {total_staff}", ln=True)
    pdf.cell(0, 10, f"Total pacients: {total_patients}", ln=True)
    pdf.cell(0, 10, f"Plantes actives: {len(floors)}", ln=True)

    for floor in floors:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Planta: {floor.name}", ln=True)
        pdf.set_font("Arial", "", 10)
        rooms = db.query(Room).filter(Room.floor_id == floor.id).count()
        nurses = db.query(NursingStaff).filter(NursingStaff.floor_id == floor.id).count()
        pdf.cell(0, 10, f"  Habitacions: {rooms}  |  Infermeres: {nurses}", ln=True)

    # Retornar com a resposta HTTP
    response = Response(pdf.output(dest="S").encode("latin-1"), media_type="application/pdf")
    response.headers["Content-Disposition"] = "attachment; filename=informe_hospital.pdf"
    return response
```

> Requereix token

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-25-18-image.png)

Si el tens genera aixo:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-26-22-image.png)

---

## Visualitzacions a l'escriptori

1. **Operational Reports** — Visites i cirurgies programades per a una data

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-26-51-image.png)

2. **Statistics** — Resum de planta, directori de personal, tendències de visites, ranking de metges, freqüència de malalties
3. **Advanced Reports** — Visor multi-pestanya amb 8 categories de reports, filtres i descàrrega PDF

---

## API de dashboard

`GET /api/dashboard/stats` retorna un JSON complet amb les dades del quadre de comandament:

| Camp                                             | Descripció                                |
| ------------------------------------------------ | ----------------------------------------- |
| `visits_today`                                   | Visites programades per avui              |
| `surgeries_today`                                | Cirurgies planificades per avui           |
| `active_admissions`                              | Pacients actualment hospitalitzats        |
| `total_patients`                                 | Total de pacients registrats              |
| `total_doctors` / `total_nurses` / `total_staff` | Desglossament de personal                 |
| `by_specialty`                                   | Visites agrupades per àrea mèdica         |
| `visits_trend`                                   | Historial de visites dels últims 7 dies   |
| `top_doctors`                                    | Top 5 metges per visites avui             |
| `recent_admissions`                              | Admissions actives amb habitació + planta |

### Lògica del dashboard (Python)

```python
@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    today = date.today()

    visits_today = db.query(func.count(Visit.id)) \
        .filter(func.date(Visit.visit_date) == today).scalar()

    surgeries_today = db.query(func.count(Surgery.id)) \
        .filter(func.date(Surgery.surgery_date) == today).scalar()

    active_admissions = db.query(func.count(Admission.id)) \
        .filter(Admission.discharge_date.is_(None)).scalar()

    total_patients = db.query(func.count(Patient.id)).scalar()
    total_doctors = db.query(func.count(MedicalStaff.id)).scalar()
    total_nurses = db.query(func.count(NursingStaff.id)).scalar()

    # Visites per especialitat
    by_specialty = db.query(
        MedicalStaff.specialty, func.count(Visit.id)
    ).join(Visit, Visit.doctor_id == MedicalStaff.id) \
     .filter(func.date(Visit.visit_date) == today) \
     .group_by(MedicalStaff.specialty).all()

    # Tendència últims 7 dies
    seven_days_ago = today - timedelta(days=7)
    visits_trend = db.query(
        func.date(Visit.visit_date).label("date"),
        func.count(Visit.id).label("count")
    ).filter(Visit.visit_date >= seven_days_ago) \
     .group_by(func.date(Visit.visit_date)) \
     .order_by(func.date(Visit.visit_date)).all()

    # Top 5 metges
    top_doctors = db.query(
        MedicalStaff.id,
        MedicalStaff.first_name,
        MedicalStaff.last_name,
        func.count(Visit.id).label("visits")
    ).join(Visit, Visit.doctor_id == MedicalStaff.id) \
     .filter(func.date(Visit.visit_date) == today) \
     .group_by(MedicalStaff.id) \
     .order_by(func.count(Visit.id).desc()) \
     .limit(5).all()

    return {
        "visits_today": visits_today or 0,
        "surgeries_today": surgeries_today or 0,
        "active_admissions": active_admissions or 0,
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_nurses": total_nurses,
        "total_staff": total_doctors + total_nurses,
        "by_specialty": {s: c for s, c in by_specialty},
        "visits_trend": [{"date": str(d), "count": c} for d, c in visits_trend],
        "top_doctors": [
            {"id": d.id, "name": f"{d.first_name} {d.last_name}", "visits": d.visits}
            for d in top_doctors
        ]
    }
```

### Exemple de resposta del dashboard

```json
{
  "visits_today": 143,
  "surgeries_today": 12,
  "active_admissions": 47,
  "total_patients": 50123,
  "total_doctors": 100,
  "total_nurses": 200,
  "total_staff": 300,
  "by_specialty": {
    "Cardiologia": 28,
    "Pediatria": 35,
    "Traumatologia": 22,
    "Medicina General": 58
  },
  "visits_trend": [
    {"date": "2026-05-16", "count": 118},
    {"date": "2026-05-17", "count": 132},
    {"date": "2026-05-18", "count": 97},
    {"date": "2026-05-19", "count": 145},
    {"date": "2026-05-20", "count": 128},
    {"date": "2026-05-21", "count": 156},
    {"date": "2026-05-22", "count": 143}
  ],
  "top_doctors": [
    {"id": 32, "name": "Dr. Martinez Ruiz", "visits": 18},
    {"id": 87, "name": "Dra. Lopez Garcia", "visits": 15},
    {"id": 45, "name": "Dr. Ferrer Costa", "visits": 14},
    {"id": 12, "name": "Dr. Vidal Serra", "visits": 12},
    {"id": 73, "name": "Dra. Roca Puig", "visits": 11}
  ],
  "recent_admissions": [
    {"patient": "Maria Garcia", "room": 204, "floor": "Planta 2", "admitted_at": "2026-05-22T09:30:00"}
  ]
}
```

---

## Funcionalitats obligatòries implementades

- ✅ Donada una planta: habitacions, quiròfans i personal d'infermeria
- ✅ Informe de tot el personal de l'hospital
- ✅ Informe de nombre de visites ateses per dia

## Funcionalitats opcionals implementades

- ✅ Ranking de metges que atenen més pacients

## Funcionalitats top implementades

- ✅ Malalties més comunes
