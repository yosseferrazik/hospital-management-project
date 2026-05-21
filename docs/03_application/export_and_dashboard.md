# Data Export and Dashboard

## XML / JSON Export

Visits between two dates can be exported in XML or JSON format:

```bash
GET /api/export/visits?start_date=2026-05-01&end_date=2026-05-20&format=xml
GET /api/export/visits?start_date=2026-05-01&end_date=2026-05-20&format=json
```

The export includes: visit ID, date, doctor name + license number, patient DNI + name + health card.

Both formats are validated against schemas:
- **XSD**: `server/src/app/schemas/visits.xsd`
- **JSON Schema**: `server/src/app/schemas/visits.schema.json`

## Social Security API

At the end of each month, visits are exported to XML and sent to the Social Security API:

```
POST /api/export/send
```

This endpoint:
1. Generates the XML file for the current month
2. Sends it to the configured external API with Basic Auth
3. Returns the API response status

The external API URL, username, and password are configured via environment variables (`EXTERNAL_API_URL`, `EXTERNAL_API_USERNAME`, `EXTERNAL_API_PASSWORD`).

## Dashboard

We built a web-based dashboard using Chart.js (instead of PowerBI, which would require paid licenses):

**URL:** `http://localhost:5000/api/dashboard/view`

**API:** `GET /api/dashboard/stats` returns:

| Field | Description |
|-------|-------------|
| `visits_today` | Visits scheduled for today |
| `surgeries_today` | Surgeries planned for today |
| `active_admissions` | Currently hospitalised patients |
| `total_patients` | Total registered |
| `total_doctors` / `total_nurses` | Staff breakdown |
| `by_specialty` | Visits grouped by medical area |
| `visits_trend` | 7-day visit history |
| `top_doctors` | Top 5 doctors by visits today |
| `recent_admissions` | Active admissions with room + floor |

### Connecting PowerBI (optional)

1. PowerBI Desktop → **Get Data** → **Web**
2. URL: `http://localhost:5000/api/dashboard/stats`
3. PowerBI auto-detects the JSON and expands it
4. Use `by_specialty` for area breakdown, `visits_trend` for time charts

## Format

- XML: indented with 2-space tabs (via `minidom.toprettyxml`)
- JSON: indented with 2-space indent (via `json.dumps(indent=2)`)
