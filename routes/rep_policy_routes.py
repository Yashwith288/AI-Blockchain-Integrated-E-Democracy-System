from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.decorators import login_required, role_required
from supabase_db.db import fetch_one, fetch_all, insert_record, update_record
from utils.helpers import generate_uuid, utc_now

from services.rep_policy_service import (
    create_new_policy_post,
    add_counter_statement,
    vote_policy_post,
    get_policy_feed
)

from models.rep_policy import get_policy_post_by_id
from services.rep_policy_comment_service import (
    add_comment,
    get_threaded_comments
)
from models.rep_policy_comments import get_policy_comments
from services.rep_policy_service import get_policy_feed_for_rep




bp = Blueprint("rep_policy", __name__, url_prefix="/policy")


# -------------------------------------------------
# Policy Feed (Public)
# -------------------------------------------------

@bp.route("/")
@login_required
def policy_feed():
    constituency_id = session.get("constituency_id")

    posts = get_policy_feed(constituency_id)

    return render_template(
        "policy/feed.html",
        posts=posts
    )

@bp.route("/rep/<rep_user_id>")
@login_required
def policy_feed_for_rep(rep_user_id):
    constituency_id = session.get("constituency_id")

    posts = get_policy_feed_for_rep(
        constituency_id=constituency_id,
        rep_user_id=rep_user_id
    )
    return render_template(
        "policy/feed.html",
        posts=posts
    )


# -------------------------------------------------
# Create Policy Post (REP / OPPOSITION)
# -------------------------------------------------

@bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("ELECTED_REP", "OPPOSITION_REP")
def create_policy():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        images = request.files.getlist("images")


        if not title or not content:
            flash("Title and content are required", "error")
            return redirect(request.url)

        create_new_policy_post(
            user_id=session["user_id"],
            role=session["role"],
            constituency_id=session["constituency_id"],
            title=title,
            content=content,
            images=images
        )

        flash("Forum post created", "success")
        return redirect(url_for("rep_policy.policy_feed"))

    return render_template("policy/create.html")



# -------------------------------------------------
# View Single Policy Post
# -------------------------------------------------

@bp.route("/<post_id>")
@login_required
def view_policy(post_id):
    post = get_policy_post_by_id(post_id, session["user_id"])
    comments = get_policy_comments(post_id)
    if not post:
        flash("Policy post not found", "error")
        return redirect(url_for("rep_policy.policy_feed"))

    return render_template(
        "policy/detail.html",
        post=post,
        comments=comments
    )

# -------------------------------------------------
# Add Counter Statement
# -------------------------------------------------

@bp.route("/<post_id>/counter", methods=["POST"])
@login_required
@role_required("ELECTED_REP", "OPPOSITION_REP")
def counter_statement(post_id):
    content = request.form.get("content")
    images = request.files.getlist("images")
    if not content:
        flash("Content required", "error")
        return redirect(url_for("rep_policy.view_policy", post_id=post_id))

    add_counter_statement(
        post_id=post_id,
        user_id=session["user_id"],
        role=session["role"],
        content=content,
        images=images
    )
    user_id = session["user_id"]
    role = session["role"]
    rep = fetch_one("representatives", {"user_id": user_id})

    if role == "ELECTED_REP":
        update_record(
            'rep_policy_posts',
            {"id": post_id},
            {
                "rep_name": rep.get("candidate_name"),
                "rep_party": rep.get("party_name"),
                "updated_at": utc_now().isoformat()
            },
            use_admin=True
        )

    elif role == "OPPOSITION_REP":
        update_record(
            'rep_policy_posts',
            {"id": post_id},
            {
                "opp_name": rep.get("candidate_name"),
                "opp_party": rep.get("party_name"),
                "updated_at": utc_now().isoformat()
            },
            use_admin=True
        )
    
    flash("Statement added", "success")
    return redirect(url_for("rep_policy.view_policy", post_id=post_id))


# -------------------------------------------------
# Voting
# -------------------------------------------------

@bp.route("/<post_id>/vote", methods=["POST"])
@login_required
def vote(post_id):
    vote_value = int(request.form.get("vote"))
    vote_policy_post(
        user_id=session["user_id"],
        post_id=post_id,
        vote_value=vote_value
    )

    # 🔥 Force fresh read (prevents stale counts)
    post = get_policy_post_by_id(post_id, session["user_id"])
    comments = get_policy_comments(post_id)

    return redirect(url_for("rep_policy.view_policy", post_id=post_id))


@bp.route("/<post_id>/comment", methods=["POST"])
@login_required
def comment(post_id):
    content = request.form.get("content")
    parent_id = request.form.get("parent_comment_id")

    if not content:
        flash("Comment cannot be empty", "error")
        return redirect(url_for("rep_policy.view_policy", post_id=post_id))

    add_comment(
        post_id=post_id,
        user_id=session["user_id"],
        content=content,
        parent_comment_id=parent_id
    )

    return redirect(url_for("rep_policy.view_policy", post_id=post_id))

@bp.route("/comment/<comment_id>/vote", methods=["POST"])
@login_required
def vote_comment_route(comment_id):
    vote_value = int(request.form.get("vote"))
    post_id = request.form.get("post_id")

    from services.rep_policy_comment_service import vote_comment

    vote_comment(
        user_id=session["user_id"],
        comment_id=comment_id,
        vote_value=vote_value
    )

    return redirect(url_for("rep_policy.view_policy", post_id=post_id), code=303)
