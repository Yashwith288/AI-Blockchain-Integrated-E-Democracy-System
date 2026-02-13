from supabase_db.db import fetch_one, fetch_all, insert_record, update_record, delete_record
from utils.helpers import generate_uuid, utc_now

TABLE = "comment_votes"


def get_user_comment_vote(comment_id, user_id):
    return fetch_one(TABLE, {
        "comment_id": comment_id,
        "user_id": user_id
    })


def add_comment_vote(comment_id, user_id, vote_type):
    return insert_record(TABLE, {
        "id": generate_uuid(),
        "comment_id": comment_id,
        "user_id": user_id,
        "vote_type": vote_type,
        "created_at": utc_now().isoformat()
    }, use_admin=True)


def update_comment_vote(vote_id, vote_type):
    return update_record(TABLE, {"id": vote_id}, {
        "vote_type": vote_type
    }, use_admin=True)


def remove_comment_vote(vote_id):
    return delete_record(TABLE, {"id": vote_id}, use_admin=True)


def get_comment_score(comment_id):
    votes = fetch_all(TABLE, {"comment_id": comment_id})
    score = 0
    for v in votes:
        score += 1 if v["vote_type"] == "up" else -1
    return score
