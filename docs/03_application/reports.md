# Queries and Reports

## Available reports

All accessible from the **Reports** / **Statistics** sections of the desktop app, or via the API.

### Required

| Report | API endpoint | Description |
|--------|-------------|-------------|
| Floor summary | `GET /api/reports/floor-summary/{id}` | Rooms, operating theaters, and nurses on a given floor |
| Staff directory | `GET /api/reports/staff-directory` | All hospital staff with roles |
| Daily visits | `GET /api/reports/daily-visits?date=X` | Number of visits attended per day |

### Optional

| Report | API endpoint |
|--------|-------------|
| Doctor ranking | `GET /api/reports/top-doctors?date=X` | Doctors ranked by number of patients seen |

### Top

| Report | API endpoint |
|--------|-------------|
| Most common diagnoses | `GET /api/reports/common-diagnoses` | Disease frequency ranking |

## PDF export

Any report can be downloaded as a professional PDF (generated with fpdf2) via `GET /api/reports/{type}/pdf`. The PDF includes KPIs, data tables, and a footer with the generation timestamp.

## Desktop views

- **Queries & Reports** tab — Daily visits and surgeries
- **Statistics** tab — Floor overview, staff directory, visit trends, doctor rankings, disease rankings
- **Advanced Reports** tab — Multi-tab view with filters and PDF download
