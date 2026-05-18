# Architecture Overview

The Hospital Management System follows a three-tier architecture:

```
Desktop Client (Tkinter) ──HTTP──► Flask API ──SQL──► PostgreSQL
```

- **Presentation**: Tkinter desktop app on workstations
- **API**: Flask 3.1 REST API behind Gunicorn (4 workers)
- **Database**: PostgreSQL 16 with WAL streaming replication

See [TECHNICAL_SPECIFICATION.md](../../TECHNICAL_SPECIFICATION.md) for the canonical architectural reference.
