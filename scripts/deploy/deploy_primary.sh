#!/bin/bash
# Deploy script for primary node (Hospital Sa Palomera)
# Installs packages, creates directories, deploys scripts, and enables systemd services.

set -euo pipefail

echo "Deploying HMS primary node..."

sudo apt update
sudo apt install -y postgresql-14 postgresql-client-14 python3 python3-pip awscli git
sudo pip3 install boto3

# Create directories
sudo mkdir -p /opt/hms/scripts /backups/local /backups/archive /var/log/hms
sudo chown -R postgres:postgres /backups/local /backups/archive
sudo chmod 700 /backups/local /backups/archive

# Copy repository (assumes repo already cloned under current directory)
REPO_ROOT=$(pwd)
echo "Using repo root: $REPO_ROOT"

sudo cp -r "$REPO_ROOT/scripts/ops" /opt/hms/ || true
sudo cp -r "$REPO_ROOT/scripts/deploy" /opt/hms/ || true

# Install scripts
sudo cp "$REPO_ROOT/scripts/ops/backup.sh" /opt/hms/scripts/backup.sh
sudo chown postgres:postgres /opt/hms/scripts/backup.sh
sudo chmod 750 /opt/hms/scripts/backup.sh

sudo cp "$REPO_ROOT/scripts/ops/check_replication.sh" /opt/hms/scripts/check_replication.sh
sudo chmod 750 /opt/hms/scripts/check_replication.sh

# Install hms-api systemd unit (if present)
if [ -f "$REPO_ROOT/scripts/systemd/hms-api.service" ]; then
  sudo cp "$REPO_ROOT/scripts/systemd/hms-api.service" /etc/systemd/system/hms-api.service
  sudo systemctl daemon-reload
  sudo systemctl enable --now hms-api.service || true
  echo "Installed and started hms-api.service (if app present)"
fi

echo "Primary deployment files installed under /opt/hms/scripts/"

echo "Creating systemd service for backup (runs via timer)"
sudo tee /etc/systemd/system/hms-backup.service > /dev/null <<'EOF'
[Unit]
Description=HMS Backup Service

[Service]
Type=oneshot
User=postgres
ExecStart=/opt/hms/scripts/backup.sh
EOF

sudo tee /etc/systemd/system/hms-backup.timer > /dev/null <<'EOF'
[Unit]
Description=Daily HMS backup timer

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now hms-backup.timer

echo "Primary node deployment completed."
