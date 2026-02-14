from supabase_db.db import fetch_one, fetch_all, insert_record, update_record
from utils.helpers import generate_uuid, utc_now
from models.voter import get_voter_by_user_id


REP_POLICY_POSTS_TABLE = "rep_policy_posts"
REP_POLICY_VOTES_TABLE = "rep_policy_votes"


# -------------------------------------------------
# Policy Posts
# -------------------------------------------------

def create_policy_post(
    user_id: str,
    role: str,
    constituency_id: str,
    title: str,
    content: str,
    image_urls: list = None
):
    """
    Create a new policy post.
    Only one side is filled based on creator role.
    """

    payload = {
        "id": generate_uuid(),
        "constituency_id": constituency_id,
        "created_by_user_id": user_id,
        "created_by_role": role,
        "title": title,
        "representative_statement": content if role == "ELECTED_REP" else None,
        "opposition_statement": content if role == "OPPOSITION_REP" else None,
        "image_urls": image_urls or [],
        "status": "OPEN",
        "created_at": utc_now().isoformat(),
        "updated_at": utc_now().isoformat(),
    }

    return insert_record(REP_POLICY_POSTS_TABLE, payload, use_admin=True)


def get_policy_post_by_id(post_id: str):
    post = fetch_one(REP_POLICY_POSTS_TABLE, {"id": post_id})
    if not post:
        return None
    # Fetch user info
    user = get_voter_by_user_id(post["created_by_user_id"])
    print('user info:', user)
    # Fetch representative info
    rep = fetch_one("representatives", {"user_id": post["created_by_user_id"]})
    print('rep info:', rep)
    post["author_name"] = user.get("full_name") if user else "Unknown"
    post["party_name"] = rep.get("party_name") if rep else "Independent"
    print(post)

    return post



def get_policy_posts_by_constituency(constituency_id: str):
    posts = fetch_all(
        REP_POLICY_POSTS_TABLE,
        {"constituency_id": constituency_id}
    ) or []

    # sort in Python (newest first)
    return sorted(
        posts,
        key=lambda p: p.get("created_at"),
        reverse=True
    )



def update_representative_statement(post_id: str, content: str):
    """
    Allows ONLY representative section to be updated.
    Service layer must validate role.
    """
    return update_record(
        REP_POLICY_POSTS_TABLE,
        {"id": post_id},
        {
            "representative_statement": content,
            "updated_at": utc_now().isoformat()
        },
        use_admin=True
    )


def update_opposition_statement(post_id: str, content: str):
    """
    Allows ONLY opposition section to be updated.
    Service layer must validate role.
    """
    return update_record(
        REP_POLICY_POSTS_TABLE,
        {"id": post_id},
        {
            "opposition_statement": content,
            "updated_at": utc_now().isoformat()
        },
        use_admin=True
    )


# -------------------------------------------------
# Voting (Low-level)
# -------------------------------------------------

def get_user_vote(post_id: str, user_id: str):
    return fetch_one(
        REP_POLICY_VOTES_TABLE,
        {"post_id": post_id, "user_id": user_id}
    )


def upsert_vote(post_id: str, user_id: str, vote_value: int):
    """
    Inserts or updates vote.
    Trigger handles count updates.
    """
    existing = get_user_vote(post_id, user_id)

    if existing:
        return update_record(
            REP_POLICY_VOTES_TABLE,
            {"id": existing["id"]},
            {
                "vote_value": vote_value,
                "updated_at": utc_now().isoformat()
            },
            use_admin=True
        )

    payload = {
        "id": generate_uuid(),
        "post_id": post_id,
        "user_id": user_id,
        "vote_value": vote_value,
        "created_at": utc_now().isoformat(),
        "updated_at": utc_now().isoformat()
    }

    return insert_record(REP_POLICY_VOTES_TABLE, payload, use_admin=True)


def remove_vote(post_id: str, user_id: str):
    """
    Optional – allows vote removal.
    """
    return update_record(
        REP_POLICY_VOTES_TABLE,
        {"post_id": post_id, "user_id": user_id},
        {"vote_value": 0},
        use_admin=True
    )

def update_policy_post_images(post_id, image_urls):
    return update_record(
        REP_POLICY_POSTS_TABLE,
        {"id": post_id},
        {
            "counter_image_urls": image_urls,
            "updated_at": utc_now().isoformat()
        },
        use_admin=True
    )
