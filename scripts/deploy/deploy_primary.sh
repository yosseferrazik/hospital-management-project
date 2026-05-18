#!/usr/bin/env bash
# Deploy script for primary node (Hospital Sa Palomera)
# Installs system packages and sets up the environment for deploy.sh.
# Usage: sudo bash scripts/deploy/deploy_primary.sh
# Then run: sudo bash scripts/deploy/deploy.sh --force

set -euo pipefail

echo "Deploying HMS primary node..."

REQUIRED_PKG=("python3-venv" "build-essential" "libpq-dev" "git" "rsync")
for pkg in "${REQUIRED_PKG[@]}"; do
    if ! dpkg -s "$pkg" &>/dev/null; then
        echo "Installing $pkg..."
        DEBIAN_FRONTEND=noninteractive apt-get install -y "$pkg"
    fi
done

if ! id -u hms >/dev/null 2>&1; then
    useradd --system --home-dir /opt/hms --shell /usr/sbin/nologin hms
    echo "Created system user 'hms'"
fi

install -d -m 755 -o hms -g hms /opt/hms/releases
install -d -m 755 -o hms -g hms /var/log/hms

if [ -f ".env.example" ] && [ ! -f /etc/hms.env ]; then
    cp .env.example /etc/hms.env
    chmod 600 /etc/hms.env
    echo "Installed /etc/hms.env from .env.example — edit to add secrets"
fi

echo "Primary node setup complete. Run: sudo bash scripts/deploy/deploy.sh --force"
