# Configuration

## Environment variables (server) — on Briar

| Variable                | Required | Default  | Notes                                              |
| ----------------------- | -------- | -------- | -------------------------------------------------- |
| `DATABASE_URL`          | Yes      | —        | `postgresql://postgres:pass@localhost:5432/hsp_db` |
| `JWT_SECRET_KEY`        | Yes      | —        | Generate with `openssl rand -hex 32`               |
| `DB_NAME`               | Yes      | `hsp_db` | Must match the created database                    |
| `EXTERNAL_API_URL`      | No       | —        | Social Security API endpoint URL                   |
| `EXTERNAL_API_USERNAME` | No       | —        | HTTP Basic Auth user for the external API          |
| `EXTERNAL_API_PASSWORD` | No       | —        | HTTP Basic Auth password                           |

## Environment variables (desktop client) — on LAN PCs

| Variable       | Required | Default                         | Notes                          |
| -------------- | -------- | ------------------------------- | ------------------------------ |
| `API_BASE_URL` | Yes      | `http://192.168.4.254:5000/api` | Briar's IP on the hospital LAN |

## Ports

| Service         | Port      | Node           | Notes                               |
| --------------- | --------- | -------------- | ----------------------------------- |
| Flask API (dev) | 5000      | Briar          | `python run.py`                     |
| Gunicorn (prod) | 8000      | Briar          | Behind systemd                      |
| PostgreSQL      | 5432      | Briar and Sion | SSL required for remote connections |
| Tailscale       | UDP 41641 | Briar and Sion | VPN mesh                            |

## Production (Briar)

- **Gunicorn** (4 workers) behind **systemd** — service file at `scripts/systemd/hms-api.service`
- **logrotate** — config at `scripts/logrotate/hms`
- **Versioned deploy** at `scripts/deploy/deploy.sh` (uses symlinks, automatic rollback if smoke test fails)

The production setup assumes Ubuntu 24.04 with PostgreSQL 16 and Python 3.12.
