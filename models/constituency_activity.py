from supabase_db.db import fetch_all,fetch_one
from utils.helpers import utc_now
from datetime import datetime


# -----------------------------
# Table Names
# -----------------------------

ISSUES_TABLE = "issues"
ISSUE_COMMENTS_TABLE = "issue_comments"
ISSUE_TIMELINE_TABLE = "issue_status_timeline"
ISSUE_RESOLUTION_TABLE = "issue_resolution"

POLICY_POSTS_TABLE = "rep_policy_posts"
POLICY_COMMENTS_TABLE = "rep_policy_comments"


ISSUE_VOTES_TABLE = "issue_votes"
ISSUE_FEEDBACK_TABLE = "issue_feedback"
ELECTIONS_TABLE = "elections"
ELECTION_CONST_TABLE = "election_constituencies"
REPRESENTATIVES_TABLE = "representatives"


# -----------------------------
# Helper: today window
# -----------------------------

def _today_iso_prefix():
    # YYYY-MM-DD
    return utc_now().date().isoformat()


# -----------------------------
# Issues Created Today
# -----------------------------

def get_issues_created_today(constituency_id: str):
    issues = fetch_all(
        ISSUES_TABLE,
        {"constituency_id": constituency_id}
    ) or []

    today = _today_iso_prefix()

    return [
        {
            "id": i["id"],
            "title": i["title"],
            "category": i["category"],
            "created_at": i["created_at"]
        }
        for i in issues
        if i.get("created_at", "").startswith(today)
    ]


# -----------------------------
# Issues Getting Attention Today
# -----------------------------

def get_active_issue_discussions_today(constituency_id: str):
    issues = fetch_all(
        ISSUES_TABLE,
        {"constituency_id": constituency_id}
    ) or []

    today = _today_iso_prefix()
    results = []

    for issue in issues:
        comments = fetch_all(
            ISSUE_COMMENTS_TABLE,
            {"issue_id": issue["id"]}
        ) or []

        today_comments = [
            c for c in comments
            if c.get("created_at", "").startswith(today)
        ]

        if len(today_comments) >= 3:   # threshold for activity
            results.append({
                "issue_id": issue["id"],
                "title": issue["title"],
                "comment_count_today": len(today_comments)
            })

    return results


# -----------------------------
# Issues Resolved Today
# -----------------------------

def get_issues_resolved_today(constituency_id: str):
    issues = fetch_all(
        ISSUES_TABLE,
        {"constituency_id": constituency_id}
    ) or []

    today = _today_iso_prefix()
    resolved = []

    for issue in issues:
        resolution = fetch_all(
            ISSUE_RESOLUTION_TABLE,
            {"issue_id": issue["id"]}
        ) or []

        for r in resolution:
            if r.get("confirmed_at") and r["confirmed_at"].startswith(today):
                resolved.append({
                    "issue_id": issue["id"],
                    "title": issue["title"]
                })

    return resolved


# -----------------------------
# Policy Posts Created Today
# -----------------------------

def get_policy_posts_today(constituency_id: str):
    posts = fetch_all(
        POLICY_POSTS_TABLE,
        {"constituency_id": constituency_id}
    ) or []

    today = _today_iso_prefix()

    return [
        {
            "id": p["id"],
            "title": p.get("title"),
            "author_role": p.get("created_by_role"),
            "author_name": p.get("rep_name") or p.get("opp_name")
        }
        for p in posts
        if p.get("created_at", "").startswith(today)
    ]


# -----------------------------
# Active Policy Debates Today
# -----------------------------

def get_active_policy_debates_today(constituency_id: str):
    posts = fetch_all(
        POLICY_POSTS_TABLE,
        {"constituency_id": constituency_id}
    ) or []

    today = _today_iso_prefix()
    debates = []

    for p in posts:
        comments = fetch_all(
            POLICY_COMMENTS_TABLE,
            {"post_id": p["id"]}
        ) or []

        today_comments = [
            c for c in comments
            if c.get("created_at", "").startswith(today)
        ]

        if len(today_comments) >= 3:
            debates.append({
                "post_id": p["id"],
                "title": p.get("title"),
                "comment_count_today": len(today_comments)
            })

    return debates


# --------------------------------------------------
# 🔥 TRENDING ISSUES (high engagement recently)
# --------------------------------------------------

def get_trending_issues(constituency_id: str, limit: int = 5):
    issues = fetch_all(ISSUES_TABLE, {"constituency_id": constituency_id}) or []

    enriched = []

    for i in issues:
        votes = fetch_all(ISSUE_VOTES_TABLE, {"issue_id": i["id"]}) or []
        comments = fetch_all(ISSUE_COMMENTS_TABLE, {"issue_id": i["id"]}) or []

        score = 0
        for v in votes:
            if v["vote_type"] == "up":
                score += 1
            elif v["vote_type"] == "down":
                score -= 1

        engagement = score + len(comments)

        enriched.append({
            "id": i["id"],
            "title": i["title"],
            "engagement": engagement,
            "status": i["status"]
        })

    enriched.sort(key=lambda x: x["engagement"], reverse=True)
    return enriched[:limit]


# --------------------------------------------------
# ⚠️ BACKLASH SIGNALS (negative sentiment)
# --------------------------------------------------

def get_backlash_issues(constituency_id: str, limit: int = 3):
    issues = fetch_all(ISSUES_TABLE, {"constituency_id": constituency_id}) or []

    backlash = []

    for i in issues:
        votes = fetch_all(ISSUE_VOTES_TABLE, {"issue_id": i["id"]}) or []
        feedback = fetch_all(ISSUE_FEEDBACK_TABLE, {"issue_id": i["id"]}) or []

        downvotes = sum(1 for v in votes if v["vote_type"] == "down")
        low_ratings = sum(1 for f in feedback if (f.get("rating") or 5) <= 2)

        if downvotes + low_ratings >= 3:
            backlash.append({
                "title": i["title"],
                "negative_score": downvotes + low_ratings
            })

    backlash.sort(key=lambda x: x["negative_score"], reverse=True)
    return backlash[:limit]


# --------------------------------------------------
# 👍 ENCOURAGED ITEMS (popular support)
# --------------------------------------------------

def get_supported_issues(constituency_id: str, limit: int = 3):
    issues = fetch_all(ISSUES_TABLE, {"constituency_id": constituency_id}) or []

    supported = []

    for i in issues:
        votes = fetch_all(ISSUE_VOTES_TABLE, {"issue_id": i["id"]}) or []
        upvotes = sum(1 for v in votes if v["vote_type"] == "up")

        if upvotes >= 5:
            supported.append({
                "title": i["title"],
                "support": upvotes
            })

    supported.sort(key=lambda x: x["support"], reverse=True)
    return supported[:limit]


# --------------------------------------------------
# 🏛 ACTIVE POLICY DISCUSSIONS
# --------------------------------------------------

def get_active_policy_discussions(constituency_id: str, limit: int = 3):
    posts = fetch_all(POLICY_POSTS_TABLE, {"constituency_id": constituency_id}) or []

    enriched = []

    for p in posts:
        comments = fetch_all(POLICY_COMMENTS_TABLE, {"post_id": p["id"]}) or []

        enriched.append({
            "title": p.get("title"),
            "discussion_count": len(comments)
        })

    enriched.sort(key=lambda x: x["discussion_count"], reverse=True)
    return enriched[:limit]


# --------------------------------------------------
# 🗳 UPCOMING OR ACTIVE ELECTIONS
# --------------------------------------------------

def get_active_elections(constituency_id: str):
    links = fetch_all(ELECTION_CONST_TABLE, {"constituency_id": constituency_id}) or []

    active = []

    for l in links:
        election = fetch_one(ELECTIONS_TABLE, {"id": l["election_id"]})
        if not election:
            continue

        if election["status"] in ["Upcoming", "Ongoing"]:
            active.append({
                "name": election["election_name"],
                "status": election["status"],
                "start": election["start_time"],
                "end": election["end_time"]
            })

    return active


# --------------------------------------------------
# ⏳ REPRESENTATIVE TERM ENDING SOON
# --------------------------------------------------

def get_representatives_ending_soon(constituency_id: str, days: int = 30):
    reps = fetch_all(REPRESENTATIVES_TABLE, {"constituency_id": constituency_id}) or []

    soon = []
    now = utc_now().date()

    for r in reps:
        term_end = r.get("term_end")
        if not term_end:
            continue

        # 🔧 Convert string → date safely
        if isinstance(term_end, str):
            try:
                term_end = datetime.fromisoformat(term_end).date()
            except Exception:
                continue

        delta = (term_end - now).days

        if 0 <= delta <= days:
            soon.append({
                "name": r.get("candidate_name"),
                "party": r.get("party_name"),
                "days_left": delta
            })

    return soon



# --------------------------------------------------
# 📊 MASTER SNAPSHOT FOR AI
# --------------------------------------------------

def get_constituency_activity_snapshot(constituency_id: str):
    """
    Ordered civic intelligence snapshot for AI.
    Highest-impact signals come first.
    """

    return {

        # 🔴 GOVERNANCE-CRITICAL
        "active_elections": get_active_elections(constituency_id),
        "rep_terms_ending": get_representatives_ending_soon(constituency_id),

        # 🟠 PUBLIC SENTIMENT SIGNALS
        "backlash_signals": get_backlash_issues(constituency_id),
        "supported_issues": get_supported_issues(constituency_id),

        # 🟡 CURRENT CIVIC FOCUS
        "trending_issues": get_trending_issues(constituency_id),
        "active_policy_debates": get_active_policy_debates_today(constituency_id),
        "active_issue_discussions": get_active_issue_discussions_today(constituency_id),

        # 🟢 FRESH EVENTS
        "new_issues": get_issues_created_today(constituency_id),
        "new_policy_posts": get_policy_posts_today(constituency_id),
        "issues_resolved": get_issues_resolved_today(constituency_id),

        # ⚪ META
        "generated_at": utc_now().isoformat()
    }
