from flask import session
from datetime import datetime
from supabase_db.client import supabase_public
from models.user import get_user_by_email
from utils.helpers import is_valid_email, normalize_role
from models.audit import create_audit_log


# -----------------------------
# Authentication Service
# -----------------------------

def login_user(email: str, password: str):
    """
    Handles full login flow:
    - Supabase Auth (v2)
    - Internal user lookup
    - Flask session setup
    """

    if not is_valid_email(email):
        raise ValueError("Invalid email format")

    # Authenticate with Supabase (v2 API)
    response = supabase_public.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if not response or not response.user:
        raise ValueError("Invalid email or password")

    supa_user = response.user

    # Fetch internal user record
    user = get_user_by_email(supa_user.email)
    if not user or not user.get("is_active"):
        raise ValueError("User not found or inactive")

    # Clear and set Flask session (used by decorators)
    session.clear()
    session["user_id"] = user["id"]
    session["email"] = user["email"]
    session["role"] = normalize_role(user["role"])
    session["state_id"] = user.get("state_id")
    session["district_id"] = user.get("district_id")
    session["constituency_id"] = user.get("constituency_id")
    session["booth_id"] = user.get("booth_id")
    session["logged_in_at"] = datetime.utcnow().isoformat()

    # Audit log
    create_audit_log(
        user_id=user["id"],
        action="LOGIN",
        entity_type="USER",
        entity_id=user["id"]
    )

    return user


def logout_current_user():
    """
    Logout user from Supabase and clear Flask session
    """
    try:
        supabase_public.auth.sign_out()
    finally:
        session.clear()
