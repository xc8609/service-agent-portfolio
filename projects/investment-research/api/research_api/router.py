"""Read registered public source packs through the shared comparison contract."""

import json
from pathlib import Path
from typing import Mapping

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from research_brief import ComparisonError, compare

PROJECT = Path(__file__).resolve().parents[2]
REGISTERED_SOURCES = {"msft-ar2025": PROJECT / "examples/msft-fy2025.json"}


class SourceUnavailable(Exception):
    """A registered source cannot currently provide a valid comparison."""


def error_response(code: str, message: str, status: int) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "safe_message": message}},
    )


def _read_comparison(source_id: str, path: Path) -> dict:
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
        result = compare(packet)
        if result["source"]["id"] != source_id:
            raise ComparisonError("Registered source identity does not match the pack")
        return result
    except (OSError, UnicodeError, ValueError, ArithmeticError) as exc:
        raise SourceUnavailable from exc


def create_router(sources: Mapping[str, Path] | None = None) -> APIRouter:
    # The registry is supplied by the application, never by a request path or URL.
    registry = dict(REGISTERED_SOURCES if sources is None else sources)
    router = APIRouter(prefix="/v1/research")

    def unavailable() -> JSONResponse:
        return error_response(
            "SOURCE_UNAVAILABLE",
            "The selected report data could not be loaded. Retry or keep working in your notes.",
            503,
        )

    @router.get("/sources")
    def list_sources():
        available = []
        try:
            for source_id, path in registry.items():
                result = _read_comparison(source_id, path)
                source = result["source"]
                available.append(
                    {
                        "id": source_id,
                        "issuer": result["issuer"],
                        "title": source["title"],
                        "url": source["url"],
                        "periods": result["periods"],
                    }
                )
        except SourceUnavailable:
            return unavailable()
        return {"sources": available}

    @router.get("/sources/{source_id}/comparison")
    def get_comparison(source_id: str):
        if source_id not in registry:
            return error_response("SOURCE_NOT_FOUND", "This report is not available.", 404)
        try:
            return _read_comparison(source_id, registry[source_id])
        except SourceUnavailable:
            return unavailable()

    return router
