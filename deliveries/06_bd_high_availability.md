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

**Justificació del hardware:**

| Component     | Justificació                                                                                       |
| ------------- | -------------------------------------------------------------------------------------------------- |
| **Xeon E-2336** | 6 nuclis a alta freqüència permeten executar PostgreSQL + API simultàniament sense contenció     |
| **16 GB ECC** | Memòria amb correcció d'errors crítica per a integritat de dades hospitalàries; suficient per a `shared_buffers = 4 GB` i `effective_cache_size = 8 GB` |
| **NVMe OS**   | Arrencada ràpida i aïllament del sistema respecte a les dades                                     |
| **SSD SATA**  | Emmagatzematge dedicat per a PGDATA i WAL amb separació física per evitar contenció d'I/O          |
| **Bonding**   | Redundància de xarxa: si un NIC falla, el segon pren el control sense interrupció                  |

### Partions LVM

LVM (Logical Volume Manager) proporciona una capa d'abstracció sobre el disc físic que permet redimensionar particions en calent, fer snapshots per a backups consistents i gestionar l'espai de manera flexible sense dependre de la geometria del disc.

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

**Avantatges de l'esquema LVM emprat:**

| Avantatge                   | Descripció                                                                             |
| --------------------------- | -------------------------------------------------------------------------------------- |
| **Snapshots**               | Es poden crear snapshots LVM del volum `lv_pgdata` en segons per a backups consistents sense aturar PostgreSQL |
| **Redimensionament**        | Si `lv_pgwal` creix per excés de WAL, es pot estendre des de l'espai lliure sense reinici |
| **Aïllament WAL/Data**      | Separar el WAL de PGDATA en volums diferents evita que un ompliment del WAL afecte les dades o viceversa |
| **Espai lliure**            | 25 GB de reserva permeten snapshots o expansions sense risc                           |

**Comandes de creació LVM:**

```bash
# Crear el grup de volums
pvcreate /dev/sdb1
vgcreate vg_postgres /dev/sdb1

# Crear volums lògics
lvcreate -L 350G -n lv_pgdata vg_postgres
lvcreate -L 80G -n lv_pgwal vg_postgres

# Formatar i muntar
mkfs.ext4 /dev/vg_postgres/lv_pgdata
mkfs.ext4 /dev/vg_postgres/lv_pgwal
mount /dev/vg_postgres/lv_pgdata /var/lib/postgresql/16/main
mount /dev/vg_postgres/lv_pgwal /var/lib/postgresql/16/wal
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

> No he pogut particionar exactament degut a desconeixement parcial de la tecnologia EC2 de AWS.

**Seguretat del node Sion (Security Group AWS):**

| Regla         | Protocol | Port     | Origen            | Descripció                          |
| ------------- | -------- | -------- | ----------------- | ----------------------------------- |
| SSH           | TCP      | 22       | 100.78.155.2/32   | Accés SSH només des de Briar        |
| PostgreSQL    | TCP      | 5432     | 100.78.155.2/32   | Replicació i consultes des de Briar |
| Tailscale     | UDP      | 41641    | 0.0.0.0/0         | Tràfic de la xarxa overlay          |
| HTTP (API)    | TCP      | 5000     | 100.78.155.2/32   | Accés API read-only                 |

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-21-00-00-20-image.png)

---

## Topologia de replicació

- **Mètode:** *Streaming replication* nativa de PostgreSQL via WAL (enviament asíncron)
- **Rol:** Actiu-passiu (Briar = primary r/w, Sion = standby read-only)
- **Xarxa:** Tailscale overlay network + LAN interna de l'hospital
- **Usuari de replicació:** `replicator`
- **Port:** 5432

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

**`postgresql.conf`:**

```ini
# Configuració de replicació WAL
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1024
max_replication_slots = 2
hot_standby = on

# Rendiment
shared_buffers = 4GB
effective_cache_size = 8GB
work_mem = 64MB
maintenance_work_mem = 512MB
wal_buffers = 16MB
```

**`pg_hba.conf`:**

```ini
# Accés de replicació per a Sion via Tailscale
host replication replicator 100.98.214.53/32 md5
```

### Inicialització del standby (Sion)

```bash
# 1. Crear l'usuari de replicació al primari
sudo -u postgres psql -c "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD '...';"

# 2. Fer el base backup des de Briar cap a Sion
sudo -u postgres pg_basebackup -h 100.78.155.2 -D /var/lib/postgresql/16/main \
  -U replicator -P -v -R --wal-method=stream

# 3. Iniciar PostgreSQL al standby
sudo systemctl start postgresql
```

La flag `-R` crea automàticament `standby.signal` i escriu `primary_conninfo` a `postgresql.auto.conf`:

```ini
# postgresql.auto.conf (generat automàticament)
primary_conninfo = 'host=100.78.155.2 port=5432 user=replicator password=...'
```

---

## Monitorització de la replicació

### Comandes de verificació

```bash
# Al primari — comprovar estat dels standby connectats
psql -c "SELECT pid, state, sync_state, application_name,
         pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
         FROM pg_stat_replication;"

# Al secundari — comprovar lag de recepció i reproducció
psql -c "SELECT pg_last_wal_receive_lsn(),
         pg_last_wal_replay_lsn(),
         pg_last_xact_replay_timestamp(),
         now() - pg_last_xact_replay_timestamp() AS replay_lag;"
```

### Script automatitzat: `scripts/ops/check_replication.sh`

```bash
#!/bin/bash
# Comprova l'estat de la replicació i envia una alerta si el lag supera el llindar
THRESHOLD_MB=500

LAG=$(psql -t -A -c "
  SELECT COALESCE(pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) / 1024 / 1024, 0)
  FROM pg_stat_replication LIMIT 1;" 2>/dev/null || echo "0")

echo "[$(date)] Replication lag: ${LAG} MB"

if [ "$LAG" -gt "$THRESHOLD_MB" ]; then
    echo "ALERTA: Lag de replicació superior a ${THRESHOLD_MB} MB"
    # Enviar alerta (email, Slack, etc.)
fi
```

Captures de la verificació de replicació:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/ha/2026-05-22-18-18-54-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/ha/2026-05-22-18-20-39-image.png)

---

## Procediment de failover

En cas de caiguda del node primari (Briar), el node secundari (Sion) pot promocionar-se a primari:

```bash
# Al node Sion (standby)
sudo -u postgres pg_ctl promote -D /var/lib/postgresql/16/main
# o
sudo -u postgres psql -c "SELECT pg_promote();"
```

Un cop promocionat, Sion accepta escriptures. Per reincorporar Briar quan es recuperi:

```bash
# 1. Al nou primari (Sion), crear un slot de replicació per a Briar
psql -c "SELECT pg_create_physical_replication_slot('briar_slot');"

# 2. A Briar (recuperat), configurar com a standby
#    Esborrar PGDATA vell i fer pg_basebackup des de Sion
sudo rm -rf /var/lib/postgresql/16/main/*
sudo -u postgres pg_basebackup -h 100.98.214.53 -D /var/lib/postgresql/16/main \
  -U replicator -P -v -R --wal-method=stream

# 3. Reiniciar PostgreSQL a Briar
sudo systemctl start postgresql
```

---

## Còpies de seguretat (Backup)

### Sistema de 3 capes

| Capa                           | Patró de fitxer     | Com es crea                      |
| ------------------------------ | ------------------- | -------------------------------- |
| **Física** (PGDATA)            | `physical_*.tar.gz` | `--physical` o `--physical-only` |
| **Lògica** (pg_dump)           | `hsp_db_*.dump`     | per defecte o `--db-only`        |
| **Configuració** (app + .conf) | `config_*.tar.gz`   | per defecte o `--config-only`    |

### Script principal: `scripts/backup_database.py`

Backup automatitzat amb metadades i rotació. Utilitza `argparse` per seleccionar la capa i `subprocess` per cridar les eines de PostgreSQL:

```python
#!/usr/bin/env python3
"""
Script de backup del sistema hospitalari.
Capes: física (pg_basebackup), lògica (pg_dump), configuració (tar).
"""

import argparse, subprocess, datetime, json, os, glob, shutil

BACKUP_DIR = "/backups/local"
RETENTION_DAYS = 5
PGDATA = "/var/lib/postgresql/16/main"

def backup_physical(tag=""):
    """Crea un backup físic consistent amb pg_basebackup."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"physical_{tag}{ts}.tar.gz"
    path = os.path.join(BACKUP_DIR, filename)
    subprocess.run([
        "pg_basebackup", "-D", "-",
        "-Ft", "-z", "-P", "-X", "fetch",
        f"--waldir={PGDATA}/pg_wal"
    ], stdout=open(path, "wb"), check=True)
    return path

def backup_logical(tag=""):
    """Crea un dump lògic del schema complet."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hsp_db_{tag}{ts}.dump"
    path = os.path.join(BACKUP_DIR, filename)
    subprocess.run([
        "pg_dump", "--format=custom", "--compress=9",
        "--dbname=hospital_db", f"--file={path}"
    ], check=True)
    return path

def rotate():
    """Elimina backups més antics de RETENTION_DAYS dies."""
    cutoff = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
    for pattern in ["physical_*.tar.gz", "hsp_db_*.dump", "config_*.tar.gz"]:
        for f in glob.glob(os.path.join(BACKUP_DIR, pattern)):
            if datetime.datetime.fromtimestamp(os.path.getmtime(f)) < cutoff:
                os.remove(f)
                print(f"  Eliminat: {os.path.basename(f)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--physical", action="store_true")
    parser.add_argument("--logical", action="store_true")
    parser.add_argument("--config", action="store_true")
    args = parser.parse_args()

    os.makedirs(BACKUP_DIR, exist_ok=True)

    if args.physical or not (args.logical or args.config):
        print(f"Backup físic → {backup_physical()}")
    if args.logical or not (args.physical or args.config):
        print(f"Backup lògic → {backup_logical()}")
    # ... (config backup omitted for brevity)

    rotate()
```

- **Rotació local:** 5 còpies diàries
- **Pujada al núvol (Sion)** cada dia via rsync sobre Tailscale:

```bash
rsync -avz /backups/local/ 100.98.214.53:/backups/remote/
```

  ![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/installation_manual/2026-05-22-17-31-12-image.png)

### Programació (cron)

```bash
# Backup complet cada dia a les 02:00
0 2 * * * /opt/hms/current/scripts/backup_wrapper.sh

# Backup lògic addicional cada 6 hores (horari laboral)
0 6,12,18 * * * /opt/hms/current/scripts/backup_wrapper.sh --logical-only
```

---

## Restauració

### Script de restauració completa: `scripts/ops/restore_service.sh`

Recuperació bare-metal completa en 5 passos:

1. **Desplegar aplicació** des de git (branch `v1.0.0` o la commit indicada)
2. **Restaurar PGDATA** (backup físic + WAL)
3. **Restaurar configuració** (app + `postgresql.conf`, `pg_hba.conf`)
4. **Restaurar dump lògic** de BD (per assegurar consistència)
5. **Reiniciar servei** + smoke test

**Ús:**

```bash
sudo bash restore_service.sh
sudo bash restore_service.sh --backup-dir /backups/local --timestamp 20260522_120000
sudo bash restore_service.sh --physical-only
sudo bash restore_service.sh --dry-run
```

**Exemple de smoke test:**

```bash
#!/bin/bash
# Smoke test post-restauració
echo "=== Smoke Test ==="
curl -sf http://localhost:5000/health && echo " API OK" || echo " API FAIL"
psql -c "SELECT count(*) FROM PATIENTS;" && echo " DB OK" || echo " DB FAIL"
```

### Backup lògic simplificat

```bash
sudo -u postgres /opt/hms/scripts/ops/backup.sh
```

---

## Verificació

| Test              | Comanda                                            |
| ----------------- | -------------------------------------------------- |
| API funciona      | `curl http://192.168.4.254:5000/health`            |
| Replicació activa | `psql -c "SELECT state FROM pg_stat_replication;"` |
| Backup recents    | `ls -la /backups/local/`                           |
| Lag de replicació | `psql -c "SELECT now() - pg_last_xact_replay_timestamp() AS lag;"` |

Captures de verificació:

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/ha/2026-05-22-17-31-54-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/ha/2026-05-22-18-17-55-image.png)

![](https://raw.githubusercontent.com/yosseferrazik/hospital-management-project/main/deliveries/images/ha/2026-05-22-18-18-11-image.png)
