# Queries and Reports

## Available reports

All accessible from the **Advanced Reports** tab of the desktop app, or via the API.

| Report | API endpoint | Filters |
|--------|-------------|---------|
| Summary | `GET /api/reports/summary` | start_date, end_date |
| Visits | `GET /api/reports/visits` | start_date, end_date, specialty, doctor_id |
| Surgeries | `GET /api/reports/surgeries` | start_date, end_date, procedure_type, surgeon_id |
| Admissions | `GET /api/reports/admissions` | start_date, end_date, floor_id |
| Medications | `GET /api/reports/medications` | start_date, end_date |
| Financial | `GET /api/reports/financial` | start_date, end_date |
| Radiology | `GET /api/reports/radiology` | start_date, end_date, status |
| Doctor Workload | `GET /api/reports/doctor-workload` | start_date, end_date |

## PDF export

The summary report can be downloaded as a professional PDF (generated with fpdf2) via `GET /api/reports/summary/pdf`. Requires JWT with ADMIN, DOCTOR, or NURSE role. Includes KPIs, data tables, and a footer with the generation timestamp.

## Desktop views

- **Operational Reports** tab — Scheduled visits and surgeries for a given date
- **Statistics** tab — Floor overview, staff directory, visit trends, doctor rankings, disease frequency
- **Advanced Reports** tab — Multi-tab view with 8 report categories, filters, and PDF download
