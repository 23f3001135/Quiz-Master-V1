from flask import flash, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models import Chapter, Question, Quiz, Score, Subject, User, db


def set_routes(app):
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
            email = request.form.get("email")
            password = request.form.get("password")
            if not email or not password:
                flash("Email and password are required")
                return render_template("login.html")
            user = User.query.filter_by(email=email).first()
            if not user:
                flash("Account does not exist")
                return render_template("login.html")
            elif not check_password_hash(user.passhash, password):
                flash("Incorrect password")
                return render_template("login.html")
            else:
                return redirect(url_for("home"))

        return render_template("login.html")

    @app.route("/home")
    def home():
        return render_template("home.html")

    @app.route("/adminlogin", methods=["GET", "POST"])
    def adminlogin():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            if not email or not password:  # checking if email and password are provided
                flash("Email and password are required")
                return render_template("adminlogin.html")

            user = User.query.filter_by(
                email=email
            ).first()  # checking if user exists - part 1

            if not user:  # checking if user exists - part 2
                flash("Account does not exist")
                return render_template("adminlogin.html")
            elif not check_password_hash(
                user.passhash, password
            ):  # checking if password is correct
                flash("Incorrect password")
                return render_template("adminlogin.html")
            elif not user.is_admin:  # checking if user is admin
                flash("You are not authorized to access this page")
                return render_template("adminlogin.html")
            else:
                return redirect(url_for("admin_home"))

        return render_template("adminlogin.html")

    @app.route("/admin_home")
    def admin_home():
        return render_template("admin_home.html")
