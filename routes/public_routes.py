from flask import Blueprint, render_template
from models.election import get_all_elections

bp = Blueprint("public", __name__)

@bp.route("/elections")
def election_schedule():
    elections = get_all_elections()
    return render_template(
        "public/election_schedule.html",
        elections=elections
    )
@bp.route("/")
def landing():
    elections = get_all_elections()
    return render_template("public/landing.html",elections=elections)


