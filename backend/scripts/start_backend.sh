#!/usr/bin/env bash
set -euo pipefail

# This script ensures the backend dependencies are installed before launching FastAPI.
# Priority: Poetry (if available). Fallback: local virtualenv + pip requirements.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR%/scripts}"
cd "$PROJECT_ROOT"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# Optional testing/tuning flags
# - BACKEND_START_MODE=print : output the chosen launcher without executing it
# - BACKEND_SKIP_INSTALL=1   : skip dependency checks/installs (useful for CI tests)
BACKEND_START_MODE="${BACKEND_START_MODE:-run}"
BACKEND_SKIP_INSTALL="${BACKEND_SKIP_INSTALL:-0}"

if command -v poetry >/dev/null 2>&1; then
  # Poetry available: ensure env ready then run.
  if [ "$BACKEND_SKIP_INSTALL" != "1" ] && ! poetry run python -c "import uvicorn" >/dev/null 2>&1; then
    echo "Installation des dépendances Poetry (une seule fois)..."
    poetry install
  fi

  if [ "$BACKEND_START_MODE" = "print" ]; then
    echo "launcher=poetry host=$HOST port=$PORT"
    exit 0
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

if [ "$BACKEND_SKIP_INSTALL" != "1" ] && ! python -c "import uvicorn" >/dev/null 2>&1; then
  echo "Installation des dépendances Python via pip (fallback)..."
  pip install --upgrade pip
  pip install -r requirements.txt
fi

if [ "$BACKEND_START_MODE" = "print" ]; then
  echo "launcher=venv path=$VENV_DIR host=$HOST port=$PORT"
  exit 0
fi

exec "$VENV_DIR/bin/uvicorn" main:app --host "$HOST" --port "$PORT"
