from models.issue import get_issues_by_constituency
from models.rep_policy import get_policy_posts_by_constituency
from models.rep_policy_comments import get_policy_comments
from models.representative import get_rep_score
from statistics import mean


def calculate_resolution_rate(rep_user_id, constituency_id):
    issues = get_issues_by_constituency(constituency_id)

    accepted = [i for i in issues if i["status"] in ("Accepted", "In Progress", "Resolved","Closed")]
    resolved = [i for i in issues if i["status"] == "Closed"]
    if not accepted:
        return 0.0
    return round(len(resolved) / len(accepted), 2)


def calculate_engagement(constituency_id):
    posts = get_policy_posts_by_constituency(constituency_id)
    if not posts:
        return 0

    score = 0
    for p in posts:
        comments = get_policy_comments(p["id"])
        score += p["upvotes"] + len(comments)

    return score


def calculate_balance_index(constituency_id):
    posts = get_policy_posts_by_constituency(constituency_id)
    scores = [
        p["ai_confidence_score"]
        for p in posts
        if p.get("ai_confidence_score") is not None
    ]

    return round(mean(scores), 2) if scores else None


def build_accountability_snapshot(rep_user_id, constituency_id):
    return {
        "resolution_rate": calculate_resolution_rate(rep_user_id, constituency_id),
        "engagement_score": calculate_engagement(constituency_id),
        "balance_index": calculate_balance_index(constituency_id),
        "system_score": get_rep_score(rep_user_id)
    }
