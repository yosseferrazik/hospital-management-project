# 9. PRG — Bloc d'Exportació de Dades

## 9.1 Visió General

El mòdul d'exportació de dades permet extreure les visites mèdiques en formats interoperables (XML i JSON), validar-les contra esquemes formals, i enviar-les automàticament a l'API de la Seguretat Social. A més, inclou un dashboard web amb gràfics en temps real basat en Chart.js i connectivitat opcional amb PowerBI Desktop.

---

## 9.2 Exportació XML / JSON

### 9.2.1 Endpoints

Les visites entre dues dates es poden exportar en format XML o JSON, permetent la interoperabilitat amb sistemes externs:

```bash
# Exportació en format XML
GET /api/export/visits?start_date=2026-05-01&end_date=2026-05-20&format=xml

# Exportació en format JSON
GET /api/export/visits?start_date=2026-05-01&end_date=2026-05-20&format=json
```

En enviar la sol·licitud GET a qualsevol dels dos endpoints, el servidor retorna el fitxer corresponent com a descàrrega directa (Content-Disposition: attachment).

### 9.2.2 Exemple de sortida XML

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<visits>
    <visit>
        <visit_id>1</visit_id>
        <visit_date>2026-05-15</visit_date>
        <doctor>
            <name>Dr. Martínez</name>
            <license_number>12345</license_number>
        </doctor>
        <patient>
            <dni>12345678A</dni>
            <first_name>Joan</first_name>
            <last_name>Garcia</last_name>
            <health_card>CAT123456789</health_card>
        </patient>
    </visit>
    <visit>
        <visit_id>2</visit_id>
        <visit_date>2026-05-15</visit_date>
        <doctor>
            <name>Dra. López</name>
            <license_number>12346</license_number>
        </doctor>
        <patient>
            <dni>87654321B</dni>
            <first_name>Maria</first_name>
            <last_name>Puig</last_name>
            <health_card>CAT987654321</health_card>
        </patient>
    </visit>
</visits>
```

### 9.2.3 Exemple de sortida JSON

```json
{
  "visits": [
    {
      "visit_id": 1,
      "visit_date": "2026-05-15",
      "doctor": {
        "name": "Dr. Martínez",
        "license_number": "12345"
      },
      "patient": {
        "dni": "12345678A",
        "first_name": "Joan",
        "last_name": "Garcia",
        "health_card": "CAT123456789"
      }
    },
    {
      "visit_id": 2,
      "visit_date": "2026-05-15",
      "doctor": {
        "name": "Dra. López",
        "license_number": "12346"
      },
      "patient": {
        "dni": "87654321B",
        "first_name": "Maria",
        "last_name": "Puig",
        "health_card": "CAT987654321"
      }
    }
  ]
}
```

### 9.2.4 Dades incloses a l'exportació

| Camp                  | Descripció                           | Tipus      |
|-----------------------|--------------------------------------|------------|
| `visit_id`            | Identificador únic de la visita      | Integer    |
| `visit_date`          | Data de la visita (YYYY-MM-DD)       | Date       |
| `doctor.name`         | Nom complet del metge                | String     |
| `doctor.license_number` | Número de col·legiat               | String     |
| `patient.dni`         | DNI del pacient                      | String     |
| `patient.first_name`  | Nom del pacient                      | String     |
| `patient.last_name`   | Cognoms del pacient                  | String     |
| `patient.health_card` | Targeta sanitària individual (TSI)   | String     |

### 9.2.5 Format i indentació

| Format | Indentació | Implementació                       |
|--------|------------|-------------------------------------|
| XML    | 2 espais   | `xml.dom.minidom.toprettyxml()`     |
| JSON   | 2 espais   | `json.dumps(data, indent=2)`        |

---

## 9.3 Esquemes de validació

Ambdós formats estan validats contra esquemes per garantir la correctesa estructural i semàntica de les dades exportades.

### 9.3.1 XSD (XML Schema Definition)

**Fitxer:** `server/src/app/schemas/visits.xsd`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://hospitaldeblanes.cat/export/visits"
           xmlns="http://hospitaldeblanes.cat/export/visits"
           elementFormDefault="qualified">

    <xs:element name="visits">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="visit" maxOccurs="unbounded">
                    <xs:complexType>
                        <xs:all>
                            <xs:element name="visit_id" type="xs:positiveInteger"/>
                            <xs:element name="visit_date" type="xs:date"/>
                            <xs:element name="doctor">
                                <xs:complexType>
                                    <xs:all>
                                        <xs:element name="name" type="xs:string"/>
                                        <xs:element name="license_number" type="xs:string"/>
                                    </xs:all>
                                </xs:complexType>
                            </xs:element>
                            <xs:element name="patient">
                                <xs:complexType>
                                    <xs:all>
                                        <xs:element name="dni" type="xs:string"/>
                                        <xs:element name="first_name" type="xs:string"/>
                                        <xs:element name="last_name" type="xs:string"/>
                                        <xs:element name="health_card" type="xs:string"/>
                                    </xs:all>
                                </xs:complexType>
                            </xs:element>
                        </xs:all>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>
```

### 9.3.2 JSON Schema

**Fitxer:** `server/src/app/schemas/visits.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Visits Export",
  "type": "object",
  "required": ["visits"],
  "properties": {
    "visits": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["visit_id", "visit_date", "doctor", "patient"],
        "properties": {
          "visit_id": { "type": "integer", "minimum": 1 },
          "visit_date": { "type": "string", "format": "date" },
          "doctor": {
            "type": "object",
            "required": ["name", "license_number"],
            "properties": {
              "name": { "type": "string" },
              "license_number": { "type": "string" }
            }
          },
          "patient": {
            "type": "object",
            "required": ["dni", "first_name", "last_name", "health_card"],
            "properties": {
              "dni": { "type": "string", "pattern": "^[0-9]{8}[A-Z]$" },
              "first_name": { "type": "string" },
              "last_name": { "type": "string" },
              "health_card": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

### 9.3.3 Implementació de la validació en Python

```python
# server/src/app/services/export_service.py
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from jsonschema import validate, ValidationError
from lxml import etree


def validate_xml(xml_string: str, xsd_path: str) -> bool:
    xsd_doc = etree.parse(xsd_path)
    xsd_schema = etree.XMLSchema(xsd_doc)
    xml_doc = etree.fromstring(xml_string.encode("utf-8"))
    return xsd_schema.validate(xml_doc)


def validate_json(json_string: str, schema_path: str) -> bool:
    with open(schema_path) as f:
        schema = json.load(f)
    data = json.loads(json_string)
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError:
        return False
```

### 9.3.4 Exemple d'ús amb errors de validació

Si s'intenta validar un XML amb un `visit_id` negatiu o un JSON amb un `dni` que no compleix el patró `^[0-9]{8}[A-Z]$`, l'esquema rebutja el document i retorna un error descriptiu.

---

## 9.4 API Seguretat Social

### 9.4.1 Endpoint d'enviament

Les visites d'un període es poden exportar i enviar automàticament a l'API externa de la Seguretat Social, automatitzant la tramitació administrativa:

```http
POST /api/export/send
Content-Type: application/json

{
  "start_date": "2026-05-01",
  "end_date": "2026-05-20",
  "format": "xml"
}
```

### 9.4.2 Flux de processament

L'endpoint `POST /api/export/send` executa el següent flux:

1. **Generació** — Crea el fitxer XML o JSON per al període indicat consultant la base de dades.
2. **Validació** — Valida el fitxer generat contra l'esquema corresponent (XSD o JSON Schema).
3. **Enviament** — Envia el fitxer a l'API externa configurada mitjançant una petició HTTP amb autenticació Basic Auth.
4. **Resposta** — Retorna l'estat de la resposta de l'API externa (codi HTTP, cos, etc.).

### 9.4.3 Implementació de l'enviament

```python
import requests
from requests.auth import HTTPBasicAuth


def send_to_external_api(export_data: str, file_format: str) -> dict:
    url = os.getenv("EXTERNAL_API_URL")
    username = os.getenv("EXTERNAL_API_USERNAME")
    password = os.getenv("EXTERNAL_API_PASSWORD")

    headers = {"Content-Type": f"application/{file_format}"}
    auth = HTTPBasicAuth(username, password)

    response = requests.post(
        url,
        data=export_data,
        headers=headers,
        auth=auth,
        timeout=30,
    )

    return {
        "status_code": response.status_code,
        "response_body": response.text,
        "success": response.ok,
    }
```

### 9.4.4 Configuració (variables d'entorn)

Fitxer `/etc/hms.env`:

| Variable                 | Descripció                                | Exemple                                        |
|--------------------------|-------------------------------------------|------------------------------------------------|
| `EXTERNAL_API_URL`       | URL de l'API de la Seguretat Social       | `https://api.seg-social.es/export`             |
| `EXTERNAL_API_USERNAME`  | Usuari per a autenticació Basic           | `api_user`                                     |
| `EXTERNAL_API_PASSWORD`  | Contrasenya per a autenticació Basic      | (emmagatzemada de forma segura)                |

### 9.4.5 Exemple de resposta

```json
{
  "success": true,
  "status_code": 200,
  "response_body": "OK",
  "export_format": "xml",
  "visit_count": 145,
  "period": {
    "start": "2026-05-01",
    "end": "2026-05-20"
  }
}
```

---

## 9.5 Dashboard

El sistema ofereix dues opcions per a la visualització gràfica de dades: un dashboard web integrat amb Chart.js i connectivitat opcional amb PowerBI Desktop.

### 9.5.1 Opció 1: Chart.js (dashboard web)

Dashboard web integrat a l'API que proporciona una visió gràfica en temps real de les dades de l'hospital.

**URL:** `http://localhost:5000/api/dashboard/view`

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/export/2026-05-22-18-34-05-image.png)

#### Endpoint de dades

```http
GET /api/dashboard/stats
```

**Exemple de resposta JSON:**

```json
{
  "visits_today": 42,
  "surgeries_today": 5,
  "active_admissions": 28,
  "total_patients": 1580,
  "total_doctors": 24,
  "total_nurses": 56,
  "total_staff": 120,
  "by_specialty": {
    "Cardiologia": 15,
    "Pediatria": 10,
    "Traumatologia": 8,
    "Medicina General": 20,
    "Neurologia": 5
  },
  "visits_trend": [
    {"date": "2026-05-14", "visits": 38},
    {"date": "2026-05-15", "visits": 42},
    {"date": "2026-05-16", "visits": 35},
    {"date": "2026-05-17", "visits": 40},
    {"date": "2026-05-18", "visits": 44},
    {"date": "2026-05-19", "visits": 39},
    {"date": "2026-05-20", "visits": 42}
  ],
  "top_doctors": [
    {"name": "Dr. Martínez", "visits": 120},
    {"name": "Dra. López", "visits": 98},
    {"name": "Dr. Garcia", "visits": 85},
    {"name": "Dra. Rodríguez", "visits": 72},
    {"name": "Dr. Fernández", "visits": 65}
  ],
  "recent_admissions": [
    {"patient": "Joan Garcia", "room": "201", "date": "2026-05-20"},
    {"patient": "Maria Puig", "room": "105", "date": "2026-05-20"}
  ]
}
```

#### Gràfics inclosos al dashboard Chart.js

| Gràfic                   | Tipus       | Dades utilitzades          |
|--------------------------|-------------|----------------------------|
| Visites avui             | Mètrica     | `visits_today`             |
| Cirurgies avui           | Mètrica     | `surgeries_today`          |
| Admissions actives       | Mètrica     | `active_admissions`        |
| Visites per especialitat | Gràfic de barres | `by_specialty`        |
| Tendència 7 dies         | Gràfic de línies  | `visits_trend`        |
| Top 5 metges             | Gràfic de barres horitzontals | `top_doctors` |

#### Implementació del dashboard Chart.js

```javascript
// server/src/app/templates/dashboard.html
fetch('/api/dashboard/stats')
    .then(res => res.json())
    .then(data => {
        // Gràfic de visites per especialitat
        new Chart(document.getElementById('specialtyChart'), {
            type: 'bar',
            data: {
                labels: Object.keys(data.by_specialty),
                datasets: [{
                    label: 'Visites per especialitat',
                    data: Object.values(data.by_specialty),
                    backgroundColor: '#4f81bd'
                }]
            }
        });

        // Gràfic de tendència 7 dies
        new Chart(document.getElementById('trendChart'), {
            type: 'line',
            data: {
                labels: data.visits_trend.map(d => d.date.slice(-5)),
                datasets: [{
                    label: 'Visites (7 dies)',
                    data: data.visits_trend.map(d => d.visits),
                    borderColor: '#c0504d',
                    fill: false
                }]
            }
        });
    });
```

### 9.5.2 Opció 2: PowerBI Desktop (connectivitat opcional)

Per a usuaris que necessitin anàlisi avançada, el dashboard es pot connectar a PowerBI Desktop:

1. Obrir **PowerBI Desktop**.
2. **Get Data** → **Web**.
3. Introduir la URL: `http://192.168.4.254:5000/api/dashboard/stats`.
4. PowerBI auto-detecta l'estructura JSON i l'expandeix en columnes.
5. Utilitzar `by_specialty` per al desglossament per àrea i `visits_trend` per a gràfics temporals.
6. Programar actualitzacions periòdiques a PowerBI Service per tenir dades sempre actualitzades.

---

## 9.6 Funcionalitats obligatòries implementades

- **EO1** ✅ Descàrrega de visites entre dues dates amb ID, dia, metge i dades del pacient.
- **EO2** ✅ Format XML i JSON amb indentació (tabulacions).
- **EO3** ✅ XSD i JSON Schema per als fitxers generats.

## 9.7 Funcionalitats opcionals implementades

- **EO4** ✅ Connexió a API externa (Seguretat Social) amb autenticació Basic Auth.
- **EO5** ✅ Dashboard amb gràfics (Chart.js / PowerBI) amb múltiples visualitzacions.
