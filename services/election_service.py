from models.election import (
    create_election,
    approve_election,
    add_constituency_to_election,
    get_election_by_id
)
from models.location import get_constituency_by_id
from models.audit import create_audit_log


# -----------------------------
# Election Service
# -----------------------------

def create_state_election(
    election_name: str,
    election_type: str,
    state_id: str,
    start_time,
    end_time,
    nomination_deadline,
    draft_roll_publish_at,
    final_roll_publish_at,
    created_by: str
):
    election = create_election(
        election_name=election_name,
        election_type=election_type,
        state_id=state_id,
        start_time=start_time,
        end_time=end_time,
        nomination_deadline=nomination_deadline,
        draft_roll_publish_at=draft_roll_publish_at,
        final_roll_publish_at=final_roll_publish_at,
        created_by=created_by
    )


    create_audit_log(
        user_id=created_by,
        action="CREATE_ELECTION",
        entity_type="ELECTION",
        entity_id=election[0]["id"]
    )

    return election


def approve_state_election(election_id: str, approved_by: str):
    election = get_election_by_id(election_id)
    if not election:
        raise ValueError("Election not found")

    approve_election(election_id, approved_by)

    create_audit_log(
        user_id=approved_by,
        action="APPROVE_ELECTION",
        entity_type="ELECTION",
        entity_id=election_id
    )


def assign_constituency_to_election(election_id: str, constituency_id: str):
    constituency = get_constituency_by_id(constituency_id)
    if not constituency:
        raise ValueError("Invalid constituency")

    return add_constituency_to_election(election_id, constituency_id)
