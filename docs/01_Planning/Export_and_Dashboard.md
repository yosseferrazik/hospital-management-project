# Bloque de Exportación de Datos y Cuadro de Mando

## 1. Exportación de Visitas

El sistema permite descargar las visitas hospitalarias en un rango de fechas en formato XML o JSON, validados contra un esquema XSD / JSON Schema.

### Endpoint

```
GET /api/export/visits?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&format=xml|json
```

- **start_date**, **end_date**: obligatorios, formato ISO (YYYY-MM-DD).
- **format**: opcional, `xml` o `json` (por defecto `json`).
- **Respuesta**: descarga del archivo con `Content-Disposition: attachment`.

### Esquemas de validación

- **XSD**: `server/src/app/schemas/visits.xsd`
- **JSON Schema**: `server/src/app/schemas/visits.schema.json`

### Estructura del archivo exportado (XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<visits>
  <visit>
    <visit_id>1</visit_id>
    <date>2026-05-19</date>
    <doctor>
      <name>Dr. Nombre Apellido</name>
      <license>DOC-123456</license>
    </doctor>
    <patient>
      <dni>12345678A</dni>
      <first_name>Nombre</first_name>
      <last_name>Apellido</last_name>
      <health_card>1234567890</health_card>
    </patient>
  </visit>
</visits>
```

## 2. Envío a API Externa

Para el volcado mensual a la Seguridad Social (API externa):

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

### Configuración (variables de entorno)

| Variable | Descripción |
|----------|-------------|
| `EXTERNAL_API_URL` | URL de la API externa |
| `EXTERNAL_API_USERNAME` | Usuario para autenticación HTTP Basic |
| `EXTERNAL_API_PASSWORD` | Contraseña para autenticación HTTP Basic |

## 3. Cuadro de Mando (Dashboard)

Endpoint JSON consumible por Power BI o cualquier herramienta de BI:

```
GET /api/dashboard/stats
```

### Respuesta

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

- **total_visits**: visitas del día actual.
- **by_specialty**: desglose por área médica (especialidad del doctor).

## 4. Dependencias

Añadidas al `requirements.txt`:

- `jsonschema` — validación JSON Schema
- `xmlschema` — validación XSD
- `requests` — llamadas HTTP a API externa

## 5. Esquema de bases de datos

Se ha añadido el campo `health_card` (`VARCHAR(50)`) a la tabla `patients` para almacenar el número de tarjeta sanitaria / SIP del paciente.
