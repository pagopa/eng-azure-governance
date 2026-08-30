#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PACKAGE_DIR="$ROOT_DIR/src/comitato/comitato_azure_retirements_v2"
VENV_DIR="$PACKAGE_DIR/.venv"

arguments=("$@")
format_option_present=false
requested_format="human"
for ((index = 0; index < ${#arguments[@]}; index++)); do
    case "${arguments[index]}" in
        --output-format)
            format_option_present=true
            if ((index + 1 < ${#arguments[@]})); then
                requested_format="${arguments[index + 1]}"
            fi
        ;;
        --output-format=*)
            format_option_present=true
            requested_format="${arguments[index]#--output-format=}"
        ;;
    esac
done

interactive_human=false
if [[ "$requested_format" == "human" && -t 2 ]]; then
    interactive_human=true
fi

log_info() {
    if [[ "$interactive_human" == true ]]; then
        printf '[INFO] %s\n' "$1" >&2
    fi
}

log_success() {
    if [[ "$interactive_human" == true ]]; then
        printf '[ OK ] %s\n' "$1" >&2
    fi
}

log_warn() {
    if [[ "$interactive_human" == true ]]; then
        printf '[WARN] %s\n' "$1" >&2
    fi
}

log_error() {
    if [[ "$interactive_human" == true ]]; then
        printf '[ERROR] %s\n' "$1" >&2
    fi
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    PYTHONPATH="$ROOT_DIR" exec python3 -m src.comitato.comitato_azure_retirements_v2 --help
fi

if [[ "$format_option_present" == false ]]; then
    arguments+=(--output-format human)
fi

PYTHON_BIN="${PYTHON_BIN:-python3.13}"
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
        log_error "Python interpreter not found: $PYTHON_BIN"
        exit 127
    fi
    log_info "Azure Retirements v2: creating the local Python environment"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
    log_info "Azure Retirements v2: installing locked dependencies"
    "$VENV_DIR/bin/python" -m pip install --disable-pip-version-check -r "$PACKAGE_DIR/requirements.txt"
    log_success "Azure Retirements v2: environment ready"
fi

log_info "Azure Retirements v2: launching report run"
PYTHONPATH="$ROOT_DIR" exec "$VENV_DIR/bin/python" -m src.comitato.comitato_azure_retirements_v2 "${arguments[@]}"
