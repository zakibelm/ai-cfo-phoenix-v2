#!/usr/bin/env bash
set -euo pipefail

# This script ensures the Poetry environment is ready before starting the backend.
# It installs dependencies on first run and then launches the FastAPI server.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR%/scripts}"
cd "$PROJECT_ROOT"

if ! command -v poetry >/dev/null 2>&1; then
  echo "Poetry n'est pas installé. Veuillez l'installer depuis https://python-poetry.org/docs/#installation." >&2
  exit 1
fi

if ! poetry run python -c "import uvicorn" >/dev/null 2>&1; then
  echo "Installation des dépendances Poetry (une seule fois)..."
  poetry install
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

exec poetry run uvicorn main:app --host "$HOST" --port "$PORT"
