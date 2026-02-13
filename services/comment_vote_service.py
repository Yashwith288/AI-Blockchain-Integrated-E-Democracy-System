from models.comment_vote import (
    get_user_comment_vote,
    add_comment_vote,
    update_comment_vote,
    remove_comment_vote
)


def toggle_comment_vote(comment_id, user_id, vote_type):
    existing = get_user_comment_vote(comment_id, user_id)

    if existing:
        if existing["vote_type"] == vote_type:
            remove_comment_vote(existing["id"])
        else:
            update_comment_vote(existing["id"], vote_type)
    else:
        add_comment_vote(comment_id, user_id, vote_type)
