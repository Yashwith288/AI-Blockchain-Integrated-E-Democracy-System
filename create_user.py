"""
One-time admin script to create users.

This script:
1. Creates user in Supabase Auth (email + password)
2. Inserts user into public.users table
3. Assigns role and election hierarchy

Run manually:
python scripts/create_user.py
"""

from supabase import create_client
from config import Config
from datetime import datetime


# -----------------------------
# Supabase Admin Client
# -----------------------------

supabase = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_SERVICE_ROLE_KEY
)


# -----------------------------
# CONFIGURE USER HERE
# -----------------------------

USER_DATA = {
    "email": "ceo@eci.gov.in",
    "password": "ceo@12345678",
    "role": "CEO",

    # Hierarchy (set None if not applicable)
    "state_id": 'c44b37b1-ced8-4344-b091-4e60465dbbf3',
    "district_id": None,
    "constituency_id": None,
    "booth_id": None
}


# -----------------------------
# CREATE USER
# -----------------------------

def create_user():
    print("Creating user in Supabase Auth...")

    # 1️⃣ Create user in auth.users
    auth_response = supabase.auth.admin.create_user({
        "email": USER_DATA["email"],
        "password": USER_DATA["password"],
        "email_confirm": True
    })

    user = auth_response.user
    if not user:
        raise Exception("Failed to create auth user")

    print(f"Auth user created: {user.id}")

    # 2️⃣ Insert into public.users
    print("Inserting into public.users...")

    db_response = supabase.table("users").insert({
        "id": user.id,                     # IMPORTANT: same UUID
        "email": USER_DATA["email"],
        "role": USER_DATA["role"],
        "state_id": USER_DATA["state_id"],
        "district_id": USER_DATA["district_id"],
        "constituency_id": USER_DATA["constituency_id"],
        "booth_id": USER_DATA["booth_id"],
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    print("User created successfully!")
    print(db_response.data)


if __name__ == "__main__":
    create_user()
