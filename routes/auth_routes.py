from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import login_user, logout_current_user
from services.booth_session_service import unregister_voting_terminal
from services.email_service import send_otp_email
from services.otp_service import generate_otp, verify_otp
from models.user import get_user_by_email
from supabase_db.client import supabase_public


bp = Blueprint("auth", __name__, url_prefix="/auth")


# -----------------------------
# Login
# -----------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        # already logged in → redirect to dashboard
        role = session.get("role")

        if role == "CITIZEN":
            return redirect(url_for("citizen.dashboard"))
        elif role == "PO":
            return redirect(url_for("presiding_officer.dashboard"))
        elif role in {"ELECTED_REP", "OPPOSITION_REP"}:
            return redirect(url_for("representative.dashboard"))
        else:
            return redirect(url_for("election_commission.dashboard"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            user = login_user(email, password)
            role = user.get("role")

            # -----------------------------
            # Role-based redirect
            # -----------------------------
            if role == "CITIZEN":
                return redirect(url_for("citizen.dashboard"))

            elif role == "PO":
                # Presiding Officer → Booth control
                return redirect(url_for("presiding_officer.dashboard"))

            elif role in {"ELECTED_REP", "OPPOSITION_REP"}:
                return redirect(url_for("representative.dashboard"))

            else:
                # CEC, CEO, DEO, RO, ERO, BLO
                return redirect(url_for("election_commission.dashboard"))

        except Exception as e:
            flash(str(e), "error")

    return render_template("auth/login.html")


# -----------------------------
# Logout
# -----------------------------
@bp.route("/logout")
def logout():
    # 🔑 IMPORTANT: Release voting terminal on logout
    booth_id = session.get("booth_id")
    if booth_id:
        unregister_voting_terminal(booth_id)

    logout_current_user()
    return redirect(url_for("public.landing"))

# -----------------------------
# Forgot Password - Request
# -----------------------------
@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        user = get_user_by_email(email)
        if not user:
            flash("No account found with this email", "error")
            return redirect(url_for("auth.forgot_password"))

        otp = generate_otp(str(user["id"]))
        send_otp_email(email, otp)

        session["reset_user_id"] = str(user["id"])
        flash("OTP sent to your email", "success")
        return redirect(url_for("auth.verify_reset_otp"))

    return render_template("auth/forgot_password.html")


# -----------------------------
# Verify OTP
# -----------------------------
@bp.route("/verify-reset-otp", methods=["GET", "POST"])
def verify_reset_otp():
    user_id = session.get("reset_user_id")
    if not user_id:
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        otp = request.form.get("otp")

        if verify_otp(user_id, otp):
            session["otp_verified"] = True
            return redirect(url_for("auth.reset_password"))
        else:
            flash("Invalid or expired OTP", "error")

    return render_template("auth/verify_reset_otp.html")


# -----------------------------
# Reset Password
# -----------------------------
@bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    user_id = session.get("reset_user_id")
    verified = session.get("otp_verified")

    if not user_id or not verified:
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password")

        # 🔐 Supabase password update
        supabase_public.auth.admin.update_user_by_id(
            user_id,
            {"password": new_password}
        )

        session.pop("reset_user_id", None)
        session.pop("otp_verified", None)

        flash("Password reset successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")

