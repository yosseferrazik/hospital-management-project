#!/usr/bin/env bash
# HMS Full Service Recovery Script (Bare Metal)
# Restores the entire HMS service from scratch — deploy code,
# restore PGDATA (physical), restore config files, restore DB.
#
# Use this when /opt/hms or /var/lib/postgresql has been lost or
# corrupted, or when migrating to a new primary node.
#
# Prerequisites:
#   - Fresh Ubuntu 22.04+ server with PostgreSQL 16
#   - Backup files accessible (local path, NFS mount, or SCP'd in)
#   - Root or sudo access
#   - Git access to the repository
#
# Usage:
#   sudo bash restore_service.sh                                        # interactive (latest)
#   sudo bash restore_service.sh --backup-dir /backups/local            # custom backup dir
#   sudo bash restore_service.sh --timestamp 20260522_120000            # specific point in time
#   sudo bash restore_service.sh --physical-only                        # restore PGDATA only
#   sudo bash restore_service.sh --skip-physical                        # skip PGDATA restore
#   sudo bash restore_service.sh --skip-db                              # skip logical DB restore
#   sudo bash restore_service.sh --skip-deploy                          # skip code deploy
#   sudo bash restore_service.sh --dry-run                              # preview only
#
# Environment variables:
#   HMS_BACKUP_DIR   - Backup directory (default: /backups/local)
#   HMS_RESTORE_TS   - Timestamp to restore (default: latest)
#   REPO_URL         - Git repository URL
#   HMS_PGDATA_DIR   - Override PGDATA directory path

set -euo pipefail

# --- configuration -----------------------------------------------------------
HMS_BACKUP_DIR="${HMS_BACKUP_DIR:-/backups/local}"
HMS_RESTORE_TS="${HMS_RESTORE_TS:-latest}"
REPO_URL="${REPO_URL:-https://github.com/yosseferrazik/hospital-management-project.git}"
HMS_DIR="/opt/hms"
RELEASES_DIR="$HMS_DIR/releases"
VENV_DIR="$HMS_DIR/venv"
CURRENT_LINK="$HMS_DIR/current"
SERVICE_NAME="hms-api"
BACKUP_SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/backup_database.py"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[INFO]${NC}  $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2; }
log_step()  { echo -e "${CYAN}[STEP]${NC}  $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2; }

SKIP_DB=false
SKIP_DEPLOY=false
SKIP_PHYSICAL=false
PHYSICAL_ONLY=false
DRY_RUN=false

usage() {
    sed -n '2,/^$/s/^# //p' "$0"
    exit 0
}
# -----------------------------------------------------------------------------

check_prerequisites() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run as root (sudo)"
        exit 1
    fi

    local missing=()
    for cmd in python3 pg_dump pg_restore git rsync systemctl; do
        if ! command -v "$cmd" &>/dev/null 2>&1; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing required commands: ${missing[*]}"
        log_info "Install with: apt-get install -y postgresql-client git rsync python3"
        exit 1
    fi

    if [ ! -d "$HMS_BACKUP_DIR" ]; then
        log_error "Backup directory not found: $HMS_BACKUP_DIR"
        log_info "Mount the backup location or copy backups to this path."
        exit 1
    fi
}

run_backup_script() {
    HMS_BACKUP_DIR="$HMS_BACKUP_DIR" \
    HMS_HMS_DIR="${HMS_HMS_DIR:-/opt/hms}" \
    HMS_PGDATA_DIR="${HMS_PGDATA_DIR:-}" \
    python3 "$BACKUP_SCRIPT" "$@"
}

list_available_backups() {
    echo ""
    echo "========================================"
    echo "  Available Backups in $HMS_BACKUP_DIR"
    echo "========================================"
    run_backup_script --list 2>/dev/null || echo "  (backup listing unavailable)"
    echo ""
}

restore_physical() {
    log_step "Restoring PGDATA (physical backup)"

    local pgdata_flag=""
    if [ -n "${HMS_PGDATA_DIR:-}" ]; then
        pgdata_flag="--pgdata-dir $HMS_PGDATA_DIR"
    fi

    if $DRY_RUN; then
        log_info "[DRY-RUN] Would run: backup_database.py --physical-restore $1 $pgdata_flag --dry-run"
        run_backup_script --physical-restore "$1" $pgdata_flag --dry-run
        return 0
    fi

    run_backup_script --physical-restore "$1" $pgdata_flag <<< "yes"
    local ret=$?

    if [ $ret -ne 0 ]; then
        log_error "PGDATA physical restore failed"
        return 1
    fi

    log_info "PGDATA restored successfully — PostgreSQL is running again"
    return 0
}

deploy_application() {
    log_step "Deploying application from repository"

    if $DRY_RUN; then
        log_info "[DRY-RUN] Would run: deploy.sh to clone and set up $REPO_URL"
        return 0
    fi

    local deploy_script="$(cd "$(dirname "$0")/../deploy" && pwd)/deploy.sh"
    if [ -f "$deploy_script" ]; then
        bash "$deploy_script" --force
    else
        log_info "Deploy script not found locally, running standalone deploy..."

        install -d -m 755 -o hms -g hms "$RELEASES_DIR" 2>/dev/null || mkdir -p "$RELEASES_DIR"

        local repo_dir="$HMS_DIR/repo"
        if [ -d "$repo_dir/.git" ]; then
            log_info "Updating existing repo"
            git -C "$repo_dir" fetch origin
            git -C "$repo_dir" reset --hard origin/main
        else
            log_info "Cloning repository"
            git clone "$REPO_URL" "$repo_dir"
        fi

        local sha; sha=$(git -C "$repo_dir" rev-parse --short HEAD)
        local release_dir="$RELEASES_DIR/$sha"

        if [ -d "$release_dir" ]; then
            rsync -a --delete --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' "$repo_dir/" "$release_dir/"
        else
            mkdir -p "$release_dir"
            rsync -a --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' "$repo_dir/" "$release_dir/"
        fi

        ln -sfn "$release_dir" "$CURRENT_LINK"

        if [ ! -d "$VENV_DIR" ]; then
            python3 -m venv "$VENV_DIR"
        fi

        local req_file="$CURRENT_LINK/server/src/requirements.txt"
        if [ -f "$req_file" ]; then
            "$VENV_DIR/bin/pip" install --upgrade pip
            "$VENV_DIR/bin/pip" install -r "$req_file"
        fi

        # Install systemd service
        local unit_src="$CURRENT_LINK/scripts/systemd/hms-api.service"
        if [ -f "$unit_src" ]; then
            cp "$unit_src" "/etc/systemd/system/${SERVICE_NAME}.service"
            systemctl daemon-reload
        fi

        # Install logrotate config
        local logrotate_src="$CURRENT_LINK/scripts/logrotate/hms"
        if [ -f "$logrotate_src" ]; then
            cp "$logrotate_src" "/etc/logrotate.d/hms"
        fi
    fi

    log_info "Application deployed"
}

restore_configuration() {
    log_step "Restoring configuration files"

    if $DRY_RUN; then
        log_info "[DRY-RUN] Would run: backup_database.py --config-restore $1 --dry-run"
        run_backup_script --config-restore "$1" --dry-run
        return 0
    fi

    run_backup_script --config-restore "$1" <<< "yes"
    local ret=$?

    if [ $ret -ne 0 ]; then
        log_error "Config restore failed"
        return 1
    fi

    log_info "Configuration restored successfully"
    return 0
}

restore_database() {
    log_step "Restoring database"

    if $DRY_RUN; then
        log_info "[DRY-RUN] Would run: backup_database.py --restore $1 --dry-run"
        run_backup_script --restore "$1" --dry-run
        return 0
    fi

    run_backup_script --restore "$1" <<< "yes"
    local ret=$?

    if [ $ret -ne 0 ]; then
        log_error "Database restore failed"
        return 1
    fi

    log_info "Database restored successfully"
    return 0
}

restart_service() {
    log_step "Restarting HMS service"

    if $DRY_RUN; then
        log_info "[DRY-RUN] Would run: systemctl daemon-reload && systemctl enable --now $SERVICE_NAME && systemctl restart $SERVICE_NAME"
        return 0
    fi

    systemctl daemon-reload 2>/dev/null || true
    systemctl enable --now "$SERVICE_NAME" 2>/dev/null || true
    systemctl restart "$SERVICE_NAME"

    log_info "Service restarted"
}

smoke_test() {
    log_step "Running smoke test"

    if $DRY_RUN; then
        log_info "[DRY-RUN] Would test: http://localhost:5000/health"
        return 0
    fi

    local retries=10
    local interval=3

    for i in $(seq 1 "$retries"); do
        if curl -sf "http://localhost:5000/health" >/dev/null 2>&1; then
            log_info "Smoke test passed (attempt $i)"
            return 0
        fi
        log_warn "Smoke test failed (attempt $i/$retries), retrying in ${interval}s"
        sleep "$interval"
    done

    log_error "Smoke test failed after $retries attempts"
    return 1
}

find_db_backup() {
    local ts="$1"
    if [ "$ts" = "latest" ]; then
        ls -1t "$HMS_BACKUP_DIR"/hsp_db_*.dump 2>/dev/null | head -1
    else
        ls -1t "$HMS_BACKUP_DIR"/hsp_db_"$ts".dump 2>/dev/null | head -1
    fi
}

find_config_backup() {
    local ts="$1"
    if [ "$ts" = "latest" ]; then
        ls -1t "$HMS_BACKUP_DIR"/config_*.tar.gz 2>/dev/null | head -1
    else
        ls -1t "$HMS_BACKUP_DIR"/config_"$ts".tar.gz 2>/dev/null | head -1
    fi
}

find_physical_backup() {
    local ts="$1"
    if [ "$ts" = "latest" ]; then
        ls -1t "$HMS_BACKUP_DIR"/physical_*.tar.gz 2>/dev/null | head -1
    else
        ls -1t "$HMS_BACKUP_DIR"/physical_"$ts".tar.gz 2>/dev/null | head -1
    fi
}

# --- main --------------------------------------------------------------------
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h) usage ;;
            --backup-dir) HMS_BACKUP_DIR="$2"; shift 2 ;;
            --backup-dir=*) HMS_BACKUP_DIR="${1#*=}"; shift ;;
            --timestamp) HMS_RESTORE_TS="$2"; shift 2 ;;
            --timestamp=*) HMS_RESTORE_TS="${1#*=}"; shift ;;
            --skip-db) SKIP_DB=true; shift ;;
            --skip-deploy) SKIP_DEPLOY=true; shift ;;
            --skip-physical) SKIP_PHYSICAL=true; shift ;;
            --physical-only) PHYSICAL_ONLY=true; shift ;;
            --pgdata-dir) HMS_PGDATA_DIR="$2"; shift 2 ;;
            --pgdata-dir=*) HMS_PGDATA_DIR="${1#*=}"; shift ;;
            --dry-run) DRY_RUN=true; shift ;;
            *) log_error "Unknown argument: $1"; usage ;;
        esac
    done

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  HMS Full Service Recovery (Bare Metal)${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo "  Backup directory: $HMS_BACKUP_DIR"
    echo "  Restore timestamp: $HMS_RESTORE_TS"
    echo "  Skip physical: $SKIP_PHYSICAL"
    echo "  Skip logical DB: $SKIP_DB"
    echo "  Skip deploy: $SKIP_DEPLOY"
    echo "  Physical only: $PHYSICAL_ONLY"
    echo "  Dry run: $DRY_RUN"
    echo -e "${GREEN}========================================${NC}"
    echo ""

    check_prerequisites

    if $DRY_RUN; then
        echo -e "${YELLOW}--- DRY RUN MODE ---${NC}"
        echo ""
    fi

    list_available_backups

    # Find backup files
    PHYSICAL_BACKUP=""
    DB_BACKUP=""
    CONFIG_BACKUP=""

    if ! $SKIP_PHYSICAL; then
        PHYSICAL_BACKUP=$(find_physical_backup "$HMS_RESTORE_TS")
        if [ -z "$PHYSICAL_BACKUP" ]; then
            log_warn "No physical PGDATA backup found for timestamp: $HMS_RESTORE_TS"
        else
            log_info "Found physical PGDATA backup: $PHYSICAL_BACKUP"
        fi
    fi

    if ! $SKIP_DB && ! $PHYSICAL_ONLY; then
        DB_BACKUP=$(find_db_backup "$HMS_RESTORE_TS")
        if [ -z "$DB_BACKUP" ]; then
            log_warn "No logical database backup found for timestamp: $HMS_RESTORE_TS"
        else
            log_info "Found logical database backup: $DB_BACKUP"
        fi
    fi

    if ! $PHYSICAL_ONLY; then
        CONFIG_BACKUP=$(find_config_backup "$HMS_RESTORE_TS")
        if [ -z "$CONFIG_BACKUP" ]; then
            log_warn "No configuration backup found for timestamp: $HMS_RESTORE_TS"
        else
            log_info "Found config backup: $CONFIG_BACKUP"
        fi
    fi

    if [ -z "$PHYSICAL_BACKUP" ] && [ -z "$DB_BACKUP" ] && [ -z "$CONFIG_BACKUP" ]; then
        log_error "No backups found for timestamp '$HMS_RESTORE_TS' in $HMS_BACKUP_DIR"
        exit 1
    fi

    if ! $DRY_RUN; then
        echo ""
        echo "========================================"
        echo "  RECOVERY PLAN"
        echo "========================================"
        local step=1
        $SKIP_DEPLOY || { echo "  $step. Deploy application from repository"; step=$((step + 1)); }
        [ -z "$PHYSICAL_BACKUP" ] || { echo "  $step. Restore PGDATA (physical): $(basename "$PHYSICAL_BACKUP")"; step=$((step + 1)); }
        [ -z "$CONFIG_BACKUP" ] || { echo "  $step. Restore configuration: $(basename "$CONFIG_BACKUP")"; step=$((step + 1)); }
        [ -z "$DB_BACKUP" ] || { echo "  $step. Restore database (logical): $(basename "$DB_BACKUP")"; step=$((step + 1)); }
        echo "  $step. Restart service"
        step=$((step + 1))
        echo "  $step. Smoke test"
        echo "========================================"
        echo ""
        read -r -p "Proceed with recovery? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "Recovery cancelled."
            exit 0
        fi
    fi

    # Step 1: Deploy application
    if ! $SKIP_DEPLOY; then
        deploy_application || { log_error "Deploy step failed"; exit 1; }
    else
        log_info "Skipping application deploy (--skip-deploy)"
    fi

    # Step 2: Restore PGDATA (physical)
    if [ -n "$PHYSICAL_BACKUP" ]; then
        restore_physical "$PHYSICAL_BACKUP" || { log_error "Physical restore step failed"; exit 1; }
    elif ! $SKIP_PHYSICAL; then
        log_warn "No physical backup to restore"
    fi

    # Step 3: Restore configuration
    if [ -n "$CONFIG_BACKUP" ] && ! $PHYSICAL_ONLY; then
        restore_configuration "$CONFIG_BACKUP" || { log_error "Config restore step failed"; exit 1; }
    fi

    # Step 4: Restore logical database
    if [ -n "$DB_BACKUP" ] && ! $SKIP_DB && ! $PHYSICAL_ONLY; then
        restore_database "$DB_BACKUP" || { log_error "Database restore step failed"; exit 1; }
    else
        log_info "Skipping logical database restore"
    fi

    # Step 5: Restart service
    restart_service

    # Step 6: Smoke test
    if smoke_test; then
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  HMS SERVICE RECOVERY COMPLETED${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo "  The HMS API service is running and healthy."
        echo "  Verify at: http://localhost:5000/health"
        if [ -n "$PHYSICAL_BACKUP" ]; then
            echo ""
            echo "  PGDATA restored from: $PHYSICAL_BACKUP"
        fi
        if [ -n "$CONFIG_BACKUP" ]; then
            echo "  Config restored from: $CONFIG_BACKUP"
        fi
        if [ -n "$DB_BACKUP" ]; then
            echo "  Database restored from: $DB_BACKUP"
        fi
        echo -e "${GREEN}========================================${NC}"
        exit 0
    else
        log_error "Recovery completed but smoke test FAILED"
        log_error "Check service status: systemctl status $SERVICE_NAME"
        log_error "Check logs: journalctl -u $SERVICE_NAME -n 50"
        exit 1
    fi
}

main "$@"
