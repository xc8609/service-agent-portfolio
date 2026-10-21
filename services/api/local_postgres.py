"""Optional Mac/Linux development runner; not a production dependency.
Run from root: .venv-app/bin/python services/api/local_postgres.py test|serve
"""

import os
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlencode, urlsplit, urlunsplit

import pgserver
import psycopg
from bank_api.db import migrate, provision_runtime
from bank_api.fixtures import seed
from psycopg.conninfo import conninfo_to_dict

ROOT = Path(__file__).resolve().parents[2]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    if mode not in ("test", "serve"):
        raise SystemExit("Choose test or serve")
    data = Path(tempfile.mkdtemp(prefix="bank-demo-pg-"))
    pg = pgserver.get_server(data, cleanup_mode="stop")
    try:
        base = pg.get_uri()
        with psycopg.connect(base, autocommit=True) as conn:
            conn.execute("CREATE DATABASE bank_demo_test")
        parts = urlsplit(base)
        admin = urlunsplit(parts._replace(path="/bank_demo_test"))
        env = {
            **os.environ,
            "BANK_TEST_ADMIN_URL": admin,
            "PYTHONPATH": str(ROOT / "services/api"),
        }
        with psycopg.connect(admin) as conn:
            print(
                "Actual PostgreSQL:",
                conn.execute("SELECT version()").fetchone()[0],
                flush=True,
            )
        if mode == "test":
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-c",
                    "services/api/pytest.ini",
                    "services/api/tests",
                    "-q",
                ],
                cwd=ROOT,
                env=env,
            )
            raise SystemExit(result.returncode)
        migrate(admin)
        seed(admin, "bank_demo_test", initialize=True)
        password = secrets.token_urlsafe(32)
        provision_runtime(admin, password)
        opts = conninfo_to_dict(admin)
        runtime = (
            "postgresql://bank_app:"
            + password
            + "@/bank_demo_test?"
            + urlencode({"host": opts["host"]})
        )
        print(
            "Synthetic demo: http://127.0.0.1:8000 — Ctrl+C stops disposable PostgreSQL.",
            flush=True,
        )
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "bank_api.app:create_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--no-access-log",
            ],
            cwd=ROOT,
            env={**env, "BANK_DATABASE_URL": runtime},
        )
    finally:
        pg.cleanup()


if __name__ == "__main__":
    main()
