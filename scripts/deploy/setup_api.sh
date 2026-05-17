#!/usr/bin/env bash
# Setup Python virtualenv and log directory for HMS API.
# This is called by deploy.sh; can also be used standalone.
set -euo pipefail

HMS_DIR="${HMS_DIR:-/opt/hms}"
VENV_DIR="${HMS_DIR}/venv"
CURRENT="${HMS_DIR}/current"
LOG_DIR="/var/log/hms"
HMS_USER="hms"

if [ ! -d "$CURRENT" ]; then
    echo "Symlink $CURRENT does not exist — skipping API setup"
    exit 0
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtualenv at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
    chown -R "$HMS_USER:$HMS_USER" "$VENV_DIR"
fi

REQ_FILE="$CURRENT/server/src/requirements.txt"
if [ -f "$REQ_FILE" ]; then
    echo "Installing Python requirements from $REQ_FILE"
    sudo -u "$HMS_USER" "$VENV_DIR/bin/pip" install --upgrade pip
    sudo -u "$HMS_USER" "$VENV_DIR/bin/pip" install -r "$REQ_FILE"
else
    echo "requirements.txt not found at $REQ_FILE — skipping pip install"
fi

install -d -m 755 -o "$HMS_USER" -g "$HMS_USER" "$LOG_DIR"
echo "API venv ready at $VENV_DIR | logs in $LOG_DIR"
