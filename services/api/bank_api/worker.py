"""Local durable deadline evaluation and notification delivery. No outbound calls."""

import argparse
import time
from datetime import datetime, timezone
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from .calendar import VERSION, add_hours
from .config import Settings
from .continuation import latest_plan, lead_review
from .db import runtime_connection
from .workflow import bump_case


def tick(settings, now):
    processed = 0
    with runtime_connection(settings.database_url) as conn:
        # Single transaction/repeatable-read retries: no partial deadline effects.
        rows = conn.execute("""SELECT w.*,c.status AS case_status,c.version AS case_version,c.timeline_sequence
         FROM work_items w JOIN cases c ON c.id=w.case_id WHERE c.closed_at IS NULL
         AND w.status NOT IN ('completed','cancelled') ORDER BY w.id""").fetchall()
        for w in rows:
            # Refresh case head after another item in this transaction advanced it.
            head = conn.execute(
                "SELECT status AS case_status,version AS case_version,timeline_sequence FROM cases WHERE id=%s",
                (w["case_id"],),
            ).fetchone()
            w.update(head)
            due = w["original_due_at"]
            kind = "overdue"
            if w["kind"] == "customer_feedback":
                if not conn.execute(
                    "SELECT 1 FROM contact_plans WHERE work_item_id=%s", (w["id"],)
                ).fetchone():
                    continue
                plan = latest_plan(conn, w)
                if plan["status"] == "active":
                    due = plan["valid_until"] or due
                elif w["status"] == "review_hold":
                    hold = conn.execute(
                        "SELECT review_at FROM lead_review_decisions WHERE work_item_id=%s AND kind='review_hold' ORDER BY decided_at DESC LIMIT 1",
                        (w["id"],),
                    ).fetchone()
                    due = hold["review_at"] if hold else None
                    kind = "hold_review"
                else:
                    continue
            if not due or now < due:
                continue
            eid = uuid4()
            created = conn.execute(
                "INSERT INTO due_events VALUES (%s,%s,%s,%s,%s) ON CONFLICT(work_item_id,due_at,kind) DO NOTHING RETURNING id",
                (eid, w["id"], due, kind, now),
            ).fetchone()
            if not created:
                continue
            if w["kind"] == "customer_feedback":
                lead_review(conn, w, plan, now)
            if w["kind"] in ("specialist_investigation", "specialist_rereview"):
                from .referrals import route_config

                route = route_config(conn)
                # The progress contact has its own one-service-day target. Inheriting the
                # missed deadline would escalate the same case/deadline a second time.
                progress_due = add_hours(now, 8)
                conn.execute(
                    "INSERT INTO work_items(id,case_id,kind,queue_id,status,original_due_at,due_at,calendar_ref,source_event_key,version,parent_work_id) VALUES (%s,%s,'progress_callback',%s,'queued',%s,%s,%s,%s,1,%s)",
                    (
                        uuid4(),
                        w["case_id"],
                        route["feedback_queue_id"],
                        progress_due,
                        progress_due,
                        VERSION,
                        "progress:" + str(eid),
                        w["id"],
                    ),
                )
            bump_case(
                conn,
                w,
                now,
                "work.overdue",
                "Original deadline missed; responsible queue lead notified. Recorded blocker reason may be unknown.",
            )
            processed += 1
        events = conn.execute(
            "SELECT id,payload FROM outbox_events WHERE status='pending' ORDER BY id LIMIT 100 FOR UPDATE SKIP LOCKED"
        ).fetchall()
        for e in events:
            conn.execute(
                "INSERT INTO local_notifications VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                (e["id"], now, Jsonb(e["payload"])),
            )
            conn.execute(
                "UPDATE outbox_events SET status='delivered_local',attempt_count=attempt_count+1 WHERE id=%s",
                (e["id"],),
            )
    return {"due_transitions": processed, "local_notifications": len(events)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    settings = Settings.from_env()
    while True:
        try:
            print(tick(settings, datetime.now(timezone.utc)), flush=True)
        except (psycopg.Error, RuntimeError):
            print("Worker dependency/conflict; retry without losing durable events.", flush=True)
            if args.once:
                raise
        if args.once:
            return
        time.sleep(30)


if __name__ == "__main__":
    main()
