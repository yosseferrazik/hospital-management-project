#!/usr/bin/env bash
# Prepare standby node for PostgreSQL 16 streaming replication.
# Run this on the standby node (Sion / hms-secondary-node).
#
# Usage:
#   PRIMARY_IP=100.78.155.2 sudo bash scripts/deploy/deploy_standby.sh

set -euo pipefail

if [ -z "${PRIMARY_IP:-}" ]; then
    echo "Usage: PRIMARY_IP=<primary ip> $0"
    exit 1
fi

echo "Preparing standby to replicate from primary at $PRIMARY_IP"

# Stop PostgreSQL if running
if systemctl is-active --quiet postgresql; then
    systemctl stop postgresql
fi

# Clear existing data directory
PG_DATA=$(pg_lsclusters -h 2>/dev/null | head -1 | awk '{print $6}' || echo "/var/lib/postgresql/16/main")
rm -rf "$PG_DATA"/*

echo "Running pg_basebackup from $PRIMARY_IP..."
sudo -u postgres pg_basebackup -h "$PRIMARY_IP" -D "$PG_DATA" -U replicator -P -v -R

systemctl start postgresql
echo "Standby configured. Verify replication status on primary."
