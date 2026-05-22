# 7. PRG — Bloc de Consultes

## Informes disponibles

Tots accessibles des de l'aplicació d'escriptori (pestanyes **Operational Reports**, **Statistics**, **Advanced Reports**) o via API. El sistema ofereix informes obligatoris, opcionals i top que cobreixen totes les necessitats de gestió hospitalària.

### Obligatoris

| Informe            | Endpoint API                                      | Descripció                                     |
| ------------------ | ------------------------------------------------- | ---------------------------------------------- |
| Dades d'una planta | `GET /api/reports/summary?floor_id=X`             | Habitacions, quiròfans i personal d'infermeria |
| Tot el personal    | `GET /api/reports/summary?report=staff`           | Llistat complet de treballadors                |
| Visites per dia    | `GET /api/reports/visits?start_date=X&end_date=Y` | Nombre de visites ateses per dia               |

Captures dels informes obligatoris:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-22-02-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-22-16-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-22-28-image.png)

### Opcionals

| Informe           | Endpoint API                       | Descripció                     |
| ----------------- | ---------------------------------- | ------------------------------ |
| Ranking de metges | `GET /api/reports/doctor-workload` | Metges que atenen més pacients |

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-22-44-image.png)

### Top

| Informe               | Endpoint API                               | Descripció                |
| --------------------- | ------------------------------------------ | ------------------------- |
| Malalties més comunes | `GET /api/reports/summary?report=diseases` | Diagnòstics més freqüents |

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-22-59-image.png)

## Reports complets via API

| Report      | Endpoint                       | Filtres                                          |
| ----------- | ------------------------------ | ------------------------------------------------ |
| Summary     | `GET /api/reports/summary`     | start_date, end_date                             |
| Visites     | `GET /api/reports/visits`      | start_date, end_date, specialty, doctor_id       |
| Cirurgies   | `GET /api/reports/surgeries`   | start_date, end_date, procedure_type, surgeon_id |
| Admissions  | `GET /api/reports/admissions`  | start_date, end_date, floor_id                   |
| Medicacions | `GET /api/reports/medications` | start_date, end_date                             |

Captures de pantalla dels reports disponibles:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-23-55-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-24-09-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-24-27-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-24-41-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-24-53-image.png)

## Exportació PDF

L'informe de sumari es pot descarregar com a PDF professional (generat amb fpdf2) via `GET /api/reports/summary/pdf`. Requereix JWT amb rol ADMIN, DOCTOR o NURSE.

> Requereix token

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-25-18-image.png)

Si el tens genera aixo:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-26-22-image.png)

## Visualitzacions a l'escriptori

1. **Operational Reports** — Visites i cirurgies programades per a una data

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/queries/2026-05-22-18-26-51-image.png)

1. **Statistics** — Resum de planta, directori de personal, tendències de visites, ranking de metges, freqüència de malalties
2. **Advanced Reports** — Visor multi-pestanya amb 8 categories de reports, filtres i descàrrega PDF

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

## Funcionalitats obligatòries implementades

- ✅ Donada una planta: habitacions, quiròfans i personal d'infermeria
- ✅ Informe de tot el personal de l'hospital
- ✅ Informe de nombre de visites ateses per dia

## Funcionalitats opcionals implementades

- ✅ Ranking de metges que atenen més pacients

## Funcionalitats top implementades

- ✅ Malalties més comunes
