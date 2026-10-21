"""Start API against explicitly supplied disposable CI PostgreSQL for browser tests."""

import os
import secrets
from urllib.parse import urlsplit, urlunsplit

import uvicorn
from bank_api.app import create_app
from bank_api.config import Settings
from bank_api.db import migrate, provision_runtime
from bank_api.fixtures import reset, seed

admin = os.environ["BANK_TEST_ADMIN_URL"]
parts = urlsplit(admin)
target = parts.path.lstrip("/")
migrate(admin)
seed(admin, target, initialize=True)
reset(admin, target)
seed(admin, target)
password = secrets.token_urlsafe(32)
provision_runtime(admin, password)
runtime = urlunsplit(
    parts._replace(netloc="bank_app:" + password + "@" + parts.netloc.split("@")[-1])
)
uvicorn.run(create_app(Settings(runtime)), host="127.0.0.1", port=8000, access_log=False)
