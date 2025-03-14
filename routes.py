from functools import wraps

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models import Chapter, Question, Quiz, Score, Subject, User, db


def set_routes(app):
    
    # --- Auth Routes ---
    
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            full_name = request.form.get(
                "full_name"
            )  # getting important data from form
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            user_exist = User.query.filter_by(
                username=username
            ).first()  # check if any same username already exists
            email_exist = User.query.filter_by(
                email=email
            ).first()  # check if any same email already exists
            if (
                not full_name
                or not username
                or not email
                or not password
                or not confirm_password
            ):
                flash("All fields are required")
                return render_template("signup.html")
            elif password != confirm_password:
                flash("Passwords do not match")
                return render_template("signup.html")
            elif user_exist:
                flash("Username already exists")
                return render_template("signup.html")
            elif email_exist:
                flash("Account already exists, Please Login")
                return render_template("signup.html")
            passhash = generate_password_hash(password)
            new_user = User(
                fullname=full_name, username=username, email=email, passhash=passhash
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account successfully created")
            return redirect(url_for("login"))

        return render_template("signup.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if not username or not password:
                flash("Username and password are required")
                return render_template("login.html")
            user = User.query.filter_by(username=username).first()
            if not user:
                flash("Account does not exist")
                return render_template("login.html")
            elif not check_password_hash(user.passhash, password):
                flash("Incorrect password")
                return render_template("login.html")
            else:
                if user.is_admin:
                    session["user_id"] = user.username
                    session["admin"] = True
                    return redirect(url_for("admin_home"))
                else:
                    session["user_id"] = user.username
                    session["admin"] = False
                    return redirect(url_for("home"))

        return render_template("login.html")

    # --- Decorators ---

    def auth_required(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first!")
                return redirect(url_for("login"))
            return func(*args, **kwargs)

        return decorated_function

    def admin_required(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please login first!")
                return redirect(url_for("login"))
            if not session.get("admin", False):
                flash("You're not authorized to access this page!")
                return redirect(url_for("login"))
            return func(*args, **kwargs)

        return decorated_function

    # --- Genral Pages ---

    @app.route("/home")
    @auth_required
    def home():
        if "admin" in session and session["admin"] is True:
            return redirect(url_for("admin_home"))
        else:
            return render_template("home.html")

    @app.route("/profile", methods=["GET", "POST"])
    @auth_required
    def profile():
        if request.method == "POST":
            user = User.query.get(session["user_id"])
            full_name = request.form.get("full_name")
            username = request.form.get("username")
            cpassword = request.form.get("cpassword")
            npassword = request.form.get("password")

            if not full_name or not username:
                full_name = user.fullname
                username = user.username

            if username != user.username:
                user_exist = User.query.filter_by(username=username).first()
                if user_exist:
                    flash("Username already exists")
                    return render_template("profile.html", user=user)

            user.fullname = full_name
            user.username = username

            if npassword and not cpassword:
                flash("Current password is required")
                return render_template("profile.html", user=user)

            if not check_password_hash(user.passhash, cpassword):
                flash("Incorrect password")
                return render_template("profile.html", user=user)

            if npassword:
                passhash = generate_password_hash(npassword)
                user.passhash = passhash

            db.session.commit()

            flash("Profile updated successfully")
            return render_template("profile.html", user=user)

        user = User.query.get(session["user_id"])
        return render_template("profile.html", user=user)

    @app.route("/logout", methods=["GET"])
    @auth_required
    def logout():
        session.pop("user_id", None)
        session.pop("admin", None)
        flash("Successfully logged out")
        return redirect(url_for("index"))

    # --- Admin Pages ---
    
    @app.route("/admin_home")
    @admin_required
    def admin_home():
        if "admin" in session and session["admin"] is True:
            subjects = Subject.query.all()
            return render_template("admin_home.html", subjects=subjects)
        else:
            flash("Access denied")
            return redirect(url_for("home"))

    # Matter related to subjects

    @app.route("/add_subjects", methods=["GET", "POST"])  # TODO: complete this route
    @admin_required
    def add_subjects():
        if request.method == "POST":
            subject_name = request.form.get("subject_name")
            subject_description = request.form.get("subject_description")
            if not subject_name:
                flash("Subject name is required")
                return render_template("add_subjects.html")
            subject = Subject(name=subject_name, description=subject_description)
            db.session.add(subject)
            db.session.commit()
            flash("Subject added successfully")
            return redirect(url_for("admin_home"))
        return render_template("subject/add_subject.html")

    @app.route("/subject/<int:id>/")
    @admin_required
    def show_subject(id):
        return "Show Subject..."

    @app.route("/subject/<int:id>/edit", methods=["GET", "POST"])
    @auth_required
    def edit_subject(id):
        # Fetching to check if subject exists when url is hit
        subject = Subject.query.get(id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))

        # editing subject if form is submitted
        if request.method == "POST":
            subject_name = request.form.get("subject_name")
            subject_description = request.form.get("subject_description")
            if not subject_name:
                flash("Subject name is required")
                return render_template("subject/edit_subject.html", subject=subject)
            subject.name = subject_name
            subject.description = subject_description
            db.session.commit()
            flash("Subject updated successfully")
            return redirect(url_for("admin_home"))
        # rendering edit form
        return render_template("subject/edit_subject.html", subject=subject)

    @app.route("/subject/<int:id>/delete", methods=["GET", "POST"])
    @auth_required
    def delete_subject(id):
        subject = Subject.query.get(id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))
        if request.method == "POST":
            db.session.delete(subject)
            db.session.commit()
            flash("Subject deleted successfully")
            return redirect(url_for("admin_home"))

        return render_template("subject/delete_subject.html", subject=subject)
