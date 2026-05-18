# Technology Stack

| Layer             | Technology                  | Role                              |
|-------------------|-----------------------------|-----------------------------------|
| Language          | Python 3.12                 | Full-stack language               |
| API Framework     | Flask 3.1.3                 | REST API framework                |
| WSGI Server       | Gunicorn 23.0.0             | Production server (via systemd)   |
| ORM               | SQLAlchemy 2.0.49           | Object-relational mapping         |
| Authentication    | Flask-JWT-Extended 4.7.1    | JWT token issuance/validation     |
| Password Hashing  | bcrypt 5.0.0                | Password storage                  |
| Database Driver   | psycopg2-binary 2.9.12      | PostgreSQL connectivity           |
| CORS              | Flask-CORS 6.0.2            | Cross-origin support              |
| Desktop Client    | tkinter + requests 2.33.1   | GUI + HTTP client                 |
| Test Data         | Faker                       | Synthetic data generation         |
| Config Loading    | python-dotenv 1.2.2         | `.env` file loader                |

## Database

| Property | Value                    |
|----------|--------------------------|
| Engine   | PostgreSQL 16            |
| Database | `hsp_db`                 |
| Port     | 5432                     |
| Replication | WAL streaming (primary/standby) |

## Deployment

| Component  | Server       | OS                   |
|------------|-------------|----------------------|
| API + DB   | Briar (on-prem) | Ubuntu Server 24.04 |
| Standby DB | Sion (AWS EC2) | Ubuntu Server 24.04 |

See [Configuration Guide](../04_Operations/Configuration_Guide.md) for environment variables and ports.
