#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
PACKAGE_DIR="$ROOT_DIR/src/comitato/comitato_azure_retirements_v2"
VENV_DIR="$PACKAGE_DIR/.venv"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  PYTHONPATH="$ROOT_DIR" exec python3 -m src.comitato.comitato_azure_retirements_v2 --help
fi

PYTHON_BIN="${PYTHON_BIN:-python3.13}"
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  "$VENV_DIR/bin/python" -m pip install --disable-pip-version-check -r "$PACKAGE_DIR/requirements.txt"
fi

PYTHONPATH="$ROOT_DIR" exec "$VENV_DIR/bin/python" -m src.comitato.comitato_azure_retirements_v2 "$@"
