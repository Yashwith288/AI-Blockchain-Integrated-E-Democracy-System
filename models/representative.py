from supabase_db.db import fetch_one, fetch_all, insert_record, update_record
from utils.helpers import generate_uuid, utc_now
from datetime import date



# -----------------------------
# Table Names
# -----------------------------
REPRESENTATIVES_TABLE = "representatives"
REP_POSTS_TABLE = "rep_posts"
REP_COMMENTS_TABLE = "rep_comments"
REP_SCORES_TABLE = "rep_scores"


def create_representative(
    user_id: str,
    constituency_id: str,
    rep_type: str,
    term_start,
    term_end,
    election_id: str,
    candidate_id: str,
    candidate_name: str,
    party_name: str
):
    payload = {
        "id": generate_uuid(),
        "user_id": user_id,
        "constituency_id": constituency_id,
        "type": rep_type,
        "term_start": term_start.isoformat(),
        "term_end": term_end.isoformat(),
        "election_id": election_id,
        "candidate_id": candidate_id,
        "candidate_name": candidate_name,
        "party_name": party_name,
        "created_at": utc_now().isoformat(),
    }
    initialize_rep_score(user_id)
    return insert_record(REPRESENTATIVES_TABLE, payload, use_admin=True)

# -----------------------------
# Representative Posts
# -----------------------------

def create_rep_post(user_id: str, constituency_id: str, content: str):
    payload = {
        "id": generate_uuid(),
        "user_id": user_id,
        "constituency_id": constituency_id,
        "content": content,
        "created_at": utc_now().isoformat()
    }
    return insert_record(REP_POSTS_TABLE, payload, use_admin=True)


def get_rep_post_by_id(post_id: str):
    return fetch_one(REP_POSTS_TABLE, {"id": post_id})


def get_rep_posts_by_constituency(constituency_id: str):
    return fetch_all(REP_POSTS_TABLE, {"constituency_id": constituency_id})


def get_rep_posts_by_user(user_id: str):
    return fetch_all(REP_POSTS_TABLE, {"user_id": user_id})


# -----------------------------
# Representative Comments (Debate)
# -----------------------------

def add_rep_comment(post_id: str, user_id: str, comment: str):
    payload = {
        "id": generate_uuid(),
        "post_id": post_id,
        "user_id": user_id,
        "comment": comment,
        "created_at": utc_now().isoformat()
    }
    return insert_record(REP_COMMENTS_TABLE, payload, use_admin=True)


def get_rep_comments(post_id: str):
    return fetch_all(REP_COMMENTS_TABLE, {"post_id": post_id})


# -----------------------------
# Representative Scores (Private)
# -----------------------------

def initialize_rep_score(user_id: str):
    payload = {
        "id": generate_uuid(),
        "user_id": user_id,
        "post_score": 0,
        "issue_resolution_score": 0,
        "overall_score": 0,
        "updated_at": utc_now().isoformat()
    }
    return insert_record(REP_SCORES_TABLE, payload, use_admin=True)


def get_rep_score(user_id: str):
    return fetch_one(REP_SCORES_TABLE, {"user_id": user_id})


def update_rep_score(
    user_id: str,
    post_score_delta: int = 0,
    issue_score_delta: int = 0
):
    current = get_rep_score(user_id)

    if not current:
        current = initialize_rep_score(user_id)[0]

    new_post_score = current["post_score"] + post_score_delta
    new_issue_score = current["issue_resolution_score"] + issue_score_delta
    new_overall_score = new_post_score + new_issue_score

    return update_record(
        REP_SCORES_TABLE,
        {"user_id": user_id},
        {
            "post_score": new_post_score,
            "issue_resolution_score": new_issue_score,
            "overall_score": new_overall_score,
            "updated_at": utc_now().isoformat()
        },
        use_admin=True
    )

def get_active_representatives(today: date):
    reps = fetch_all(REPRESENTATIVES_TABLE)

    active = []
    for r in reps:
        if r["term_start"] <= today.isoformat() <= r["term_end"]:
            active.append(r)

    return active


def get_all_representatives():
    return fetch_all(REPRESENTATIVES_TABLE)