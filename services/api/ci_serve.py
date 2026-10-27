"""Start API against explicitly supplied disposable CI PostgreSQL for browser tests."""

import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import uvicorn
from bank_api.app import create_app
from bank_api.config import Settings
from bank_api.db import migrate, provision_runtime
from bank_api.fixtures import reset, seed

admin = os.environ["BANK_TEST_ADMIN_URL"]
# Only this disposable browser-test server freezes time. The interactive demo and
# container retain the real clock and their normal service-window restrictions.
now = datetime.fromisoformat(
    json.loads((Path(__file__).parent / "tests/browser-clock.json").read_text())
)
parts = urlsplit(admin)
target = parts.path.lstrip("/")
migrate(admin)
seed(admin, target, initialize=True, now=now)
reset(admin, target)
seed(admin, target, now=now)
password = secrets.token_urlsafe(32)
provision_runtime(admin, password)
runtime = urlunsplit(
    parts._replace(netloc="bank_app:" + password + "@" + parts.netloc.split("@")[-1])
)
uvicorn.run(
    create_app(Settings(runtime), clock=lambda: now),
    host="127.0.0.1",
    # A spare port keeps local browser runs away from an already running demo.
    port=int(os.environ.get("BANK_DEMO_PORT", "8000")),
    access_log=False,
)
