# Data Export and Dashboard Module

## 1. Visit Export

The system allows downloading hospital visits within a date range in XML or JSON format, validated against an XSD / JSON Schema.

### Endpoint

```
GET /api/export/visits?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&format=xml|json
```

- **start_date**, **end_date**: required, ISO format (YYYY-MM-DD).
- **format**: optional, `xml` or `json` (default `json`).
- **Response**: file download with `Content-Disposition: attachment`.

### Validation schemas

- **XSD**: `server/src/app/schemas/visits.xsd`
- **JSON Schema**: `server/src/app/schemas/visits.schema.json`

### Exported file structure (XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<visits>
  <visit>
    <visit_id>1</visit_id>
    <date>2026-05-19</date>
    <doctor>
      <name>Dr. FirstName LastName</name>
      <license>DOC-123456</license>
    </doctor>
    <patient>
      <dni>12345678A</dni>
      <first_name>FirstName</first_name>
      <last_name>LastName</last_name>
      <health_card>1234567890</health_card>
    </patient>
  </visit>
</visits>
```

## 2. External API Submission

For the monthly dump to Social Security (external API):

### Endpoint

```
POST /api/export/send
Content-Type: application/json

{
  "start_date": "2026-05-01",
  "end_date": "2026-05-31",
  "format": "xml"
}
```

### Configuration (environment variables)

| Variable | Description |
|----------|-------------|
| `EXTERNAL_API_URL` | External API URL |
| `EXTERNAL_API_USERNAME` | Username for HTTP Basic authentication |
| `EXTERNAL_API_PASSWORD` | Password for HTTP Basic authentication |

## 3. Dashboard

### 3.1 Interactive Web Dashboard

The system includes a visual web dashboard accessible from the browser:

```
GET /api/dashboard/view
```

It also automatically redirects from the root: `http://localhost:5000/`

Features:
- KPI: total visits today and number of specialties
- Bar chart: visits by medical specialty
- Donut chart: percentage distribution
- Detailed table with percentages
- Auto-refresh every 60 seconds
- Professional dark theme

Technology: HTML + Chart.js (CDN), no additional dependencies.

### 3.2 JSON API (for Power BI)

JSON endpoint consumable by Power BI or any BI tool:

```
GET /api/dashboard/stats
```

No authentication required to facilitate Power BI integration.

#### Response

```json
{
  "date": "2026-05-19",
  "total_visits": 42,
  "by_specialty": [
    { "specialty": "Cardiology", "count": 12 },
    { "specialty": "Traumatology", "count": 8 }
  ]
}
```

- **total_visits**: current day visits.
- **by_specialty**: breakdown by medical area (doctor's specialty).

#### Power BI

1. Power BI Desktop → **Get data** → **Web**
2. URL: `http://localhost:5000/api/dashboard/stats`
3. Power BI auto-detects JSON and expands it into columns
4. For specialty breakdown: expand `by_specialty` → **Expand to New Rows**

## 4. Dependencies

Added to `requirements.txt`:

- `jsonschema` — JSON Schema validation
- `xmlschema` — XSD validation
- `requests` — HTTP calls to external API

## 5. Database schema

Added the `health_card` (`VARCHAR(50)`) field to the `patients` table to store the patient's health card / SIP number.
