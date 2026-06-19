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
VENV_DIR="${SCRIPT_DIR}/.venv"
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"
REQUIREMENTS_STAMP="${VENV_DIR}/.requirements.sha256"
RESOLVED_SCOPE_ARGS=()

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

venv_python() {
    printf '%s' "${VENV_DIR}/bin/python"
}

python_version_of() {
    local python_bin="$1"
    "${python_bin}" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))'
}

resolve_python_bin() {
    local required_version="$1"
    local required_major_minor="${required_version%.*}"
    local pyenv_python=""
    local candidate
    local detected_version
    local -a candidates=()

    if [[ -n "${PYTHON_BIN:-}" ]]; then
        candidates+=("${PYTHON_BIN}")
    fi

    if command -v pyenv >/dev/null 2>&1; then
        if pyenv_python="$(pyenv which python 2>/dev/null)"; then
            candidates+=("${pyenv_python}")
        fi
    fi

    candidates+=("python${required_version}" "python${required_major_minor}" "python3")

    for candidate in "${candidates[@]}"; do
        if ! command -v "${candidate}" >/dev/null 2>&1; then
            continue
        fi

        detected_version="$(python_version_of "${candidate}")"
        if [[ "${detected_version}" == "${required_version}" ]]; then
            printf '%s' "${candidate}"
            return 0
        fi
    done

    local fallback_bin="${PYTHON_BIN:-python3}"
    local fallback_version="not-found"
    if command -v "${fallback_bin}" >/dev/null 2>&1; then
        fallback_version="$(python_version_of "${fallback_bin}")"
    fi

    log_error "Python version mismatch: required ${required_version} from .python-version, detected ${fallback_version} via ${fallback_bin}"
    log_error "Install Python ${required_version}, set PYTHON_BIN to a matching executable, or make pyenv expose that version"
    return 1
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

ensure_virtualenv() {
    local required_version
    required_version="$(read_required_python_version)"

    if [[ -x "$(venv_python)" ]]; then
        local existing_venv_version
        existing_venv_version="$(python_version_of "$(venv_python)")"

        if [[ "${existing_venv_version}" == "${required_version}" ]]; then
            log_info "Using virtual environment Python ${existing_venv_version}"
            return 0
        fi

        log_warn "Local virtual environment uses Python ${existing_venv_version}; recreating with ${required_version}"
        rm -rf "${VENV_DIR}"
    fi

    local python_bin
    python_bin="$(resolve_python_bin "${required_version}")"

    log_info "Creating local virtual environment at ${VENV_DIR} with ${python_bin}"
    "${python_bin}" -m venv "${VENV_DIR}"

    local created_venv_version
    created_venv_version="$(python_version_of "$(venv_python)")"
    if [[ "${created_venv_version}" != "${required_version}" ]]; then
        log_error "Virtual environment mismatch: required ${required_version}, detected ${created_venv_version}"
        return 1
    fi

    log_info "Using virtual environment Python ${created_venv_version}"
}

requirements_digest() {
    if [[ ! -f "${REQUIREMENTS_FILE}" ]]; then
        log_error "Requirements file not found: ${REQUIREMENTS_FILE}"
        return 1
    fi

    shasum -a 256 "${REQUIREMENTS_FILE}" | awk '{print $1}'
}

install_requirements_if_needed() {
    local current_digest
    current_digest="$(requirements_digest)"

    local installed_digest=""
    if [[ -f "${REQUIREMENTS_STAMP}" ]]; then
        installed_digest="$(<"${REQUIREMENTS_STAMP}")"
    fi

    if [[ "${current_digest}" == "${installed_digest}" ]]; then
        log_info "Python dependencies already synchronized"
        return 0
    fi

    log_info "Installing locked Python dependencies"
    "$(venv_python)" -m pip install --upgrade pip >/dev/null
    "$(venv_python)" -m pip install --require-hashes -r "${REQUIREMENTS_FILE}"
    printf '%s\n' "${current_digest}" > "${REQUIREMENTS_STAMP}"
    log_success "Python dependencies synchronized"
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

effective_mode() {
    local mode="${AZURE_RETIREMENTS_MODE:-live}"
    local current_arg

    while [[ $# -gt 0 ]]; do
        current_arg="$1"
        case "${current_arg}" in
            --mode)
                if [[ $# -lt 2 ]]; then
                    break
                fi
                mode="$2"
                shift 2
            ;;
            --mode=*)
                mode="${current_arg#--mode=}"
                shift
            ;;
            *)
                shift
            ;;
        esac
    done

    printf '%s' "${mode}"
}

has_explicit_scope() {
    if [[ -n "${AZURE_SUBSCRIPTIONS:-}" || -n "${AZURE_MANAGEMENT_GROUPS:-}" ]]; then
        return 0
    fi

    local current_arg
    while [[ $# -gt 0 ]]; do
        current_arg="$1"
        case "${current_arg}" in
            --subscriptions|--management-groups)
                return 0
            ;;
            --subscriptions=*|--management-groups=*)
                return 0
            ;;
        esac
        shift
    done

    return 1
}

discover_default_subscriptions() {
    if ! command -v az >/dev/null 2>&1; then
        log_error "Azure CLI not found and no live scope was provided"
        log_error "Install az, pass --subscriptions/--management-groups, or use --mode schema-only"
        return 1
    fi

    local subscriptions_tsv
    if ! subscriptions_tsv="$(az account list --all --query "[?state=='Enabled'].id" -o tsv 2>/dev/null)"; then
        log_error "Unable to resolve enabled Azure CLI subscriptions for the default live run"
        log_error "Run 'az login' and select a subscription, or pass --subscriptions/--management-groups explicitly"
        return 1
    fi

    subscriptions_tsv="$(printf '%s\n' "${subscriptions_tsv}" | awk 'NF')"
    if [[ -z "${subscriptions_tsv}" ]]; then
        log_error "No enabled Azure CLI subscriptions were found for the default live run"
        log_error "Pass --subscriptions/--management-groups explicitly, or use --mode schema-only"
        return 1
    fi

    printf '%s' "$(printf '%s\n' "${subscriptions_tsv}" | paste -sd, -)"
}

build_default_scope_args() {
    RESOLVED_SCOPE_ARGS=()

    local mode
    mode="$(effective_mode "$@")"
    if [[ "${mode}" != "live" ]]; then
        return 0
    fi

    if has_explicit_scope "$@"; then
        return 0
    fi

    local subscriptions_csv
    subscriptions_csv="$(discover_default_subscriptions)"

    local subscription_count
    subscription_count="$(printf '%s' "${subscriptions_csv}" | awk -F',' '{print NF}')"
    RESOLVED_SCOPE_ARGS=("--subscriptions" "${subscriptions_csv}")

    if [[ "${subscription_count}" -gt 1 ]]; then
        log_info "No explicit live scope provided; defaulting to ${subscription_count} enabled Azure CLI subscription(s) with degraded mode"
        RESOLVED_SCOPE_ARGS+=("--allow-degraded")
        return 0
    fi

    log_info "No explicit live scope provided; defaulting to ${subscription_count} enabled Azure CLI subscription(s)"
}

run_python() {
    if [[ ! -f "${PYTHON_SCRIPT}" ]]; then
        log_error "Python entrypoint not found: ${PYTHON_SCRIPT}"
        return 1
    fi

    local -a python_args=()
    if ! build_default_scope_args "$@"; then
        return 1
    fi

    if [[ "${#RESOLVED_SCOPE_ARGS[@]}" -gt 0 ]]; then
        python_args=("${RESOLVED_SCOPE_ARGS[@]}" "$@")
    else
        python_args=("$@")
    fi

    log_info "Launching exporter"
    "$(venv_python)" "${PYTHON_SCRIPT}" "${python_args[@]}"
    log_success "Exporter finished"
}

main() {
    load_env_file
    ensure_virtualenv
    install_requirements_if_needed

    if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
        "$(venv_python)" "${PYTHON_SCRIPT}" --help
        exit 0
    fi

    run_python "$@"
}

main "$@"
