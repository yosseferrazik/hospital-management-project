# Project Overview — Hospital Management System

## Architecture

Three-tier system for **Hospital de Blanes**: patient management, medical staff coordination, visit and surgery scheduling, pharmacy, and data export to the Spanish Social Security.

```
Tkinter Desktop Client ──HTTP──► Flask API ──SQL──► PostgreSQL 16
```

We chose Flask and PostgreSQL because that's what we covered in class and it keeps licensing costs at zero.

## Technology stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | Flask 3.1, Python 3.12 | Lightweight, well known |
| API server | Gunicorn (4 workers) + systemd | Production setup |
| Database | PostgreSQL 16 with streaming replication | Required by project, supports UTF-8 and Cyrillic |
| ORM | SQLAlchemy 2.0 | Prevents SQL injection |
| Auth | JWT (Flask-JWT-Extended) + bcrypt | Stateless, reasonably secure |
| Desktop | Tkinter + requests | Low resource usage, built into Python |
| Dashboard | Chart.js (web) | Free alternative to PowerBI |
| Fake data | Faker (es_ES and ru_RU locales) | 50k patients, 100k visits |

## What we built

- 22 database tables with full referential integrity
- REST API with 23 endpoint groups (CRUD, reports, export, admin)
- Tkinter desktop client with 11 views
- RBAC with 5 roles and row-level security
- Audit logging via PostgreSQL triggers (8 tables)
- SSL-secured connections
- Active-passive streaming replication (primary + cloud standby)
- Automated daily backups with 5-day retention
- XML/JSON export with XSD and JSON Schema validation
- Social Security API integration
- Chart.js web dashboard

## Problems we ran into

- **Replication**: tried pgpool-II first, switched to built-in streaming replication because it was more stable
- **Batch inserts**: generating 100k visits crashed until we added periodic commits
- **Audit triggers**: needed SECURITY DEFINER on helper functions or permissions would fail
- **RLS policies**: nurses couldn't see their own patients until we fixed the floor assignment logic

## References

- PostgreSQL: https://www.postgresql.org/docs/
- Flask: https://flask.palletsprojects.com/
- Faker: https://faker.readthedocs.io/
- Chart.js: https://www.chartjs.org/
- OWASP: https://owasp.org/www-project-top-ten/
