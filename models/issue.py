from supabase_db.db import fetch_one, fetch_all, insert_record, update_record
from utils.helpers import generate_uuid, utc_now


# -----------------------------
# Table Names
# -----------------------------

ISSUES_TABLE = "issues"
ISSUE_VOTES_TABLE = "issue_votes"
ISSUE_COMMENTS_TABLE = "issue_comments"
ISSUE_RESOLUTION_TABLE = "issue_resolution"


# -----------------------------
# Issues
# -----------------------------

def create_issue(
    title: str,
    description: str,
    category: str,
    created_by: str,
    constituency_id: str,
    blockchain_hash: str = None
):
    payload = {
        "id": generate_uuid(),
        "title": title,
        "description": description,
        "category": category,
        "created_by": created_by,
        "constituency_id": constituency_id,
        "status": "Open",
        "blockchain_hash": blockchain_hash,
        "created_at": utc_now()
    }
    return insert_record(ISSUES_TABLE, payload, use_admin=True)


def get_issue_by_id(issue_id: str):
    return fetch_one(ISSUES_TABLE, {"id": issue_id})


def get_issues_by_constituency(constituency_id: str):
    return fetch_all(ISSUES_TABLE, {"constituency_id": constituency_id})


def update_issue_status(issue_id: str, status: str):
    return update_record(
        ISSUES_TABLE,
        {"id": issue_id},
        {"status": status},
        use_admin=True
    )


# -----------------------------
# Issue Votes (Upvote / Downvote)
# -----------------------------

def vote_on_issue(issue_id: str, user_id: str, vote_type: str):
    payload = {
        "id": generate_uuid(),
        "issue_id": issue_id,
        "user_id": user_id,
        "vote_type": vote_type,
        "created_at": utc_now()
    }
    return insert_record(ISSUE_VOTES_TABLE, payload, use_admin=True)


def get_issue_votes(issue_id: str):
    return fetch_all(ISSUE_VOTES_TABLE, {"issue_id": issue_id})


# -----------------------------
# Issue Comments
# -----------------------------

def add_issue_comment(issue_id: str, user_id: str, comment: str):
    payload = {
        "id": generate_uuid(),
        "issue_id": issue_id,
        "user_id": user_id,
        "comment": comment,
        "created_at": utc_now()
    }
    return insert_record(ISSUE_COMMENTS_TABLE, payload, use_admin=True)


def get_issue_comments(issue_id: str):
    return fetch_all(ISSUE_COMMENTS_TABLE, {"issue_id": issue_id})


# -----------------------------
# Issue Resolution
# -----------------------------

def mark_issue_resolved(issue_id: str, resolved_by: str):
    payload = {
        "id": generate_uuid(),
        "issue_id": issue_id,
        "resolved_by": resolved_by,
        "citizen_confirmed": False,
        "confirmed_at": None
    }
    return insert_record(ISSUE_RESOLUTION_TABLE, payload, use_admin=True)


def confirm_issue_resolution(issue_id: str):
    return update_record(
        ISSUE_RESOLUTION_TABLE,
        {"issue_id": issue_id},
        {
            "citizen_confirmed": True,
            "confirmed_at": utc_now()
        },
        use_admin=True
    )


def get_issue_resolution(issue_id: str):
    return fetch_one(ISSUE_RESOLUTION_TABLE, {"issue_id": issue_id})

def get_issues_by_user(user_id: str):
    return fetch_all(ISSUES_TABLE, {"created_by": user_id})

