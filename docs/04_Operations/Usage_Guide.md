# Usage Guide — Hospital Management System

## API Endpoints

Base URL: `http://localhost:5000/api`

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-05-18T10:00:00+00:00"
}
```

### Authentication Flow

The authentication flow works as follows:
1. Client sends credentials to `POST /api/auth/login`
2. Backend validates against database (bcrypt)
3. JWT token returned to client
4. Client stores token in session and sends it as `Authorization: Bearer <token>`

#### Register

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "doctor1", "password": "secret", "staff_id": 1, "role": "DOCTOR"}'
```

#### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "yossef", "password": "ChangeMePleaseChange!"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

Then use the token for protected endpoints:

```bash
curl -X POST http://localhost:5000/api/maintenance/patients \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"national_id": "12345678A", "first_name": "John", "last_name": "Doe", "birth_date": "1990-01-01"}'
```

---

### CRUD Endpoints (all return JSON)

| Endpoint                    | Methods                         | Description                |
|-----------------------------|---------------------------------|----------------------------|
| `/api/patients`             | GET, POST                       | List / create patients     |
| `/api/patients/<id>`        | GET, PUT, DELETE                | Read / update / delete     |
| `/api/staff`                | GET                             | List all staff             |
| `/api/staff/<id>`           | GET, PUT, DELETE                | Read / update / delete     |
| `/api/staff/medical`        | POST                            | Create medical staff       |
| `/api/staff/nursing`        | POST                            | Create nursing staff       |
| `/api/staff/general`        | POST                            | Create general staff       |
| `/api/floors`               | GET, POST                       | List / create floors       |
| `/api/rooms`                | GET, POST                       | List / create rooms        |
| `/api/visits`               | GET, POST                       | List / create visits       |
| `/api/visits/scheduled/<date>` | GET                          | Visits scheduled on date   |
| `/api/surgeries`            | GET, POST                       | List / create surgeries    |
| `/api/surgeries/by_date/<date>` | GET                        | Surgeries on date          |
| `/api/medications`          | GET, POST                       | List / create medications  |
| `/api/prescriptions`        | GET, POST                       | List / create prescriptions|
| `/api/admissions`           | GET, POST                       | List / create admissions   |
| `/api/medical_specialties`  | GET, POST                       | List / create specialties  |
| `/api/operating_theaters`   | GET, POST                       | List / create theaters     |
| `/api/medical_devices`      | GET, POST                       | List / create devices      |
| `/api/radiology_exams`      | GET, POST                       | List / create exams        |
| `/api/pharmacy_dispensations` | GET, POST                     | List / create dispensations|
| `/api/dispensation_items`   | GET, POST                       | List / create items        |
| `/api/scheduled_appointments` | GET, POST                     | List / create appointments |
| `/api/surgery_assistants`   | GET, POST                       | List / create assistants   |

### Reports Endpoints (JWT required — ADMIN, DOCTOR, NURSE)

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/api/reports/summary` | Summary report (totals, activity, occupancy, top diagnoses, surgeries by type) |
| GET | `/api/reports/visits` | Visit report grouped by date |
| GET | `/api/reports/surgeries` | Surgery report grouped by date |
| GET | `/api/reports/admissions` | Admission report with stay duration |
| GET | `/api/reports/medications` | Prescribed medications grouped by name |
| GET | `/api/reports/financial` | Pharmacy dispensation costs |
| GET | `/api/reports/radiology` | Radiology exam counts by type |
| GET | `/api/reports/doctor-workload` | Physician visit/surgery counts |
| GET | `/api/reports/summary/pdf` | **Download** a 3-page PDF report with KPIs, clinical activity, and financial data |

All report endpoints accept optional `start_date` and `end_date` query parameters (ISO format, e.g. `?start_date=2026-01-01&end_date=2026-03-31`).

#### PDF Download Example

```bash
curl -o report.pdf \
  -H "Authorization: Bearer <token>" \
  "http://localhost:5000/api/reports/summary/pdf?start_date=2026-01-01&end_date=2026-05-19"
```

### Audit Log Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/api/audit-logs` | List logs with optional `table`, `action`, `user_id`, `start_date`, `end_date`, `page`, `per_page` query params |
| GET | `/api/audit-logs/diagnostics` | Check PostgreSQL trigger status and log count |
| POST | `/api/audit-logs/test` | Create a test audit entry (INSERT+UPDATE+DELETE on a temp record) |
| GET | `/api/audit-logs/retention` | Get current retention setting in days |
| DELETE | `/api/audit-logs/cleanup` | Delete logs older than `before` query param (ISO date) |

### Export and Dashboard Endpoints

| Endpoint                                           | Description                                  |
|----------------------------------------------------|----------------------------------------------|
| `GET /api/export/visits?start_date=&end_date=&format=` | Download visits in XML/JSON (no auth)    |
| `POST /api/export/send`                            | Send visits to external API                  |
| `GET /api/dashboard/stats`                         | Today's visits by specialty (for Power BI)   |
| `GET /api/dashboard/view`                          | Interactive web dashboard (Chart.js)         |
| `GET /`                                            | Redirects to `/api/dashboard/view`           |

### Protected Endpoints (require JWT token)

| Endpoint                                           | Description                       |
|----------------------------------------------------|-----------------------------------|
| `POST /api/maintenance/staff/medical`              | Create medical staff              |
| `POST /api/maintenance/staff/nursing`              | Create nursing staff              |
| `POST /api/maintenance/staff/general`              | Create general staff              |
| `POST /api/maintenance/patients`                   | Create patient                    |
| `PUT /api/maintenance/nursing/assign`              | Assign nurse to doctor or floor   |
| `GET /api/maintenance/surgeries?date=YYYY-MM-DD`  | Surgeries by date                 |
| `GET /api/maintenance/visits/scheduled?date=YYYY-MM-DD` | Scheduled visits by date    |
| `POST /api/dummy/generate`                         | Generate test data                |
| `DELETE /api/dummy/cleanup`                        | Remove test data                  |

---

## CRUD Examples

### Create a patient

```bash
curl -X POST http://localhost:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "national_id": "12345678X",
    "first_name": "Maria",
    "last_name": "Garcia",
    "birth_date": "1985-06-15",
    "gender": "FEMALE",
    "phone": "+34-600000001",
    "blood_type": "A+"
  }'
```

Response: `{"patient_id": 1}` (HTTP 201)

### List all patients

```bash
curl http://localhost:5000/api/patients
```

### Get a specific patient

```bash
curl http://localhost:5000/api/patients/1
```

### Get surgeries by date

```bash
curl "http://localhost:5000/api/surgeries/by_date/2026-05-18"
```

### Get scheduled appointments

```bash
curl "http://localhost:5000/api/visits/scheduled/2026-05-18"
```

### Create medical staff (requires JWT)

```bash
curl -X POST http://localhost:5000/api/maintenance/staff/medical \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "national_id": "87654321B",
    "first_name": "Carlos",
    "last_name": "Mendez",
    "birth_date": "1975-03-20",
    "specialty_id": 1,
    "license_number": "LIC-123456"
  }'
```

### Download PDF Report (requires JWT — ADMIN, DOCTOR, or NURSE)

```bash
curl -o hospital_report.pdf \
  -H "Authorization: Bearer <token>" \
  "http://localhost:5000/api/reports/summary/pdf?start_date=2026-01-01&end_date=2026-05-19"
```

---

## Desktop Client

The Tkinter desktop application provides a GUI for all CRUD operations.

### Navigation

| Menu Item           | Description                                     |
|---------------------|-------------------------------------------------|
| Dashboard           | Overview: record counts, today's visits/surgeries |
| Maintenance         | Register staff, patients, assign nurses         |
| Data Workspace      | Browse and edit all entities (CRUD)             |
| Operational Reports | View visits and surgeries filtered by date      |
| Statistics          | Hospital operational metrics (use cases)        |
| Advanced Reports    | Multi-section PDF report with download button   |
| Dummy Data          | Generate or clean up test data                  |

### Login

Default admin credentials (after running `initial_script.sql`):
- **Username:** `yossef`
- **Password:** `ChangeMePleaseChange!`

---

## Generating Test Data

From the desktop client: navigate to **Dummy Data** → enter patient count → click **Generate**.

From the API:

```bash
curl -X POST http://localhost:5000/api/dummy/generate \
  -H "Authorization: Bearer <token>"
```

To clean up:

```bash
curl -X DELETE http://localhost:5000/api/dummy/cleanup \
  -H "Authorization: Bearer <token>"
```

> Generated data now includes realistic Spanish medical content: 16 specialties with 160 diagnoses, 25 medications with real dosages, 26 surgical procedures, 24 radiology exam types with clinical findings, and coherent diagnosis-prescription-specialty relationships.
