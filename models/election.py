from supabase_db.db import fetch_one, fetch_all, insert_record, update_record
from utils.helpers import generate_uuid, utc_now


# -----------------------------
# Table Names
# -----------------------------

ELECTIONS_TABLE = "elections"
ELECTION_CONSTITUENCIES_TABLE = "election_constituencies"


# -----------------------------
# Elections
# -----------------------------

def create_election(
    election_name: str,
    election_type: str,
    state_id: str,
    start_time,
    end_time,
    created_by: str
):
    payload = {
        "id": generate_uuid(),
        "election_name": election_name,
        "election_type": election_type,
        "state_id": state_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": "Draft",
        "created_by": created_by,
        "approved_by": None,
        "created_at": utc_now()
    }
    return insert_record(ELECTIONS_TABLE, payload, use_admin=True)


def get_election_by_id(election_id: str):
    return fetch_one(ELECTIONS_TABLE, {"id": election_id})


def get_elections_by_state(state_id: str):
    return fetch_all(ELECTIONS_TABLE, {"state_id": state_id})


def get_all_elections():
    return fetch_all(ELECTIONS_TABLE)


def update_election_status(election_id: str, status: str):
    return update_record(
        ELECTIONS_TABLE,
        {"id": election_id},
        {"status": status},
        use_admin=True
    )


def approve_election(election_id: str, approved_by: str):
    return update_record(
        ELECTIONS_TABLE,
        {"id": election_id},
        {
            "status": "Approved",
            "approved_by": approved_by
        },
        use_admin=True
    )


# -----------------------------
# Election Constituencies
# -----------------------------

def add_constituency_to_election(election_id: str, constituency_id: str):
    payload = {
        "id": generate_uuid(),
        "election_id": election_id,
        "constituency_id": constituency_id
    }
    return insert_record(ELECTION_CONSTITUENCIES_TABLE, payload, use_admin=True)


def get_constituencies_for_election(election_id: str):
    return fetch_all(ELECTION_CONSTITUENCIES_TABLE, {"election_id": election_id})


def is_constituency_in_election(election_id: str, constituency_id: str) -> bool:
    record = fetch_one(
        ELECTION_CONSTITUENCIES_TABLE,
        {
            "election_id": election_id,
            "constituency_id": constituency_id
        }
    )
    return record is not None
