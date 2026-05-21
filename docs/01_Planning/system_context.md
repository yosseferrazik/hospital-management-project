# System Context

## C4 Level 1 diagram

![C4 Context Diagram](./images/C4_Context_Diagram.drawio.png)

## Users and roles

| Role | What they do | Database role |
|------|-------------|---------------|
| Administrator | Full access, user management, audit logs | `app_admin` |
| Doctor | CRUD patients, visits, prescriptions, surgeries | `app_doctor` |
| Nurse | Manage admissions, assist surgeries, view patients on their floor | `app_nurse` |
| Receptionist | Register patients, schedule appointments | `app_receptionist` |
| General staff | Read-only: patient name and room | `app_staff` |

## External systems

- **Social Security API** — receives monthly XML visit exports via HTTP POST (Basic Auth)
- **AWS EC2 (standby)** — hosts the standby PostgreSQL replica

## Deployment nodes

| Node | Location | LAN IP | Tailscale IP | Role |
|------|----------|--------|-------------|------|
| **Briar** | Hospital server room | 192.168.4.254 | 100.78.155.2 | API + PostgreSQL primary |
| **Sion** | AWS EC2 eu-west-3 (Paris) | — | 100.98.214.53 | PostgreSQL standby (read-only) |
| **Clients** | Hospital workstations | 192.168.4.0/24 | — | Tkinter desktop app |

Briar and Sion are connected through **Tailscale** (VPN mesh, automatic encryption). Users access Briar at **192.168.4.254** from the hospital LAN.
