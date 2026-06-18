#!/usr/bin/env bash
#
# Purpose: Launch the Azure retirements export tool with local defaults.
# Usage examples:
#   ./run.sh
#   ./run.sh --mode live --subscriptions "sub-1,sub-2"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/comitato-azure-retirements.py"
ENV_FILE="${SCRIPT_DIR}/.env"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
PYTHON_VERSION_FILE="${REPO_ROOT}/.python-version"

log_info() {
    printf 'ℹ️  %s\n' "$1"
}

log_success() {
    printf '✅ %s\n' "$1"
}

log_warn() {
    printf '⚠️  %s\n' "$1"
}

log_error() {
    printf '❌ %s\n' "$1" >&2
}

resolve_python_bin() {
    printf '%s' "${PYTHON_BIN:-python3}"
}

read_required_python_version() {
    if [[ ! -f "${PYTHON_VERSION_FILE}" ]]; then
        log_error "Python version file not found: ${PYTHON_VERSION_FILE}"
        return 1
    fi
    
    local required_version
    required_version="$(tr -d '[:space:]' < "${PYTHON_VERSION_FILE}")"
    if [[ -z "${required_version}" ]]; then
        log_error "Python version file is empty: ${PYTHON_VERSION_FILE}"
        return 1
    fi
    
    printf '%s' "${required_version}"
}

assert_python_version() {
    local python_bin
    python_bin="$(resolve_python_bin)"
    
    if ! command -v "${python_bin}" >/dev/null 2>&1; then
        log_error "Python interpreter not found: ${python_bin}"
        return 1
    fi
    
    local required_version
    required_version="$(read_required_python_version)"
    
    local detected_version
    detected_version="$("${python_bin}" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')"
    
    if [[ "${detected_version}" != "${required_version}" ]]; then
        log_error "Python version mismatch: required ${required_version} from .python-version, detected ${detected_version} via ${python_bin}"
        log_error "Use the matching interpreter or set PYTHON_BIN to a Python ${required_version} executable"
        return 1
    fi
    
    log_info "Using Python ${detected_version} (from .python-version)"
}

load_env_file() {
    if [[ -f "${ENV_FILE}" ]]; then
        log_info "Loading environment from ${ENV_FILE}"
        set -a
        # shellcheck disable=SC1090
        source "${ENV_FILE}"
        set +a
    fi
}

run_python() {
    local python_bin
    python_bin="$(resolve_python_bin)"
    
    if [[ ! -f "${PYTHON_SCRIPT}" ]]; then
        log_error "Python entrypoint not found: ${PYTHON_SCRIPT}"
        return 1
    fi
    
    log_info "Launching exporter"
    "${python_bin}" "${PYTHON_SCRIPT}" "$@"
    log_success "Exporter finished"
}

main() {
    load_env_file
    assert_python_version
    
    local python_bin
    python_bin="$(resolve_python_bin)"
    
    if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
        "${python_bin}" "${PYTHON_SCRIPT}" --help
        exit 0
    fi
    
    run_python "$@"
}

main "$@"
