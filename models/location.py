from supabase_db.db import fetch_one, fetch_all, insert_record, update_record, delete_record
from utils.helpers import generate_uuid, utc_now


# -----------------------------
# Table Names
# -----------------------------

STATES_TABLE = "states"
DISTRICTS_TABLE = "districts"
CONSTITUENCIES_TABLE = "constituencies"
BOOTHS_TABLE = "booths"


# -----------------------------
# States
# -----------------------------

def create_state(state_name: str, state_code: str):
    payload = {
        "id": generate_uuid(),
        "state_name": state_name,
        "state_code": state_code,
        "created_at": utc_now()
    }
    return insert_record(STATES_TABLE, payload, use_admin=True)


def get_state_by_id(state_id: str):
    return fetch_one(STATES_TABLE, {"id": state_id})


def get_state_by_code(state_code: str):
    return fetch_one(STATES_TABLE, {"state_code": state_code})


def get_all_states():
    return fetch_all(STATES_TABLE)


# -----------------------------
# Districts
# -----------------------------

def create_district(district_name: str, state_id: str):
    payload = {
        "id": generate_uuid(),
        "district_name": district_name,
        "state_id": state_id,
        "created_at": utc_now()
    }
    return insert_record(DISTRICTS_TABLE, payload, use_admin=True)


def get_district_by_id(district_id: str):
    return fetch_one(DISTRICTS_TABLE, {"id": district_id})


def get_districts_by_state(state_id: str):
    return fetch_all(DISTRICTS_TABLE, {"state_id": state_id})


# -----------------------------
# Constituencies
# -----------------------------

def create_constituency(constituency_name: str, district_id: str, constituency_type: str):
    payload = {
        "id": generate_uuid(),
        "constituency_name": constituency_name,
        "district_id": district_id,
        "constituency_type": constituency_type,
        "created_at": utc_now()
    }
    return insert_record(CONSTITUENCIES_TABLE, payload, use_admin=True)


def get_constituency_by_id(constituency_id: str):
    return fetch_one(CONSTITUENCIES_TABLE, {"id": constituency_id})


def get_constituencies_by_district(district_id: str):
    return fetch_all(CONSTITUENCIES_TABLE, {"district_id": district_id})


# -----------------------------
# Booths
# -----------------------------

def create_booth(booth_number: int, constituency_id: str, booth_name: str = None):
    payload = {
        "id": generate_uuid(),
        "booth_number": booth_number,
        "booth_name": booth_name,
        "constituency_id": constituency_id,
        "created_at": utc_now()
    }
    return insert_record(BOOTHS_TABLE, payload, use_admin=True)


def get_booth_by_id(booth_id: str):
    return fetch_one(BOOTHS_TABLE, {"id": booth_id})


def get_booths_by_constituency(constituency_id: str):
    return fetch_all(BOOTHS_TABLE, {"constituency_id": constituency_id})
