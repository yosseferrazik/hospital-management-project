# 12. Document Final — Hospital Management System

## Resum del projecte

Sistema de gestió hospitalària per a **Hospital de Blanes** amb tres capes:

```
Client Tkinter ──HTTP──► API Flask ──SQL──► PostgreSQL 16
```

L'aplicació cobreix: gestió de pacients, coordinació de personal mèdic, programació de visites i cirurgies, farmàcia, radiologia i exportació de dades a la Seguretat Social.

## Tecnologies utilitzades

| Capa          | Tecnologia                        | Versió        |
| ------------- | --------------------------------- | ------------- |
| Backend       | Python + Flask                    | 3.12 / 3.1.3  |
| API Server    | Gunicorn (4 workers) + systemd    | 23.0.0        |
| ORM           | SQLAlchemy                        | 2.0.49        |
| Base de dades | PostgreSQL                        | 16.13         |
| Autenticació  | JWT (Flask-JWT-Extended) + bcrypt | 4.7.1 / 5.0.0 |
| Client        | Tkinter                           | —             |
| Dashboard     | Chart.js                          | —             |
| Dades falses  | Faker (es_ES, ru_RU)              | 40.15.0       |

## Nodes

| Node      | IP Tailscale  | Rol                      |
| --------- | ------------- | ------------------------ |
| **Briar** | 100.78.155.2  | API + PostgreSQL primari |
| **Sion**  | 100.98.214.53 | PostgreSQL standby       |

Xarxa: Tailscale + LAN hospitalària.

## Estructura del repositori

```
hospital-management-project/
├── server/src/           # API Flask (24 blueprints)
│   ├── run.py            # Dev server
│   ├── wsgi.py           # Producció (Gunicorn)
│   ├── app/              # App factory, models, routes, services
│   └── requirements.txt  # Dependències (24 paquets)
├── desktop/src/          # Client Tkinter
│   ├── main.py           # Punt d'entrada
│   └── views/            # 13+ vistes d'usuari
├── scripts/
│   ├── deploy/           # Desplegament versionat
│   ├── ops/              # Backup, restore, monitorització
│   ├── sql/              # Schema, seguretat, seed
│   └── systemd/          # Servei systemd
├── docs/                 # Documentació del projecte
└── deliveries/           # Blocs d'entrega
```

## Base de dades

- **24 taules** amb integritat referencial
- Indexos, constraints UNIQUE, CHECK i FKs
- Suport UTF-8 (ciríl·lic)
- Row-Level Security (RLS) a PATIENTS i ADMISSIONS
- 8 triggers d'auditoria automàtics
- 5 rols RBAC (app_admin, app_doctor, app_nurse, app_receptionist, app_staff)

## Funcionalitats implementades

### Bloc de connectivitat i login

- Connexió a BD des de Python
- Registre i inici de sessió amb JWT
- Credencials protegides (bcrypt, fitxer extern, secrets en memòria)

### Bloc de manteniment

- CRUD de personal (metges, infermeres, general)
- CRUD de pacients
- Assignació infermera-metge/planta
- Consulta de cirurgies i visites per data
- Dispositius per quiròfan
- 5 funcions/triggers PL/pgSQL

### Bloc de consultes

- Resum de planta (habitacions, quiròfans, infermeres)
- Directori de personal
- Visites per dia
- Ranking de metges
- Malalties més comunes
- Dashboard amb gràfics

### Bloc d'exportació

- Exportació XML/JSON de visites (indentat)
- XSD + JSON Schema
- Enviament a API Seguretat Social (Basic Auth)
- Dashboard Chart.js + connexió PowerBI opcional

### Alta disponibilitat

- Streaming replication (actiu-passiu)
- Backup de 3 capes (física, lògica, configuració)
- Restauració bare-metal automatitzada
- Rotació de 5 dies + còpia al núvol
- Monitorització de lag de replicació
- Renovació automàtica de certificats SSL

### Dummy data

- 50.000 pacients, 100.000 visites
- Dades en ciríl·lic (5%)
- Generació per lots optimitzada
- Neteja amb DummyRegistry

### Seguretat

- RBAC amb 5 rols
- SSL a PostgreSQL
- RLS a taules sensibles
- Data masking per columnes
- Auditoria de 8 taules
- Document AGPD

## Problemes trobats i solucions

| Problema                  | On          | Solució                                   |
| ------------------------- | ----------- | ----------------------------------------- |
| pgpool-II inestable       | Replicació  | Canvi a streaming replication nativa      |
| Generació lenta           | Dummy data  | Insercions per lots amb flush/commit      |
| Permisos d'auditoria      | Triggers    | SECURITY DEFINER a funcions helper        |
| RLS massa restrictiu      | Infermeres  | Ajustar política a admissions actives     |
| pg_basebackup timeout     | Replicació  | Afegir sslmode=require a primary_conninfo |
| Lag de replicació alt     | Briar       | Augmentar wal_keep_size a 1024 MB         |
| psycopg2 no compilava     | Briar       | Instal·lar libpq-dev                      |
| Tkinter no trobat         | PC hospital | Instal·lar python3-tk                     |
| DNI reiniciats al restore | Briar       | pg_dump -Fc en lloc de text pla           |
| Firewall bloquejava API   | LAN         | Obrir port 5000 amb equip de xarxa        |

## Enllaços

- **Repositori GitHub:** https://github.com/yosseferrazik/hospital-management-project
- **Documentació:** `docs/` i `deliveries/`

## Autors

**Yossef Errazik** — Desenvolupament complet
