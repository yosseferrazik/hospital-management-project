#!/bin/bash
# Deploy helper for standby node (AWS EC2)
# This script prepares the standby for streaming replication from the primary. It expects
# that the primary is reachable via Tailscale or network and that replicator credentials are configured.

set -euo pipefail

if [ -z "${PRIMARY_IP:-}" ]; then
  echo "Usage: PRIMARY_IP=<primary ip> $0"
  exit 1
fi

echo "Preparing standby to replicate from $PRIMARY_IP"

sudo apt update
sudo apt install -y postgresql-14 postgresql-client-14

sudo systemctl stop postgresql
sudo rm -rf /var/lib/postgresql/14/main/*

echo "Running pg_basebackup from primary..."
sudo -u postgres pg_basebackup -h "$PRIMARY_IP" -D /var/lib/postgresql/14/main -U replicator -P -v -R

sudo systemctl start postgresql
echo "Standby configured and started. Verify replication on primary."
