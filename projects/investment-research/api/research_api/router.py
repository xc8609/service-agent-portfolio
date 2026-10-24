"""Read registered public source packs through the shared comparison contract."""

import json
from pathlib import Path
from typing import Mapping

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from research_brief import ComparisonError, compare
from research_brief.agent import run_research

PROJECT = Path(__file__).resolve().parents[2]
REGISTERED_SOURCES = {"msft-ar2025": PROJECT / "examples/msft-fy2025.json"}
REGISTERED_PASSAGES = {"msft-ar2025": PROJECT / "examples/msft-fy2025-passages.json"}


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    question: str = Field(min_length=1, max_length=1000)
    expected_source_hash: str = Field(pattern=r"^[a-fA-F0-9]{64}$")


class SourceUnavailable(Exception):
    """A registered source cannot currently provide a valid comparison."""


def error_response(code: str, message: str, status: int) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "safe_message": message}},
    )


def _read_source(source_id: str, path: Path) -> tuple[dict, dict]:
    try:
        packet = json.loads(path.read_text(encoding="utf-8"))
        result = compare(packet)
        if result["source"]["id"] != source_id:
            raise ComparisonError("Registered source identity does not match the pack")
        return packet, result
    except (OSError, UnicodeError, ValueError, ArithmeticError) as exc:
        raise SourceUnavailable from exc


def _read_comparison(source_id: str, path: Path) -> dict:
    return _read_source(source_id, path)[1]


def create_router(
    sources: Mapping[str, Path] | None = None,
    passages: Mapping[str, Path] | None = None,
    provider=None,
) -> APIRouter:
    # The registry is supplied by the application, never by a request path or URL.
    registry = dict(REGISTERED_SOURCES if sources is None else sources)
    passage_registry = dict(REGISTERED_PASSAGES if passages is None else passages)
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

    @router.post("/runs")
    def run_draft(request: RunRequest):
        if request.source_id not in registry:
            return error_response("SOURCE_NOT_FOUND", "This report is not available.", 404)
        try:
            packet, comparison = _read_source(request.source_id, registry[request.source_id])
            if comparison["source"]["sha256"].lower() != request.expected_source_hash.lower():
                return error_response(
                    "SOURCE_CHANGED",
                    "The report changed. Reload the comparison before drafting.",
                    409,
                )
            passage_path = passage_registry.get(request.source_id)
            passage_pack = (
                json.loads(passage_path.read_text(encoding="utf-8")) if passage_path else None
            )
        except (SourceUnavailable, OSError, UnicodeError, ValueError):
            return unavailable()
        # Provider and tool permissions are application-owned, never request fields.
        # Each run reads one local snapshot; no source downloads or financial writes.
        return run_research(packet, passage_pack, request.question, provider=provider)

    return router
