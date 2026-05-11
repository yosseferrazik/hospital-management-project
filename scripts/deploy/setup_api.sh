#!/bin/bash
# Small helper to prepare Python virtualenv and logs for the HMS API
set -euo pipefail

API_DIR=/opt/hms/api
VENV_DIR=/opt/hms/venv
HMS_USER=hms

if [ ! -d "$API_DIR" ]; then
  echo "API directory $API_DIR not found, skipping API setup"
  exit 0
fi

echo "Setting up Python virtualenv for HMS API..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-wheel || true

if [ ! -d "$VENV_DIR" ]; then
  sudo python3 -m venv "$VENV_DIR"
  sudo chown -R $HMS_USER:$HMS_USER "$VENV_DIR"
fi

if [ -f "$API_DIR/requirements.txt" ]; then
  echo "Installing Python requirements..."
  sudo -u $HMS_USER "$VENV_DIR/bin/pip" install --upgrade pip
  sudo -u $HMS_USER "$VENV_DIR/bin/pip" install -r "$API_DIR/requirements.txt"
else
  echo "No requirements.txt found in $API_DIR — skipping pip install"
fi

sudo mkdir -p /var/log/hms
sudo touch /var/log/hms/api.log
sudo chown -R $HMS_USER:$HMS_USER /var/log/hms

echo "API virtualenv prepared at $VENV_DIR. Logs: /var/log/hms/api.log"

exit 0
