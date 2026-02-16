import os
from models.rep_policy_comments import (
    add_policy_comment,
    get_policy_comments
)
from models.audit import create_audit_log
from models.rep_policy import get_policy_post_by_id
from services.policy_ai_prompt import build_policy_prompt
from services.ai_client import run_policy_analysis, AIClientError
from utils.helpers import utc_now
from supabase_db.db import insert_record
from services.ai_client import run_comment_reply
from services.citizen_service import ensure_citizen_alias
from models.rep_policy_comment_votes import (
    get_user_comment_vote,
    upsert_comment_vote,
    remove_comment_vote
)



def add_comment(post_id, user_id, content, parent_comment_id=None):
    ensure_citizen_alias(user_id)
    comment = add_policy_comment(
        post_id=post_id,
        user_id=user_id,
        content=content,
        parent_comment_id=parent_comment_id
    )

    create_audit_log(
        user_id=user_id,
        action="ADD_POLICY_COMMENT",
        entity_type="REP_POLICY_POST",
        entity_id=post_id
    )

    return comment


def build_comment_tree(comments):
    """
    Converts flat list → nested tree
    """
    comment_map = {}
    roots = []

    for c in comments:
        c["replies"] = []
        comment_map[c["id"]] = c

    for c in comments:
        parent_id = c.get("parent_comment_id")
        if parent_id and parent_id in comment_map:
            comment_map[parent_id]["replies"].append(c)
        else:
            roots.append(c)

    return roots


def get_threaded_comments(post_id):
    comments = get_policy_comments(post_id)
    return build_comment_tree(comments)

def should_trigger_ai_reply(content: str) -> bool:
    content = content.strip().lower()
    return "@ai" in content

def build_comment_ai_prompt(post, thread_context, user_comment):
    return f"""
You are an AI assistant in a democratic policy discussion.

Rules:
- Be neutral.
- Do NOT take sides.
- Do NOT persuade.
- Clarify facts if possible.
- If uncertain, say so.

Representative Statement:
\"\"\"{post.get('representative_statement')}\"\"\"

Opposition Statement:
\"\"\"{post.get('opposition_statement')}\"\"\"

Discussion Context:
\"\"\"{thread_context}\"\"\"

User Question:
\"\"\"{user_comment}\"\"\"

Respond concisely.
"""

def add_comment(post_id, user_id, content, parent_comment_id=None):
    
    comment = add_policy_comment(
        post_id=post_id,
        user_id=user_id,
        content=content,
        parent_comment_id=parent_comment_id
    )

    create_audit_log(
        user_id=user_id,
        action="ADD_POLICY_COMMENT",
        entity_type="REP_POLICY_POST",
        entity_id=post_id
    )

    # 🔥 AI REPLY LOGIC
    if should_trigger_ai_reply(content):

        post = get_policy_post_by_id(post_id)

        try:
            thread_context = content  # Simplified first version

            prompt = build_comment_ai_prompt(
                post,
                thread_context,
                content
            )

            ai_text = run_comment_reply(prompt)
            user_id=os.getenv("AI_SYSTEM_USER_ID")
            print(user_id)
            insert_record(
                "rep_policy_comments",
                {
                    "post_id": post_id,
                    "user_id": user_id,  # AI has no user
                    "content": ai_text,
                    "parent_comment_id": comment[0]["id"],
                    "ai_generated": True,
                    "created_at": utc_now().isoformat(),
                    "updated_at": utc_now().isoformat(),
                },
                use_admin=True
            )

        except AIClientError:
            pass  # AI failure should not break discussion

    return comment

def vote_comment(user_id, comment_id, vote_value):

    if vote_value not in (1, -1):
        raise ValueError("Invalid vote")

    existing = get_user_comment_vote(comment_id, user_id)

    if not existing:
        upsert_comment_vote(comment_id, user_id, vote_value)

    elif existing["vote_value"] == vote_value:
        remove_comment_vote(comment_id, user_id)

    else:
        upsert_comment_vote(comment_id, user_id, vote_value)

