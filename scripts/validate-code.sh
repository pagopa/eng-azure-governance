#!/usr/bin/env bash
set -euo pipefail

SOURCE="${BASH_SOURCE[0]}"
while [[ -h "${SOURCE}" ]]; do
  SOURCE_DIR="$(cd -- "$(dirname -- "${SOURCE}")" && pwd)"
  SOURCE="$(readlink -- "${SOURCE}")"
  [[ "${SOURCE}" == /* ]] || SOURCE="${SOURCE_DIR}/${SOURCE}"
done
SCRIPT_DIR="$(cd -- "$(dirname -- "${SOURCE}")" && pwd)"
REPOSITORY_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
cd -- "${REPOSITORY_ROOT}"

if [[ -z "${PYTHON_BIN:-}" ]]; then
  VENV_PYTHON="${REPOSITORY_ROOT}/src/comitato/comitato_azure_retirements_v2/.venv/bin/python"
  if [[ -x "${VENV_PYTHON}" ]]; then
    PYTHON_BIN="${VENV_PYTHON}"
  else
    PYTHON_BIN="python3"
  fi
fi
command -v "${PYTHON_BIN}" >/dev/null 2>&1 || {
  printf 'ERROR: Python interpreter not found: %s\n' "${PYTHON_BIN}" >&2
  exit 2
}
exec "${PYTHON_BIN}" -m tools.validate_code.validate_code --root "${REPOSITORY_ROOT}" "$@"