# 6. BD — Esquema d'Alta Disponibilitat

## Proposta de hardware

### Briar (node primari — al hospital)

| Component    | Especificació                                   |
| ------------ | ----------------------------------------------- |
| CPU          | Intel Xeon E-2336 (6 nuclis, 12 fils) @ 4.8 GHz |
| RAM          | 16 GB DDR4 ECC (2 × 8 GB)                       |
| Disc 1       | 240 GB SSD NVMe — OS + sistema                  |
| Disc 2       | 480 GB SSD SATA — PostgreSQL data + WAL         |
| Xarxa        | 2 × 1 GbE (bonding mode 1 active-passive)       |
| LAN Hospital | 192.168.4.254                                   |
| Tailscale    | 100.78.155.2                                    |

#### Partions LVM

```
Disc 1 — /dev/sda (240 GB NVMe)
├── /dev/sda1   512 MB   /boot/efi    vfat
├── /dev/sda2   4 GB     [swap]       swap
└── /dev/sda3   235 GB   LVM VG: vg_system
    ├── vg_system/lv_root     80 GB   /
    ├── vg_system/lv_var      40 GB   /var
    ├── vg_system/lv_log      30 GB   /var/log
    └── vg_system/lv_tmp      10 GB   /tmp

Disc 2 — /dev/sdb (480 GB SATA SSD)
└── /dev/sdb1   480 GB   LVM VG: vg_postgres
    ├── vg_postgres/lv_pgdata    350 GB   /var/lib/postgresql/16/main
    └── vg_postgres/lv_pgwal      80 GB   /var/lib/postgresql/16/wal
    (25 GB reserva per a snapshots LVM)
```

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-08-15-image.png)

### Sion (node secundari — AWS EC2)

| Component | Especificació             |
| --------- | ------------------------- |
| CPU       | 2 vCPU (AWS t3.medium)    |
| RAM       | 4 GB                      |
| Disc      | 100 GB gp3 (EBS) — PGDATA |
| OS        | Ubuntu Server 24.04 LTS   |
| Tailscale | 100.98.214.53             |

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-00-20-image.png)

> No he pugut particionar exactament degut a desconeixement parcial de la tecnologia EC2 de AWS.

## Topologia de replicació

- **Mètode:** Streaming replication nativa de PostgreSQL via WAL
- **Rol:** Actiu-passiu (Briar = primary r/w, Sion = standby read-only)
- **Xarxa:** Tailscale overlay network + LAN interna de l'hospital
- **Usuari de replicació:** `replicator`

```
┌──────────────────────────────────────────────────┐
│           Hospital LAN (192.168.4.0/24)           │
│                                                    │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐   │
│  │  Users   │   │  Users   │   │    Admin      │   │
│  │ (doctors)│   │ (recept) │   │ (IT staff)    │   │
│  └────┬─────┘   └────┬─────┘   └──────┬───────┘   │
│       │              │               │            │
└───────┼──────────────┼───────────────┼────────────┘
        │              │               │
        │     192.168.4.254            │
        │              │         (Tailscale VPN)
   ┌────┴──────────────┴───────────────┴────┐
   │               Briar                     │
   │   API + PostgreSQL PRIMARY              │
   └────────────┬────────────────────────────┘
                │ Tailscale (100.78.155.2 ↔ 100.98.214.53)
                │ (WAL streaming + rsync backups)
   ┌────────────┴────────────────────────────┐
   │               Sion (AWS)                 │
   │   PostgreSQL STANDBY (read-only)         │
   └──────────────────────────────────────────┘
```

### Configuració del primari (Briar)

`postgresql.conf`:

```
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1024
```

`pg_hba.conf`:

```
host replication replicator 100.98.214.53/32 md5
```

### Inicialització del standby (Sion)

```bash
sudo -u postgres pg_basebackup -h 100.78.155.2 -D /var/lib/postgresql/16/main \
  -U replicator -P -v -R --wal-method=stream
sudo systemctl start postgresql
```

La flag `-R` crea automàticament `standby.signal` i escriu `primary_conninfo`.

## Monitorització de la replicació

```bash
# Al primari — comprovar estat
psql -c "SELECT state, sync_state, application_name FROM pg_stat_replication;"

# Al secundari — comprovar lag
psql -c "SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn(), pg_last_xact_replay_timestamp();"
```

Script automatitzat: `scripts/ops/check_replication.sh`

Captures de la verificació de replicació:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/ha/2026-05-22-18-18-54-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/ha/2026-05-22-18-20-39-image.png)

## Còpies de seguretat (Backup)

### Sistema de 3 capes

| Capa                           | Patró de fitxer     | Com es crea                      |
| ------------------------------ | ------------------- | -------------------------------- |
| **Física** (PGDATA)            | `physical_*.tar.gz` | `--physical` o `--physical-only` |
| **Lògica** (pg_dump)           | `hsp_db_*.dump`     | per defecte o `--db-only`        |
| **Configuració** (app + .conf) | `config_*.tar.gz`   | per defecte o `--config-only`    |

### Script principal

`scripts/backup_database.py` — backup automatitzat amb metadades i rotació:

- Rotació local: 5 còpies diàries
- Pujada al núvol (Sion) cada dia

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-17-31-12-image.png)

### Programació (cron)

```bash
# Backup complet cada dia a les 02:00
0 2 * * * /opt/hms/current/scripts/backup_wrapper.sh
```

## Restauració

### Script de restauració completa

`scripts/ops/restore_service.sh` — recuperació bare-metal completa:

1. Desplegar aplicació des de git
2. Restaurar PGDATA (física)
3. Restaurar configuració (app + postgresql.conf)
4. Restaurar dump lògic de BD
5. Reiniciar servei + smoke test

**Ús:**

```bash
sudo bash restore_service.sh
sudo bash restore_service.sh --backup-dir /backups/local --timestamp 20260522_120000
sudo bash restore_service.sh --physical-only
sudo bash restore_service.sh --dry-run
```

### Backup lògic simplificat

```bash
sudo -u postgres /opt/hms/scripts/ops/backup.sh
```

## Verificació

| Test              | Comanda                                            |
| ----------------- | -------------------------------------------------- |
| API funciona      | `curl http://192.168.4.254:5000/health`            |
| Replicació activa | `psql -c "SELECT state FROM pg_stat_replication;"` |
| Backup recents    | `ls -la /backups/local/`                           |

Captures de verificació:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/ha/2026-05-22-17-31-54-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/ha/2026-05-22-18-17-55-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/ha/2026-05-22-18-18-11-image.png)
