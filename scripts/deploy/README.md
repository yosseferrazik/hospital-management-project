Deployment helpers for Hospital Management System

Two convenience scripts are provided to prepare the primary and the standby nodes.

1) deploy_primary.sh
   - Installs system packages required by the HMS primary node
   - Creates directories and deploys operational scripts to /opt/hms/scripts
   - Installs a systemd timer to run daily backups at 02:00

Usage: run on the primary node after cloning the repository:

    sudo bash scripts/deploy/deploy_primary.sh

2) deploy_standby.sh
   - Prepares an AWS EC2 instance as a standby
   - Uses pg_basebackup to clone the primary

Usage (run on standby):

    PRIMARY_IP=<primary tailscale ip> sudo bash scripts/deploy/deploy_standby.sh

Networking

This project assumes Tailscale is used to connect nodes. Ensure tailscaled is running and the nodes can reach each other via their Tailscale IPs.
