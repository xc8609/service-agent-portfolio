"""Additional synthetic operating roles, separate from inbound scope."""


def seed_workflow_roles(conn):
    from .fixtures import insert, uid

    conn.execute("UPDATE service_routes SET complaint_queue_id=%s", (uid("complaint_queue"),))
    for actor, queue, role in [
        ("Demo specialist Alex", "specialist_queue", "specialist"),
        ("feedback", "feedback_queue", "feedback_representative"),
        ("feedback_other", "feedback_queue", "feedback_representative"),
        ("lead", "specialist_queue", "queue_lead"),
        ("lead", "feedback_queue", "queue_lead"),
    ]:
        insert(
            conn,
            "queue_memberships",
            {
                "id": uid(actor + "-" + queue + "-" + role),
                "principal_id": uid(actor),
                "queue_id": uid(queue),
                "role": role,
                "active": True,
            },
        )
