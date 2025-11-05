from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, go directly to dashboard
    if current_user.is_authenticated:
        return redirect(url_for("tasks.dashboard"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        # Simple validation: username and password must not be empty
        if not username:
            flash("Username is required", "danger")
            return render_template("login.html")

        if not password:
            flash("Password is required", "danger")
            return render_template("login.html")

        # Check if user exists in database
        user = User.query.filter_by(username=username).first()

        if user:
            # If user exists, validate password
            if user.check_password(password):
                login_user(user)
                flash("Login successful", "success")
                return redirect(url_for("tasks.dashboard"))
            else:
                # If password doesn't match, still allow login but update password
                user.set_password(password)
                db.session.commit()
                login_user(user)
                flash("Login successful", "success")
                return redirect(url_for("tasks.dashboard"))
        else:
            # Create new user if doesn't exist
            new_user = User(username=username, is_admin=True)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash("Login successful", "success")
            return redirect(url_for("tasks.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("auth.login"))
