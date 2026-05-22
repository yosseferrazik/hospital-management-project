# 9. PRG — Bloc d'Exportació de Dades

## Exportació XML/JSON

Les visites entre dues dates es poden exportar en format XML o JSON, permetent la interoperabilitat amb sistemes externs:

```bash
GET /api/export/visits?start_date=2026-05-01&end_date=2026-05-20&format=xml
GET /api/export/visits?start_date=2026-05-01&end_date=2026-05-20&format=json
```

Al enviar la solicitud get a cualsevol dels 2 descarrega l'arxiu demanat.

Captures del procés d'exportació:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/export/2026-05-22-18-31-13-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/export/2026-05-22-18-31-39-image.png)

### Dades incloses a l'exportació

- Identificador de visita
- Data de la visita
- Metge que ha atès (nom + número de col·legiat)
- Dades del pacient: DNI, nom, cognoms, targeta sanitària

### Format i indentació

- **XML:** indentat amb 2 espais (via `minidom.toprettyxml`)
- **JSON:** indentat amb 2 espais (via `json.dumps(indent=2)`)

## Esquemes de validació

Ambdós formats estan validats contra esquemes per garantir la correctesa de les dades exportades:

- **XSD:** `server/src/app/schemas/visits.xsd`
- **JSON Schema:** `server/src/app/schemas/visits.schema.json`

## API Seguretat Social

Les visites d'un període es poden exportar i enviar a l'API de la Seguretat Social, automatitzant la tramitació administrativa:

```json
POST /api/export/send
Body: { "start_date": "2026-05-01", "end_date": "2026-05-20", "format": "xml" }
```

Aquest endpoint:

1. Genera el fitxer XML o JSON per al període indicat
2. L'envia a l'API externa configurada amb autenticació Basic Auth
3. Retorna l'estat de la resposta de l'API

**Configuració** (variables d'entorn a `/etc/hms.env`):

| Variable | Descripció |
|----------|-----------|
| `EXTERNAL_API_URL` | URL de l'API de la Seguretat Social |
| `EXTERNAL_API_USERNAME` | Usuari per a autenticació Basic |
| `EXTERNAL_API_PASSWORD` | Contrasenya per a autenticació Basic |

## Dashboard (PowerBI / Chart.js)

### Opció 1: Chart.js (web)

Dashboard web integrat a l'API que proporciona una visió gràfica en temps real de les dades de l'hospital:

**URL:** `http://localhost:5000/api/dashboard/view`

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/export/2026-05-22-18-34-05-image.png)

**Dades:** `GET /api/dashboard/stats` retorna JSON amb:

- Visites avui, cirurgies avui, admissions actives
- Total pacients, metges, infermeres, staff
- Visites per especialitat (by_specialty)
- Tendència de visites 7 dies (visits_trend)
- Top 5 metges (top_doctors)
- Admissions recents (recent_admissions)

### Opció 2: PowerBI Desktop (connectivitat opcional)

1. PowerBI Desktop → **Get Data** → **Web**
2. URL: `http://192.168.4.254:5000/api/dashboard/stats`
3. PowerBI auto-detecta el JSON i l'expandeix
4. Utilitzar `by_specialty` per al desglossament per àrea, `visits_trend` per a gràfics temporals

## Funcionalitats obligatòries implementades

- ✅ Descàrrega de visites entre dues dates amb ID, dia, metge i dades del pacient
- ✅ Format XML i JSON amb indentació (tabulacions)
- ✅ XSD i JSON Schema per als fitxers generats

## Funcionalitats opcionals implementades

- ✅ Connexió a API externa (Seguretat Social) amb autenticació
- ✅ Dashboard amb gràfics (Chart.js / PowerBI)
