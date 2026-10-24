"""Run the research workbench independently of bank services and customer data."""

from pathlib import Path
from typing import Mapping

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .router import PROJECT, create_router, error_response


def create_app(
    sources: Mapping[str, Path] | None = None,
    static_dir: Path | None = None,
    passages: Mapping[str, Path] | None = None,
    provider=None,
) -> FastAPI:
    app = FastAPI(title="Investment Research Brief", version="0.1.0")

    @app.get("/health/live")
    def health():
        return {"status": "alive"}

    app.include_router(create_router(sources, passages, provider))

    @app.api_route("/v1/{unsupported:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def unsupported_api(unsupported: str):
        return error_response("NOT_FOUND", "This research endpoint is not available.", 404)

    assets = PROJECT / "web/dist" if static_dir is None else static_dir
    if assets.is_dir():
        app.mount("/", StaticFiles(directory=assets, html=True), name="research-workbench")
    return app
