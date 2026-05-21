# Hospital Sa Palomera — Hospital Management System

> Intermodular project for the ASIX program at **Institut Sa Palomera**.

---

## Documentation

**Canonical reference:** [TECHNICAL_SPECIFICATION.md](./TECHNICAL_SPECIFICATION.md)

### Practical Guides (quick start)

| Guide | Description |
|:------|:------------|
| [Installation Guide](./docs/04_deployment/installation_guide.md) | Step-by-step setup from scratch |
| [Configuration Guide](./docs/04_deployment/configuration.md) | Environment variables, database, ports, logging |
| [User Manual](./docs/05_user_guides/user_manual.md) | Desktop client features for end users |
| [Administrator Manual](./docs/05_user_guides/administrator_manual.md) | User management, audit logs, maintenance |

### Reference Documentation (detailed)

Database design, security, high availability, application specs, and planning documents are in [docs/](./docs/README.md).

---

## Quick Links

| Area               | Location |
|:-------------------|:---------|
| API code           | `server/src/` |
| Desktop client     | `desktop/src/` |
| Deploy automation  | `scripts/deploy/deploy.sh` |
| SQL schema         | `scripts/sql/schema.sql` |
| Systemd unit       | `scripts/systemd/hms-api.service` |
| Ansible playbook   | `deploy/ansible/deploy_hms.yml` |

---

## Authors

- **Yossef Errazik** — [GitHub](https://github.com/yosseferrazik)
