#!/bin/sh

set -eu

CDPATH=
export CDPATH
SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/.." && git rev-parse --show-toplevel)
GRAPHIFY_OUT="$REPO_ROOT/graphify-out"

GRAPHIFY_PYTHON=${GRAPHIFY_PYTHON:-}
if [ -z "$GRAPHIFY_PYTHON" ] && [ -f "$GRAPHIFY_OUT/.graphify_python" ]; then
    GRAPHIFY_PYTHON=$(sed -e 's/[[:space:]]//g' "$GRAPHIFY_OUT/.graphify_python")
fi

if [ -z "$GRAPHIFY_PYTHON" ]; then
    GRAPHIFY_BIN=${GRAPHIFY_BIN:-$(command -v graphify 2>/dev/null || true)}
    if [ -n "$GRAPHIFY_BIN" ] && [ -f "$GRAPHIFY_BIN" ]; then
        GRAPHIFY_PYTHON=$(sed -n '1s/^#!//p' "$GRAPHIFY_BIN" | sed -e 's/[[:space:]]//g')
    fi
fi

if [ -z "$GRAPHIFY_PYTHON" ]; then
    echo "graphify Python interpreter not found; run graphify extract first or set GRAPHIFY_PYTHON" >&2
    exit 1
fi

DEBOUNCE=${GRAPHIFY_WATCH_DEBOUNCE:-3}
export GRAPHIFY_MAX_WORKERS=${GRAPHIFY_MAX_WORKERS:-1}
case "$DEBOUNCE" in
    ''|*[!0-9.]*|.*|*.)
        echo "GRAPHIFY_WATCH_DEBOUNCE must be a positive number" >&2
        exit 2
        ;;
esac

exec "$GRAPHIFY_PYTHON" -m graphify.watch "$REPO_ROOT" --debounce "$DEBOUNCE"
