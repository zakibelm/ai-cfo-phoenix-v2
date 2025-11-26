import os
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "start_backend.sh"


def run_start_script(env):
    result = subprocess.run(
        ["bash", str(SCRIPT_PATH)],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip().splitlines()[-1]


def test_start_backend_prefers_poetry_when_available(tmp_path):
    """Ensure Poetry is preferred when available and print mode is enabled."""
    fake_poetry = tmp_path / "poetry"
    fake_poetry.write_text("#!/usr/bin/env bash\nexit 0\n")
    fake_poetry.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env.get('PATH', '')}"
    env["BACKEND_START_MODE"] = "print"
    env["BACKEND_SKIP_INSTALL"] = "1"

    output = run_start_script(env)
    assert output.startswith("launcher=poetry")
    assert "host=" in output and "port=" in output


def test_start_backend_falls_back_to_venv(tmp_path):
    """Ensure fallback path is selected when Poetry is unavailable."""
    venv_dir = tmp_path / "custom-venv"

    env = os.environ.copy()
    env["BACKEND_START_MODE"] = "print"
    env["BACKEND_SKIP_INSTALL"] = "1"
    env["VENV_DIR"] = str(venv_dir)
    env["PYTHON"] = sys.executable
    env["PATH"] = f"{os.path.dirname(sys.executable)}:/bin:/usr/bin"
    env.pop("VIRTUAL_ENV", None)

    output = run_start_script(env)
    assert output.startswith("launcher=venv")
    assert f"path={venv_dir}" in output
    assert "host=" in output and "port=" in output
    assert venv_dir.exists()
