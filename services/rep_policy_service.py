from models.rep_policy import (
    create_policy_post,
    get_policy_post_by_id,
    get_policy_posts_by_constituency,
    update_representative_statement,
    update_opposition_statement,
    upsert_vote
)
from models.audit import create_audit_log
from services.policy_ai_service import (
    should_run_ai,
    store_ai_analysis
)
from services.policy_ai_prompt import build_policy_prompt
from services.ai_client import run_policy_analysis, AIClientError
import cloudinary.uploader
from utils.helpers import generate_uuid, utc_now
import cloudinary.uploader
from utils.helpers import utc_now
from models.rep_policy import update_policy_post_images


# -------------------------------------------------
# Policy Post Creation
# -------------------------------------------------




def create_new_policy_post(user_id, role, constituency_id, title, content, images=None):
    if role not in ("ELECTED_REP", "OPPOSITION_REP"):
        raise PermissionError("Only representatives can create forum posts")

    # -----------------------------
    # Upload images to Cloudinary
    # -----------------------------
    image_urls = []

    if images:
        for file in images:
            if file and file.filename:
                try:
                    upload_result = cloudinary.uploader.upload(
                        file,
                        folder="forum_posts",   # changed folder for clarity
                        resource_type="image",
                        transformation=[
                            {"width": 1200, "height": 1200, "crop": "limit"},
                            {"quality": "auto"},
                            {"fetch_format": "auto"}
                        ]
                    )
                    image_urls.append(upload_result["secure_url"])

                except Exception:
                    # Skip failed uploads but continue creating post
                    continue

    # -----------------------------
    # Create post in DB
    # -----------------------------
    post = create_policy_post(
        user_id=user_id,
        role=role,
        constituency_id=constituency_id,
        title=title,
        content=content,
        image_urls=image_urls
    )

    # -----------------------------
    # Audit log
    # -----------------------------
    create_audit_log(
        user_id=user_id,
        action="CREATE_FORUM_POST",
        entity_type="REP_POLICY_POST",
        entity_id=post[0]["id"]
    )

    return post




# -------------------------------------------------
# Counter Statement Logic
# -------------------------------------------------

def add_counter_statement(post_id, user_id, role, content, images=None):
    post = get_policy_post_by_id(post_id)
    if not post:
        raise ValueError("Policy post not found")
    
    if role == "ELECTED_REP":
        if post.get("representative_statement"):
            raise ValueError("Representative statement already exists")
        update_representative_statement(post_id, content)

    elif role == "OPPOSITION_REP":
        if post.get("opposition_statement"):
            raise ValueError("Opposition statement already exists")
        update_opposition_statement(post_id, content)

    else:
        raise PermissionError("Only representatives may respond")

    create_audit_log(
        user_id=user_id,
        action="ADD_COUNTER_STATEMENT",
        entity_type="REP_POLICY_POST",
        entity_id=post_id
    )


# -------------------------------------------------
# Voting Logic
# -------------------------------------------------

def vote_policy_post(user_id, post_id, vote_value):
    if vote_value not in (1, -1):
        raise ValueError("Invalid vote")

    upsert_vote(
        post_id=post_id,
        user_id=user_id,
        vote_value=vote_value
    )

    create_audit_log(
        user_id=user_id,
        action="VOTE_POLICY_POST",
        entity_type="REP_POLICY_POST",
        entity_id=post_id
    )


# -------------------------------------------------
# Feed
# -------------------------------------------------

def get_policy_feed(constituency_id):
    posts = get_policy_posts_by_constituency(constituency_id)

    # sort by net votes, then recency
    return sorted(
        posts,
        key=lambda p: ((p["upvotes"] - p["downvotes"]), p["created_at"]),
        reverse=True
    )

def add_counter_statement(post_id, user_id, role, content, images=None):
    post = get_policy_post_by_id(post_id)
    if not post:
        raise ValueError("Policy post not found")

    # ---------------------------
    # Upload images to Cloudinary
    # ---------------------------
    image_urls = []

    if images:
        for file in images:
            if file and file.filename:
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="forum_posts",
                    resource_type="image",
                    transformation=[
                        {"width": 1200, "height": 1200, "crop": "limit"},
                        {"quality": "auto"},
                        {"fetch_format": "auto"}
                    ]
                )
                image_urls.append(upload_result["secure_url"])

    # ---------------------------
    # Update statements
    # ---------------------------
    if role == "ELECTED_REP":
        if post.get("representative_statement"):
            raise ValueError("Representative statement already exists")

        update_representative_statement(post_id, content)

        if image_urls:
            update_policy_post_images(post_id, image_urls)

    elif role == "OPPOSITION_REP":
        if post.get("opposition_statement"):
            raise ValueError("Opposition statement already exists")

        update_opposition_statement(post_id, content)

        if image_urls:
            update_policy_post_images(post_id, image_urls)

    else:
        raise PermissionError("Only representatives may respond")

    # ---------------------------
    # Audit log
    # ---------------------------
    create_audit_log(
        user_id=user_id,
        action="ADD_COUNTER_STATEMENT",
        entity_type="REP_POLICY_POST",
        entity_id=post_id
    )

    # 🔥 AI TRIGGER (SAFE)
    post = get_policy_post_by_id(post_id)
    if should_run_ai(post):
        try:
            prompt = build_policy_prompt(
                post["representative_statement"],
                post["opposition_statement"]
            )

            result = run_policy_analysis(prompt)

            store_ai_analysis(
                post_id=post_id,
                summary=result["summary"],
                fact_check=result["fact_check"],
                confidence_score=result["confidence_score"]
            )

        except AIClientError as e:
            # ⚠️ AI failure must NEVER block governance
            create_audit_log(
                user_id=user_id,
                action="AI_POLICY_ANALYSIS_FAILED",
                entity_type="REP_POLICY_POST",
                entity_id=post_id,
                metadata={"error": str(e)}
            )
