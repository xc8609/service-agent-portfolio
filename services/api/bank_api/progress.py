"""Manual progress calls separate from the final-result attempt quota (D-26)."""

from uuid import uuid4

from psycopg.types.json import Jsonb

from .workflow import bump_case, callback_context, proof


def execute(conn, name, p, w, actor, operation, request_id, now):
    from .app import fail

    if w["kind"] != "progress_callback" or w["status"] != "assigned":
        fail("CONFLICT")
    parent = conn.execute(
        "SELECT status FROM work_items WHERE id=%s", (w["parent_work_id"],)
    ).fetchone()
    if not parent or parent["status"] in ("completed", "cancelled"):
        fail("CONFLICT")
    if name == "open_progress_contact":
        cid = uuid4()
        conn.execute(
            "INSERT INTO contacts(id,customer_id,actor_id,kind,status,opened_at,version) VALUES (%s,%s,%s,'callback','open',%s,1)",
            (cid, w["customer_id"], actor, now),
        )
        conn.execute("INSERT INTO callback_contexts VALUES (%s,%s,NULL)", (cid, w["id"]))
        conn.execute(
            "INSERT INTO verification_assertions VALUES (%s,%s,'local_synthetic_callback_adapter','unverified',%s,%s,%s)",
            (uuid4(), cid, now, now, Jsonb({"case_id": str(w["case_id"])})),
        )
        return {
            "contact_id": str(cid),
            "notice": "Manual progress context; no call placed and no final-result quota started.",
        }
    c = callback_context(conn, actor, p["callback_contact_id"], w)
    proof(conn, c, now)
    commitment = conn.execute(
        "SELECT * FROM update_commitments WHERE work_item_id=%s AND status='approved' ORDER BY decided_at DESC LIMIT 1",
        (w["parent_work_id"],),
    ).fetchone()
    message = "Investigation remains open. The blocker reason is not confirmed and no next-update time is approved."
    if commitment and commitment["proposed_update_at"] > now:
        message = (
            commitment["customer_safe_progress"]
            + " Next update: "
            + commitment["proposed_update_at"].isoformat()
        )
    if name == "get_progress_disclosure":
        return {
            "explanation": message,
            "commitment_id": str(commitment["id"]) if commitment else None,
        }
    if name == "record_progress_contact":
        current = str(commitment["id"]) if commitment else None
        if p["commitment_id"] != current or not p["reviewed"]:
            fail("CONFLICT")
        conn.execute(
            "INSERT INTO progress_contacts VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (
                uuid4(),
                w["id"],
                c["id"],
                commitment["id"] if commitment else None,
                actor,
                now,
                operation[0],
            ),
        )
        conn.execute(
            "UPDATE work_items SET status='completed',version=version+1 WHERE id=%s", (w["id"],)
        )
        bump_case(
            conn,
            w,
            now,
            "progress.delivered",
            "Verified manual progress contact recorded; investigation remains open.",
        )
        return {"status": "recorded", "notice": "Progress delivered, not investigation resolution."}
    fail("VALIDATION_ERROR")
