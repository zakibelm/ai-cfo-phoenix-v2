#!/usr/bin/env bash
set -euo pipefail

# This script ensures the backend dependencies are installed before launching FastAPI.
# Priority: Poetry (if available). Fallback: local virtualenv + pip requirements.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR%/scripts}"
cd "$PROJECT_ROOT"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

if command -v poetry >/dev/null 2>&1; then
  # Poetry available: ensure env ready then run.
  if ! poetry run python -c "import uvicorn" >/dev/null 2>&1; then
    echo "Installation des dépendances Poetry (une seule fois)..."
    poetry install
  fi

  exec poetry run uvicorn main:app --host "$HOST" --port "$PORT"
fi

# Fallback path: no Poetry installed. Use a local virtualenv with pip requirements.
PYTHON_BIN="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-${PROJECT_ROOT}/.venv}"

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "Poetry absent : création d'un environnement virtuel local dans $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if ! python -c "import uvicorn" >/dev/null 2>&1; then
  echo "Installation des dépendances Python via pip (fallback)..."
  pip install --upgrade pip
  pip install -r requirements.txt
fi

exec "$VENV_DIR/bin/uvicorn" main:app --host "$HOST" --port "$PORT"
