from supabase_db.db import fetch_one, fetch_all, insert_record, update_record
from utils.helpers import generate_uuid, utc_now
from utils.helpers import normalize_role


# -----------------------------
# Table Names
# -----------------------------

USERS_TABLE = "users"
CITIZEN_ALIAS_TABLE = "citizen_alias"


# -----------------------------
# Users
# -----------------------------

def create_user(
    email: str,
    password_hash: str,
    role: str,
    state_id: str = None,
    district_id: str = None,
    constituency_id: str = None,
    booth_id: str = None
):
    payload = {
        "id": generate_uuid(),
        "email": email,
        "password_hash": password_hash,
        "role": normalize_role(role),
        "state_id": state_id,
        "district_id": district_id,
        "constituency_id": constituency_id,
        "booth_id": booth_id,
        "is_active": True,
        "created_at": utc_now()
    }
    return insert_record(USERS_TABLE, payload, use_admin=True)


def get_user_by_id(user_id: str):
    return fetch_one(USERS_TABLE, {"id": user_id})


def get_user_by_email(email: str):
    return fetch_one(USERS_TABLE, {"email": email})


def deactivate_user(user_id: str):
    return update_record(
        USERS_TABLE,
        {"id": user_id},
        {"is_active": False},
        use_admin=True
    )


def get_users_by_role(role: str):
    return fetch_all(USERS_TABLE, {"role": normalize_role(role)})


# -----------------------------
# Citizen Alias (Privacy)
# -----------------------------

def create_citizen_alias(user_id: str, random_username: str):
    payload = {
        "id": generate_uuid(),
        "user_id": user_id,
        "random_username": random_username,
        "created_at": utc_now()
    }
    return insert_record(CITIZEN_ALIAS_TABLE, payload, use_admin=True)


def get_citizen_alias(user_id: str):
    return fetch_one(CITIZEN_ALIAS_TABLE, {"user_id": user_id})


def get_alias_by_username(random_username: str):
    return fetch_one(CITIZEN_ALIAS_TABLE, {"random_username": random_username})
