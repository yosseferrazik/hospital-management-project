# 5. PRG — Bloc de Manteniment

## Operacions de manteniment (CRUD)

Des de la pestanya **Maintenance** de l'aplicació d'escriptori (5 subpestanyes: Doctor, Nursing, General Staff, Patient, Assignments) es poden realitzar totes les operacions de manteniment del sistema. Cada operació es tradueix en una crida a l'API corresponent:

| Tasca                              | Endpoint API                                   | Descripció                                            |
| ---------------------------------- | ---------------------------------------------- | ----------------------------------------------------- |
| Alta personal mèdic                | `POST /api/maintenance/staff/medical`          | Afegir un metge/ssa                                   |
| Alta personal d'infermeria         | `POST /api/maintenance/staff/nursing`          | Afegir un/a infermer/a                                |
| Alta personal general              | `POST /api/maintenance/staff/general`          | Afegir administratiu, neteja, etc.                    |
| Alta nous pacients                 | `POST /api/maintenance/patients`               | Afegir un nou pacient                                 |
| Assignar infermer a metge/planta   | `PUT /api/maintenance/nursing/assign`          | Cos: `{nurse_id, doctor_id}` o `{nurse_id, floor_id}` |
| Consultar cirurgies per data       | `GET /api/maintenance/surgeries?date=X`        | Llistar cirurgies amb pacient, cirurgià, assistents   |
| Consultar visites per data         | `GET /api/maintenance/visits/scheduled?date=X` | Llistar visites programades                           |
| Consultar dispositius per quiròfan | `GET /api/medical-devices?theater_id=X`        | Dispositius disponibles en un quiròfan                |

## PL/pgSQL: Funcions i triggers

Es van crear 5 funcions/procediments a PostgreSQL per garantir la integritat de les dades i automatitzar processos crítics:

### 1. `check_surgery_overlap()`

**Trigger** (BEFORE INSERT/UPDATE a SURGERIES) que evita reservar el mateix quiròfan al mateix dia/hora. Si ja existeix una cirurgia al mateix quiròfan amb solapament d'horari, llança un error. Això evita dobles reserves i conflictes de programació quirúrgica.

### 2. `validate_nurse_assignment()`

**Trigger** (BEFORE INSERT/UPDATE a NURSING_STAFF) que comprova que el metge o la planta assignada existeixin realment a la base de dades, evitant assignacions invàlides.

### 3. `audit_trigger_function()`

Registrador d'auditoria genèric per a 8 taules sensibles. S'activa amb AFTER INSERT/UPDATE/DELETE i guarda: usuari, timestamp, acció, taula, valors anteriors/nous (JSON). Aquesta funció és reutilitzada pels 8 triggers d'auditoria del sistema.

### 4. `get_current_app_user_id()`

Funció helper que retorna l'ID de l'usuari actual des del context de sessió (`SET_CONFIG`). Utilizada per les polítiques RLS i els triggers d'auditoria.

### 5. `get_current_staff_id()`

Funció helper que retorna l'ID del treballador actual des del context de sessió. Permet que els triggers sàpiguen qui està realitzant cada operació.

## Funcionalitats obligatòries implementades

- ✅ Alta de personal (metge/ssa, infermer/a, administratiu/va, neteja...)
- ✅ Alta de nous pacients
- ✅ Per personal d'infermeria: saber si depèn d'un metge/ssa o és de planta
- ✅ Per un dia determinat: operacions previstes per quiròfan (pacient, hora, metge, infermeria)
- ✅ Per un dia determinat: visites planificades (hora, metge, pacient)
- ✅ 2 procediments/funcions/triggers PL/pgSQL mínim (se'n van crear 5)

## Funcionalitats opcionals implementades

- ✅ Donada una habitació: reserves previstes (data ingrés, sortida, pacient)
- ✅ Donat un pacient: historial de visites, diagnòstics, medicaments, ingressos, quiròfan
- ✅ Donat un metge/ssa: visites i operacions programades + hores disponibles

## Funcionalitats top implementades

- ✅ Per cada quiròfan: quants aparells mèdics té i quantitat de cadascun

## Imatges

A continuació es mostren les pantalles de l'aplicació per a les operacions de manteniment:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/maintenance/2026-05-22-17-24-32-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/maintenance/2026-05-22-17-24-48-image.png)
