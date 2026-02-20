from flask import Blueprint, jsonify, render_template, request
from utils.decorators import login_required, role_required
from models.election import get_current_active_election_for_results
from models.election import get_constituencies_for_election
from services.result_service import get_constituency_results

bp = Blueprint("results", __name__, url_prefix="/results")


# --------------------------------------------------
# Results Dashboard (HTML)
# --------------------------------------------------
@bp.route("/dashboard")
@login_required
@role_required("CEC", "CEO", "RO")
def dashboard():
    election = get_current_active_election_for_results()

    if not election:
        return render_template("results/no_active_election.html")

    constituencies = get_constituencies_for_election(election["id"])

    return render_template(
        "results/dashboard.html",
        election=election,
        constituencies=constituencies
    )


# --------------------------------------------------
# Constituency-wise Results API
# --------------------------------------------------
@bp.route("/api/constituency")
@login_required
@role_required("CEC", "CEO", "RO")
def constituency_results():
    election = get_current_active_election_for_results()
    constituency_id = request.args.get("constituency_id")

    if not election or not constituency_id:
        return jsonify({"error": "Invalid request"}), 400

    results = get_constituency_results(
        election_id=election["id"],
        constituency_id=constituency_id
    )

    return jsonify({
        "election_name": election["election_name"],
        "constituency_id": constituency_id,
        "results": results
    })
