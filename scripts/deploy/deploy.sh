#!/usr/bin/env bash
# HMS versioned deploy script
# Deploys the API from the main branch with release versioning, smoke tests,
# and automatic rollback on failure.
#
# Usage:
#   sudo bash scripts/deploy/deploy.sh            # normal deploy (window-checked)
#   sudo bash scripts/deploy/deploy.sh --force    # bypass time window
#   sudo bash scripts/deploy/deploy.sh --rollback # revert to previous release

set -euo pipefail

# --- configuration -----------------------------------------------------------
REPO_URL="https://github.com/yosseferrazik/hospital-management-project.git"
HMS_DIR="/opt/hms"
RELEASES_DIR="$HMS_DIR/releases"
VENV_DIR="$HMS_DIR/venv"
CURRENT_LINK="$HMS_DIR/current"
DEPLOY_META="$HMS_DIR/.deploy_meta"
SERVICE_NAME="hms-api"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
LOG_DIR="/var/log/hms"
LOGROTATE_FILE="/etc/logrotate.d/hms"
REQUIRED_PKG=("python3-venv" "build-essential" "libpq-dev" "git" "rsync")
MAX_RELEASES=5
SMOKE_RETRIES=5
SMOKE_INTERVAL=3
WIN_MORNING_START=6
WIN_MORNING_END=10
WIN_NIGHT_START=20
WIN_NIGHT_END=23

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[INFO]${NC}  $(date '+%Y-%m-%d %H:%M:%S') - $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $(date '+%Y-%m-%d %H:%M:%S') - $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $*" >&2; }
# -----------------------------------------------------------------------------

usage() {
    sed -n '2,/^$/s/^# //p' "$0"
    exit 0
}

check_time_window() {
    local h; h=$(date +%-H)
    if [ "$h" -ge "$WIN_MORNING_START" ] && [ "$h" -lt "$WIN_MORNING_END" ]; then
        return 0
    fi
    if [ "$h" -ge "$WIN_NIGHT_START" ] && [ "$h" -lt "$WIN_NIGHT_END" ]; then
        return 0
    fi
    log_error "Outside deploy window (${WIN_MORNING_START}:00-${WIN_MORNING_END}:00 or ${WIN_NIGHT_START}:00-${WIN_NIGHT_END}:00). Use --force to override."
    return 1
}

ensure_hms_user() {
    if ! id -u hms &>/dev/null; then
        log_info "Creating system user 'hms'"
        useradd --system --home-dir "$HMS_DIR" --shell /usr/sbin/nologin hms
    fi
}

ensure_directories() {
    install -d -m 755 -o hms -g hms "$RELEASES_DIR"
    install -d -m 755 -o hms -g hms "$LOG_DIR"
}

install_system_packages() {
    local missing=()
    for pkg in "${REQUIRED_PKG[@]}"; do
        if ! dpkg -s "$pkg" &>/dev/null; then missing+=("$pkg"); fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        log_info "Installing system packages: ${missing[*]}"
        DEBIAN_FRONTEND=noninteractive apt-get install -y "${missing[@]}"
    fi
}

ensure_repo() {
    local repo_dir="$HMS_DIR/repo"
    if [ -d "$repo_dir/.git" ]; then
        log_info "Updating existing repo at $repo_dir"
        git -C "$repo_dir" fetch origin
        git -C "$repo_dir" reset --hard origin/main
    else
        log_info "Cloning repository to $repo_dir"
        git clone "$REPO_URL" "$repo_dir"
    fi
    echo "$repo_dir"
}

get_commit_sha() {
    git -C "$1" rev-parse --short HEAD
}

create_release() {
    local repo_dir="$1" sha="$2"
    local release_dir="$RELEASES_DIR/$sha"
    if [ -d "$release_dir" ]; then
        log_info "Release $sha already exists, syncing"
        rsync -a --delete --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' "$repo_dir/" "$release_dir/"
    else
        log_info "Creating release $sha"
        mkdir -p "$release_dir"
        rsync -a --exclude='venv' --exclude='*.pyc' --exclude='__pycache__' "$repo_dir/" "$release_dir/"
    fi
    chown -R hms:hms "$release_dir"
    echo "$release_dir"
}

setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        log_info "Creating virtualenv at $VENV_DIR"
        python3 -m venv "$VENV_DIR"
        chown -R hms:hms "$VENV_DIR"
    fi
    local req_file="$CURRENT_LINK/server/src/requirements.txt"
    if [ -f "$req_file" ]; then
        log_info "Installing Python requirements"
        sudo -u hms "$VENV_DIR/bin/pip" install --upgrade pip
        sudo -u hms "$VENV_DIR/bin/pip" install -r "$req_file"
    else
        log_warn "requirements.txt not found at $req_file"
    fi
}

update_symlink() {
    local release_dir="$1"
    local previous
    if [ -L "$CURRENT_LINK" ]; then
        previous=$(readlink -f "$CURRENT_LINK")
    fi
    ln -sfn "$release_dir" "$CURRENT_LINK"
    chown -h hms:hms "$CURRENT_LINK"
    echo "$previous"
}

install_service() {
    local unit_src="$CURRENT_LINK/scripts/systemd/hms-api.service"
    if [ -f "$unit_src" ]; then
        cp "$unit_src" "$SERVICE_FILE"
        systemctl daemon-reload
        log_info "systemd unit installed"
    else
        log_error "Service unit not found at $unit_src"
        return 1
    fi
}

install_logrotate() {
    local logrotate_src="$CURRENT_LINK/scripts/logrotate/hms"
    if [ -f "$logrotate_src" ]; then
        cp "$logrotate_src" "$LOGROTATE_FILE"
        log_info "logrotate config installed"
    fi
}

restart_service() {
    log_info "Restarting $SERVICE_NAME"
    systemctl enable --now "$SERVICE_NAME" 2>/dev/null || true
    systemctl restart "$SERVICE_NAME"
}

smoke_test() {
    local uri="http://localhost:5000/health"
    log_info "Smoke test: $uri"
    for i in $(seq 1 "$SMOKE_RETRIES"); do
        if curl -sf "$uri" >/dev/null 2>&1; then
            log_info "Smoke test passed (attempt $i)"
            return 0
        fi
        log_warn "Smoke test failed (attempt $i/$SMOKE_RETRIES), retrying in ${SMOKE_INTERVAL}s"
        sleep "$SMOKE_INTERVAL"
    done
    log_error "Smoke test failed after $SMOKE_RETRIES attempts"
    return 1
}

save_meta() {
    local sha="$1" previous="$2" status="$3"
    cat > "$DEPLOY_META" <<EOF
PREVIOUS_RELEASE=$(basename "${previous:-}")
CURRENT_RELEASE=$sha
DEPLOY_TIMESTAMP=$(date -Iseconds)
DEPLOY_STATUS=$status
EOF
    chown hms:hms "$DEPLOY_META"
    chmod 600 "$DEPLOY_META"
}

cleanup_old() {
    local keep=$MAX_RELEASES
    local releases; releases=$(ls -1 "$RELEASES_DIR" 2>/dev/null | sort || true)
    local count; count=$(echo "$releases" | wc -l)
    if [ "$count" -gt "$keep" ]; then
        local remove=$((count - keep))
        log_info "Cleaning up $remove old release(s)"
        echo "$releases" | head -n "$remove" | while read -r r; do
            rm -rf "$RELEASES_DIR/$r"
            log_info "Removed release $r"
        done
    fi
}

do_rollback() {
    if [ ! -f "$DEPLOY_META" ]; then
        log_error "No deploy metadata found, cannot rollback"
        return 1
    fi
    # shellcheck source=/dev/null
    . "$DEPLOY_META"
    if [ -z "${PREVIOUS_RELEASE:-}" ] || [ ! -d "$RELEASES_DIR/$PREVIOUS_RELEASE" ]; then
        log_error "No previous release available for rollback"
        return 1
    fi
    log_info "Rolling back to release $PREVIOUS_RELEASE"
    local release_dir="$RELEASES_DIR/$PREVIOUS_RELEASE"
    update_symlink "$release_dir"
    restart_service
    if smoke_test; then
        save_meta "$(basename "$release_dir")" "" "rolled_back"
        log_info "Rollback successful, running release $PREVIOUS_RELEASE"
    else
        log_error "Rollback smoke test failed — manual intervention required"
        return 1
    fi
}

# --- main --------------------------------------------------------------------
main() {
    if [[ "$*" == *--help* ]] || [[ "$*" == *-h* ]]; then usage; fi

    # Must be root
    if [ "$EUID" -ne 0 ]; then log_error "Please run as root"; exit 1; fi

    # Parse flags
    local ROLLBACK=false FORCE=false
    for arg in "$@"; do
        case "$arg" in
            --rollback) ROLLBACK=true ;;
            --force)    FORCE=true ;;
        esac
    done

    if $ROLLBACK; then
        do_rollback
        exit $?
    fi

    if ! $FORCE; then check_time_window; fi

    log_info "=== HMS Deploy started ==="

    install_system_packages
    ensure_hms_user
    ensure_directories

    local repo_dir; repo_dir=$(ensure_repo)
    local sha; sha=$(get_commit_sha "$repo_dir")

    # Check if already deployed
    if [ -f "$DEPLOY_META" ]; then
        # shellcheck source=/dev/null
        . "$DEPLOY_META"
        if [ "${CURRENT_RELEASE:-}" = "$sha" ]; then
            log_info "Release $sha is already current, nothing to do"
            exit 0
        fi
    fi

    local release_dir; release_dir=$(create_release "$repo_dir" "$sha")
    local previous; previous=$(update_symlink "$release_dir")

    # venv setup must run AFTER the symlink is updated so it points at the new release
    setup_venv
    install_service
    install_logrotate
    restart_service

    if smoke_test; then
        save_meta "$sha" "$previous" "success"
        cleanup_old
        log_info "=== Deploy of $sha completed successfully ==="
    else
        log_error "=== Deploy FAILED, initiating rollback ==="
        # Restore previous symlink
        if [ -n "$previous" ]; then
            ln -sfn "$previous" "$CURRENT_LINK"
            restart_service
            if smoke_test; then
                save_meta "$(basename "$previous")" "$sha" "rolled_back"
                log_info "Rollback to $(basename "$previous") successful"
            else
                log_error "CRITICAL: Rollback smoke test also failed!"
                save_meta "$(basename "$previous")" "$sha" "rollback_failed"
                return 1
            fi
        else
            log_error "No previous release to rollback to"
            save_meta "$sha" "" "failed"
            return 1
        fi
    fi
}

main "$@"
