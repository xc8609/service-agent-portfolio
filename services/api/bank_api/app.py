"""Scoped synthetic lookup and trusted human investigation commands."""

import base64
import hashlib
import json
import secrets
from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

import psycopg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from jsonschema import Draft202012Validator, FormatChecker
from psycopg.types.json import Jsonb
from starlette.concurrency import run_in_threadpool
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .case_lookup import dispatch_cases
from .config import Settings
from .db import ROOT, SCHEMA_VERSION, runtime_connection
from .fixtures import FIXTURE_VERSION, PERSONAS, uid
from .investigation import dispatch_investigation
from .policy_lookup import dispatch_policy
from .proposals import dispatch_proposals
from .workflow import SCHEMAS as WORKFLOW_SCHEMAS
from .workflow import dispatch_workflow

CONTRACTS = json.loads(
    (ROOT / "projects/bank-service-assist/specs/contracts/agent-tools.json").read_text()
)
TOOLS = {t["name"]: t for t in CONTRACTS["tools"]}
READ_TOOLS = ("get_contact_context", "search_transactions", "get_transaction_evidence")
MESSAGES = {
    "CONTACT_GAP": (
        "Customer-service contact resolution is still outstanding. Investigation deadlines remain unchanged.",
        409,
    ),
    "DUPLICATE_REVIEW_REQUIRED": (
        "Related active work exists. Link it or review a distinct-work reason before submitting.",
        409,
    ),
    "IDEMPOTENCY_CONFLICT": (
        "This operation key already belongs to different reviewed content. Reload its receipt; do not overwrite it.",
        409,
    ),
    "UNSUPPORTED_CLAIM": (
        "Unsupported financial completion claim: attribute customer reports separately; no execution evidence exists.",
        422,
    ),
    "EVIDENCE_CHANGED": (
        "Selected transaction evidence changed. Inspect the pair again before using a handling rule.",
        409,
    ),
    "POLICY_CONFLICT": (
        "Applicable handling rules conflict. Request service-lead and policy-owner clarification; no instruction selected.",
        409,
    ),
    "STALE_VERSION": (
        "Recorded case state conflicts with its timeline. Refresh or request manual reconciliation; do not create another enquiry from this view.",
        409,
    ),
    "LIMIT_EXCEEDED": (
        "Too much related history to safely display. Narrow the selection or use manual case review.",
        422,
    ),
    "CONFLICT": (
        "Investigation or source evidence changed. Reload history and recheck selected evidence before saving.",
        409,
    ),
    "AUTH_REQUIRED": ("Fresh session and customer verification are required.", 401),
    "FORBIDDEN_OR_NOT_FOUND": (
        "Requested information is not available in this scope.",
        404,
    ),
    "VALIDATION_ERROR": ("Check the request fields and permitted limits.", 422),
    "DEPENDENCY_UNAVAILABLE": (
        "Service unavailable. Continue with the manual support route.",
        503,
    ),
    "TIMEOUT": ("Source lookup timed out. No result has been inferred.", 503),
}


class BankError(Exception):
    def __init__(self, code):
        self.code = code


def fail(code):
    raise BankError(code)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def validate(schema, payload):
    if not Draft202012Validator(schema, format_checker=FormatChecker()).is_valid(payload):
        fail("VALIDATION_ERROR")


def as_uuid(value):
    try:
        return str(UUID(value))
    except (ValueError, TypeError, AttributeError):
        fail("FORBIDDEN_OR_NOT_FOUND")


def source(kind, ident, version, section=None):
    return {"kind": kind, "id": str(ident), "version": str(version), "section": section}


def projection(row):
    return {
        key: (
            str(row[key])
            if key in ("id", "version")
            else row[key].isoformat()
            if isinstance(row[key], datetime)
            else row[key]
        )
        for key in (
            "id",
            "version",
            "amount_minor",
            "currency",
            "merchant_description",
            "status",
            "occurred_at",
            "posted_at",
        )
    }


def authenticate(conn, authorization, now):
    if not authorization.startswith("Bearer ") or len(authorization) > 512:
        fail("AUTH_REQUIRED")
    session = conn.execute(
        """SELECT s.*, p.active FROM demo_sessions s
        JOIN staff_principals p ON p.id=s.principal_id WHERE token_hash=%s""",
        (digest(authorization[7:]),),
    ).fetchone()
    if not session or not session["active"] or session["expires_at"] <= now:
        fail("AUTH_REQUIRED")
    return session


def scope(conn, session, contact_id, now):
    contact_id = as_uuid(contact_id)
    if contact_id != str(session["contact_id"]):
        fail("FORBIDDEN_OR_NOT_FOUND")
    # No request-supplied role or claimed identity is trusted.
    role = conn.execute(
        """SELECT 1 FROM queue_memberships m JOIN service_queues q ON q.id=m.queue_id
        WHERE m.principal_id=%s AND m.active AND q.active AND m.role='inbound_representative' """,
        (session["principal_id"],),
    ).fetchone()
    if not role:
        fail("FORBIDDEN_OR_NOT_FOUND")
    contact = conn.execute(
        """SELECT * FROM contacts WHERE id=%s AND actor_id=%s
        AND status='open' AND kind='inbound' """,
        (contact_id, session["principal_id"]),
    ).fetchone()
    if not contact:
        fail("FORBIDDEN_OR_NOT_FOUND")
    proof = conn.execute(
        """SELECT * FROM verification_assertions WHERE contact_id=%s
        ORDER BY verified_at DESC NULLS LAST, id DESC LIMIT 1""",
        (contact_id,),
    ).fetchone()
    if (
        not proof
        or proof["issuer_ref"] != "local_synthetic_adapter"
        or proof["state"] != "verified"
        or not proof["verified_at"]
        or proof["verified_at"] > now
        or not proof["expires_at"]
        or proof["expires_at"] <= now
    ):
        fail("AUTH_REQUIRED")
    ids = proof["scope_json"].get("account_ids", [])
    # UUIDs originate in the trusted assertion, never a model/user payload.
    cards = conn.execute(
        "SELECT * FROM card_accounts WHERE customer_id=%s AND id=ANY(%s::uuid[])",
        (contact["customer_id"], ids),
    ).fetchall()
    if not cards:
        fail("FORBIDDEN_OR_NOT_FOUND")
    return contact, cards


def search(conn, payload, contact, cards):
    card = next((c for c in cards if c["masked_ref"] == payload["card_ref"]), None)
    if not card:
        fail("FORBIDDEN_OR_NOT_FOUND")
    start, end = (
        date.fromisoformat(payload["date_from"]),
        date.fromisoformat(payload["date_to"]),
    )
    if end < start or (end - start).days > 366 or end == date.max:
        fail("VALIDATION_ERROR")
    if payload["amount_minor"] is not None and abs(payload["amount_minor"]) > 9223372036854775807:
        fail("VALIDATION_ERROR")
    merchant = payload["merchant_query"]
    if merchant is not None and len(merchant) > 120:
        fail("VALIDATION_ERROR")
    binding = digest(
        json.dumps(
            {k: v for k, v in payload.items() if k not in ("cursor", "limit")},
            sort_keys=True,
        )
    )
    cursor_date = datetime.min.replace(tzinfo=UTC)
    cursor_id = UUID(int=0)
    if payload["cursor"]:
        try:
            if len(payload["cursor"]) > 1024:
                raise ValueError()
            cursor = json.loads(base64.urlsafe_b64decode(payload["cursor"]))
            if set(cursor) != {"binding", "at", "id"} or cursor["binding"] != binding:
                raise ValueError()
            cursor_date = datetime.fromisoformat(cursor["at"])
            cursor_id = UUID(cursor["id"])
            if cursor_date.tzinfo is None:
                raise ValueError()
        except (ValueError, TypeError, KeyError):
            fail("VALIDATION_ERROR")
    rows = conn.execute(
        """SELECT * FROM card_transactions WHERE account_id=%s
        AND occurred_at >= %s AND occurred_at < %s
        AND (%s::bigint IS NULL OR amount_minor=%s)
        AND (%s::text IS NULL OR strpos(lower(merchant_description),lower(%s))>0)
        AND (occurred_at,id)>(%s,%s) ORDER BY occurred_at,id LIMIT %s""",
        (
            card["id"],
            datetime.combine(start, datetime.min.time(), UTC),
            datetime.combine(end + timedelta(days=1), datetime.min.time(), UTC),
            payload["amount_minor"],
            payload["amount_minor"],
            merchant,
            merchant,
            cursor_date,
            cursor_id,
            payload["limit"] + 1,
        ),
    ).fetchall()
    records = rows[: payload["limit"]]
    next_cursor = None
    if len(rows) > payload["limit"]:
        last = records[-1]
        next_cursor = base64.urlsafe_b64encode(
            json.dumps(
                {
                    "binding": binding,
                    "at": last["occurred_at"].isoformat(),
                    "id": str(last["id"]),
                }
            ).encode()
        ).decode()
    return (
        {"records": [projection(r) for r in records], "next_cursor": next_cursor},
        records,
        [],
    )


def evidence(conn, payload, contact, cards):
    ids = [as_uuid(i) for i in payload["transaction_ids"]]
    rows = conn.execute(
        """SELECT * FROM card_transactions WHERE account_id=ANY(%s::uuid[])
        AND id=ANY(%s::uuid[]) ORDER BY occurred_at,id""",
        ([c["id"] for c in cards], ids),
    ).fetchall()
    if len(rows) != len(ids):
        fail("FORBIDDEN_OR_NOT_FOUND")
    relations = conn.execute(
        """SELECT * FROM transaction_relationships
        WHERE left_transaction_id=ANY(%s::uuid[]) AND right_transaction_id=ANY(%s::uuid[])""",
        (ids, ids),
    ).fetchall()
    by_id = {str(r["id"]): r for r in rows}
    links = [
        {
            "left_id": str(r["left_transaction_id"]),
            "right_id": str(r["right_transaction_id"]),
            "relation": r["relation"],
            "evidence_ref": source(
                "transaction",
                r["left_transaction_id"],
                by_id[str(r["left_transaction_id"])]["version"],
                r["evidence_ref"],
            ),
        }
        for r in relations
    ]
    cases = conn.execute(
        """SELECT DISTINCT c.id,c.version FROM cases c JOIN case_transactions ct ON ct.case_id=c.id
        WHERE c.customer_id=%s AND ct.transaction_id=ANY(%s::uuid[])""",
        (contact["customer_id"], ids),
    ).fetchall()
    missing = []
    if len(rows) > 1 and not links:
        missing.append(
            "No source relationship is recorded; equal amounts or merchant names do not establish a duplicate."
        )
    if any(r["status"] == "pending" for r in rows):
        missing.append("Pending status is not a refund or automatic reversal commitment.")
    if any(r["merchant_description"] == "Merchant unavailable" for r in rows):
        missing.append("Merchant context unavailable; specialist verification may be needed.")
    return (
        {
            "records": [projection(r) for r in rows],
            "relationships": links,
            "related_case_ids": [str(c["id"]) for c in cases],
            "missing_evidence": missing,
        },
        rows,
        cases,
    )


def audit(conn, actor, action, outcome, request_id, now):
    conn.execute(
        """INSERT INTO audit_events
        (id,actor_ref,event_type,occurred_at,safe_details,aggregate_sequence)
        VALUES (%s,%s,%s,%s,%s,0)""",
        (
            uuid4(),
            str(actor) if actor else "unauthenticated",
            "lookup." + action,
            now,
            Jsonb({"outcome": outcome, "request_id": request_id}),
        ),
    )


def dispatch(settings, name, payload, authorization, request_id, now):
    error = None
    result = None
    actor = None
    try:
        with runtime_connection(settings.database_url) as conn:
            # A consistent snapshot binds proof and returned records for this request.
            try:
                session = authenticate(conn, authorization, now)
                actor = session["principal_id"]
                validate(TOOLS[name]["input_schema"], payload)
                contact, cards = scope(conn, session, payload["contact_id"], now)
                if name == "get_contact_context":
                    data = {
                        "contact_id": str(contact["id"]),
                        "context_version": str(contact["version"]),
                        "verification": "verified",
                        "masked_card_refs": [c["masked_ref"] for c in cards],
                        "allowed_actions": [
                            "customer.read_context",
                            "transaction.read",
                            "result.read_approved",
                            "policy.read",
                        ],
                        "access_purpose": "inbound_service",
                        "assigned_work_ref": None,
                        "customer_disclosure_allowed": True,
                    }
                    rows = []
                    cases = []
                elif name == "search_transactions":
                    data, rows, cases = search(conn, payload, contact, cards)
                else:
                    data, rows, cases = evidence(conn, payload, contact, cards)
                result = {
                    "data": data,
                    "meta": {
                        "as_of": now.isoformat(),
                        "scope_ref": str(contact["id"]),
                        "sources": [source("contact", contact["id"], contact["version"])]
                        + [
                            source("transaction", r["id"], r["version"], r["source_ref"])
                            for r in rows
                        ]
                        + [source("case", r["id"], r["version"]) for r in cases],
                    },
                }
                # Contract drift is an internal failure, never echo rejected values.
                if not Draft202012Validator(
                    TOOLS[name]["success_schema"], format_checker=FormatChecker()
                ).is_valid(result):
                    fail("DEPENDENCY_UNAVAILABLE")
            except BankError as exc:
                error = exc
            audit(conn, actor, name, error.code if error else "allowed", request_id, now)
    except psycopg.errors.QueryCanceled:
        fail("TIMEOUT")
    except (psycopg.Error, RuntimeError):
        fail("DEPENDENCY_UNAVAILABLE")
    if error:
        raise error
    return result


def create_app(settings=None, clock=None):
    settings = settings or Settings.from_env()
    now = clock or (lambda: datetime.now(UTC))
    app = FastAPI(
        title="Synthetic bank service — authorized lookup",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "testserver", "api"],
    )

    @app.middleware("http")
    async def boundaries(request: Request, call_next):
        request.state.request_id = str(uuid4())
        origin = request.headers.get("origin")
        allowed = {
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        }
        if origin and origin not in allowed:
            response = error_response("FORBIDDEN_OR_NOT_FOUND", request.state.request_id)
        else:
            response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'"
        )
        return response

    @app.exception_handler(BankError)
    async def bank_error(request, exc):
        return error_response(exc.code, request.state.request_id)

    @app.exception_handler(psycopg.Error)
    @app.exception_handler(RuntimeError)
    async def db_error(request, exc):
        return error_response("DEPENDENCY_UNAVAILABLE", request.state.request_id)

    async def body(request):
        raw = await request.body()
        if len(raw) > 32768:
            fail("VALIDATION_ERROR")
        try:
            return json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            fail("VALIDATION_ERROR")

    @app.get("/health/live")
    def live():
        return {"status": "alive", "data_kind": "synthetic", "agent_enabled": False}

    @app.get("/health/ready")
    def ready():
        try:
            with runtime_connection(settings.database_url) as conn:
                version = conn.execute(
                    "SELECT name FROM schema_migrations ORDER BY name DESC LIMIT 1"
                ).fetchone()
                marker = conn.execute(
                    "SELECT marker FROM demo_environment WHERE singleton"
                ).fetchone()
                if not version or version["name"] != SCHEMA_VERSION or not marker:
                    fail("DEPENDENCY_UNAVAILABLE")
        except (psycopg.Error, RuntimeError):
            fail("DEPENDENCY_UNAVAILABLE")
        return {
            "status": "ready",
            "data_kind": "synthetic",
            "schema_version": SCHEMA_VERSION,
            "fixture_version": FIXTURE_VERSION,
            "agent_enabled": False,
            "offline_assistant_available": True,
        }

    @app.post("/v1/demo/session")
    async def demo_session(request: Request):
        payload = await body(request)
        if (
            not isinstance(payload, dict)
            or set(payload) != {"persona"}
            or not isinstance(payload["persona"], str)
            or payload["persona"] not in PERSONAS
        ):
            fail("VALIDATION_ERROR")

        def issue():
            actor, contact, _, _ = PERSONAS[payload["persona"]]
            token = secrets.token_urlsafe(32)
            with runtime_connection(settings.database_url) as conn:
                if not conn.execute("SELECT 1 FROM demo_environment WHERE singleton").fetchone():
                    fail("DEPENDENCY_UNAVAILABLE")
                conn.execute(
                    "INSERT INTO demo_sessions VALUES (%s,%s,%s,%s)",
                    (
                        digest(token),
                        uid(actor),
                        uid(contact),
                        now() + timedelta(minutes=15),
                    ),
                )
            return {
                "access_token": token,
                "contact_id": uid(contact),
                "data_kind": "synthetic",
                "identity_adapter": "local_demo_only",
                "expires_in_seconds": 900,
            }

        return await run_in_threadpool(issue)

    def endpoint(name, handler=dispatch):
        async def call(request: Request):
            payload = await body(request)
            return await run_in_threadpool(
                handler,
                settings,
                name,
                payload,
                request.headers.get("authorization", ""),
                request.state.request_id,
                now(),
            )

        return call

    for name in READ_TOOLS:
        app.add_api_route(TOOLS[name]["http"]["path"], endpoint(name), methods=["POST"], name=name)

    for name in ("get_investigation", "save_investigation"):
        app.add_api_route(
            "/v1/workspace/" + name,
            endpoint(name, dispatch_investigation),
            methods=["POST"],
            name=name,
        )

    app.add_api_route(
        TOOLS["get_case_snapshot"]["http"]["path"],
        endpoint("get_case_snapshot", dispatch_cases),
        methods=["POST"],
    )
    app.add_api_route(
        "/v1/workspace/get_related_cases",
        endpoint("get_related_cases", dispatch_cases),
        methods=["POST"],
    )

    for name in ("search_policy", "get_policy_section", "get_handling_rules"):
        app.add_api_route(
            "/v1/workspace/get_handling_rules"
            if name == "get_handling_rules"
            else TOOLS[name]["http"]["path"],
            endpoint(name, dispatch_policy),
            methods=["POST"],
            name=name,
        )

    for name in (
        "create_proposal",
        "get_operation_status",
        "edit_proposal",
        "approve_and_commit_proposal",
        "reject_proposal",
        "get_proposals",
        "prepare_note",
        "prepare_referral",
        "get_referrals",
    ):
        prefix = (
            "agent-tools"
            if name in ("create_proposal", "get_operation_status")
            else "workspace"
            if name in ("get_proposals", "prepare_note", "prepare_referral", "get_referrals")
            else "commands"
        )
        app.add_api_route(
            "/v1/" + prefix + "/" + name,
            endpoint(name, dispatch_proposals),
            methods=["POST"],
            name=name,
        )

    for name in (
        *WORKFLOW_SCHEMAS,
        "accept_specialist_work",
        "claim_feedback_task",
        "record_specialist_result",
        "record_callback_attempt",
        "decide_contact_continuation",
        "propose_next_update",
        "confirm_next_update",
        "capture_customer_objection",
        "register_complaint_intake",
    ):
        prefix = "workspace" if name in WORKFLOW_SCHEMAS else "commands"
        if name == "demo_callback_verification":
            path = "/v1/demo/callback-verification"
        else:
            path = "/v1/" + prefix + "/" + name
        app.add_api_route(path, endpoint(name, dispatch_workflow), methods=["POST"], name=name)

    from .agent.runtime import control as agent_control
    from .agent.runtime import run as agent_run

    def agent_dispatch(settings, name, payload, authorization, request_id, at):
        try:
            return (
                agent_run(settings, payload, authorization, request_id, at)
                if name == "run"
                else agent_control(settings, name, payload, authorization, request_id, at)
            )
        except (psycopg.errors.UniqueViolation, psycopg.errors.SerializationFailure):
            fail("CONFLICT")
        except (psycopg.Error, RuntimeError):
            fail("DEPENDENCY_UNAVAILABLE")

    for action in ("run", "get_run", "cancel_run"):
        app.add_api_route(
            "/v1/assistant/" + action,
            endpoint(action, agent_dispatch),
            methods=["POST"],
            name="assistant_" + action,
        )

    @app.api_route("/v1/{unsupported:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def unsupported_api(unsupported: str):
        # Keep missing/privileged APIs uniform even when the static UI is mounted.
        fail("FORBIDDEN_OR_NOT_FOUND")

    static = ROOT / "apps/web/dist"
    if static.is_dir():
        app.mount("/", StaticFiles(directory=static, html=True), name="workspace")
    return app


def error_response(code, request_id):
    message, status = MESSAGES[code]
    return JSONResponse(
        status_code=status,
        content={
            "error": {
                "code": code,
                "safe_message": message,
                "retryable": status == 503,
                "operation_key": None,
            },
            "request_id": request_id,
        },
    )
