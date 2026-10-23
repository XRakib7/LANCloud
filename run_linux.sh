#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
    PY=python3
else
    PY=python
fi

if ! "$PY" -c "import flask" >/dev/null 2>&1; then
    echo "Installing dependencies..."
    "$PY" -m pip install -r requirements.txt
fi

exec "$PY" app.py
