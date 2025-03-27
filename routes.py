from datetime import datetime, timedelta
from functools import wraps

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models import Chapter, Question, Quiz, Score, Subject, User, db


def set_routes(app):
    # --- Utility Functions ---
    @app.context_processor
    def utility_processor():
        def now():
            return datetime.now()

        return dict(now=now, timedelta=timedelta)

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

    # --- Authentication Routes ---

    @app.route("/", methods=["GET"])  # Landing page
    def index():
        return render_template("index.html")

    @app.route("/signup", methods=["GET", "POST"])  # Signup page
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

    # --- Genral Pages ---

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

    @app.route("/search", methods=["GET", "POST"])
    @auth_required
    def search():
        if request.method == "POST":
            query = request.form.get("query", "")
            entity_type = request.form.get("entity_type", "")

            if not query or not entity_type:
                flash("Please provide a search term and select what to search for")
                return redirect(url_for("search"))

            # Convert the query to a SQL LIKE pattern with wildcards
            search_term = f"%{query}%"
            results = []

            # --- Admin searches ---

            if session.get("admin", False):  # checking if user is admin
                # searching for user
                if entity_type == "users":
                    results = User.query.filter(
                        db.or_(
                            User.username.like(search_term),
                            User.fullname.like(search_term),
                            User.email.like(search_term),
                        )
                    ).all()

                # searching for subjects
                elif entity_type == "subjects":
                    results = Subject.query.filter(
                        db.or_(
                            Subject.name.like(search_term),
                            Subject.description.like(search_term),
                        )
                    ).all()

                # searching for quizzes
                elif entity_type == "quizzes":
                    results = Quiz.query.filter(
                        db.or_(
                            Quiz.name.like(search_term),
                            Quiz.description.like(search_term),
                        )
                    ).all()

                # searching for questions
                elif entity_type == "questions":
                    results = Question.query.filter(
                        db.or_(
                            Question.question.like(search_term),
                            Question.option1.like(search_term),
                            Question.option2.like(search_term),
                            Question.option3.like(search_term),
                            Question.option4.like(search_term),
                        )
                    ).all()

            # --- User searches ---
            else:
                entity_type = "quizzes"  # Always set to quizzes for users
                
                # First, find quizzes that directly match the search term
                direct_matches = Quiz.query.filter(
                    db.or_(
                        Quiz.name.like(search_term),
                        Quiz.description.like(search_term),
                    )
                ).all()
                
                # Next, find subjects that match the search term
                subject_matches = Subject.query.filter(
                    db.or_(
                        Subject.name.like(search_term),
                        Subject.description.like(search_term),
                    )
                ).all()
                
                # Get quizzes from those subjects
                related_quizzes = []
                for subject in subject_matches:
                    for chapter in subject.chapters:
                        for quiz in chapter.quizzes:
                            if quiz not in direct_matches and quiz not in related_quizzes:
                                related_quizzes.append(quiz)
                
                # Combine direct matches with related quizzes
                results = direct_matches + related_quizzes

            # Render results template based on user role
            if session.get("admin", False):
                return render_template(
                    "search_results.html",
                    results=results,
                    entity_type=entity_type,
                    query=query,
                )
            else:
                return render_template(
                    "user_dashboard/search_results.html",
                    results=results,
                    entity_type=entity_type,
                    query=query,
                )

        # Display search form
        is_admin = session.get("admin", False)
        return render_template("search.html", is_admin=is_admin)


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

    @app.route("/users")
    @admin_required
    def manage_users():
        users = User.query.all()
        return render_template("manage_users.html", users=users)

    # Matter related to subjects

    @app.route("/add_subjects", methods=["GET", "POST"])
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

    @app.route("/subject/<int:id>/", methods=["GET", "POST"])
    @admin_required
    def show_subject(id):
        subject = Subject.query.get(id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))
        if request.method == "POST":
            chapter_name = request.form.get("chapter_name")
            chapter_description = request.form.get("chapter_description")
            if not chapter_name:
                flash("Chapter name is required")
                return render_template("subject/show_subject.html", subject=subject)
            chapter = Chapter(
                name=chapter_name, description=chapter_description, subject_id=id
            )
            db.session.add(chapter)
            db.session.commit()
            flash("Chapter added successfully")
            return redirect(url_for("show_subject", id=id))
        return render_template("subject/show_subject.html", subject=subject)

    @app.route("/subject/<int:id>/edit", methods=["GET", "POST"])
    @admin_required
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

    # Matter related to Chapters

    @app.route("/add_chapter/<int:subject_id>", methods=["GET", "POST"])
    @admin_required
    def add_chapter(subject_id):
        # check if subject exists
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))

        # when form is summited
        if request.method == "POST":
            chapter_name = request.form.get("chapter_name")
            chapter_description = request.form.get("chapter_description")
            if not chapter_name:
                flash("Chapter name is required")
                return render_template("subject/show_subject.html")
            # checking if chapter already exsist in the subject
            chapter = Chapter.query.filter_by(
                name=chapter_name, subject_id=subject_id
            ).first()
            if chapter:
                flash("Chapter already exists")
                return render_template("subject/show_subject.html", subject=subject)
            chapter = Chapter(
                name=chapter_name,
                description=chapter_description,
                subject_id=subject_id,
            )
            db.session.add(chapter)
            db.session.commit()
            flash("Chapter added successfully")
            return redirect(url_for("show_subject", id=subject_id))
        return render_template("chapter/add_chapter.html")

    @app.route("/chapter/<int:subject_id>/<int:chapter_id>", methods=["GET", "POST"])
    @admin_required
    def show_chapter(subject_id, chapter_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("show_subject", id=subject_id))
        if request.method == "POST":
            chapter_name = request.form.get("chapter_name")
            chapter_description = request.form.get("chapter_description")
            if not chapter_name:
                flash("Chapter name is required")
                return render_template("subject/show_subject.html", subject=subject)
            chapter.name = chapter_name
            chapter.description = chapter_description
            db.session.commit()
            flash("Chapter added successfully")
            return redirect(url_for("show_subject", id=id))
        return render_template(
            "chapter/show_chapter.html", subject=subject, chapter=chapter
        )

    @app.route(
        "/chapter/<int:subject_id>/<int:chapter_id>/edit", methods=["GET", "POST"]
    )
    @auth_required
    def edit_chapter(subject_id, chapter_id):
        # Fetching to check if subject exists when url is hit
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))

        # editing chapter if form is submitted
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("show_subject", id=subject_id))

        if request.method == "POST":
            chapter_name = request.form.get("chapter_name")
            chapter_description = request.form.get("chapter_description")
            if not chapter_name:
                flash("Chapter name is required")
                return render_template("subject/show_subject.html", subject=subject)
            chapter.name = chapter_name
            chapter.description = chapter_description
            db.session.commit()
            flash("Chapter updated successfully")
            return redirect(url_for("show_subject", id=subject_id))
        # rendering edit form
        return render_template(
            "chapter/edit_chapter.html", subject=subject, chapter=chapter
        )

    @app.route(
        "/chapter/<int:subject_id>/<int:chapter_id>/delete", methods=["GET", "POST"]
    )
    @auth_required
    def delete_chapter(subject_id, chapter_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("show_subject", id=subject_id))
        if request.method == "POST":
            db.session.delete(chapter)
            db.session.commit()
            flash("Chapter deleted successfully")
            return redirect(url_for("show_subject", id=subject_id))

        return render_template(
            "chapter/delete_chapter.html", subject=subject, chapter=chapter
        )

    # ------------------------------
    # Matter related to Quizzes
    # ------------------------------

    @app.route("/add_quiz/<int:subject_id>/<int:chapter_id>", methods=["GET", "POST"])
    @admin_required
    def add_quiz(subject_id, chapter_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("admin_home"))

        if request.method == "POST":
            name = request.form.get("quiz_name")
            description = request.form.get("quiz_description")
            quiz_date_time_str = request.form.get("quiz_date_time")
            quiz_duration_str = request.form.get("quiz_duration")
            if not name:
                flash("Quiz name is required")
                return render_template("subject/show_subject.html", subject=subject)
            quiz = Quiz.query.filter_by(name=name, chapter_id=chapter_id).first()
            if quiz:
                flash("Quiz already exists")
                return render_template("subject/show_subject.html", subject=subject)

            try:
                quiz_schedule_date = datetime.strptime(
                    quiz_date_time_str, "%Y-%m-%dT%H:%M"
                )
            except ValueError:
                flash("Invalid date/time format")
                return render_template(
                    "quiz/add_quiz.html", subject=subject, chapter=chapter
                )

            try:
                quiz_duration = int(quiz_duration_str)
            except ValueError:
                flash("Invalid duration format. Please enter a number.")
                return render_template(
                    "quiz/add_quiz.html", subject=subject, chapter=chapter
                )

            quiz = Quiz(
                name=name,
                description=description,
                chapter_id=chapter_id,
                quiz_schedule_date=quiz_schedule_date,
                quiz_duration=quiz_duration,
            )
            db.session.add(quiz)
            db.session.commit()
            flash("Quiz added successfully")
            return redirect(url_for("show_subject", id=subject_id))
        return render_template("quiz/add_quiz.html", subject=subject, chapter=chapter)

    @app.route(
        "/quiz/<int:subject_id>/<int:chapter_id>/<int:quiz_id>", methods=["GET", "POST"]
    )
    @admin_required
    def show_quiz(subject_id, chapter_id, quiz_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("admin_home"))
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Quiz not found")
            return redirect(url_for("admin_home"))
        if request.method == "POST":
            quiz_name = request.form.get("quiz_name")
            quiz_description = request.form.get("quiz_description")
            if not quiz_name:
                flash("Quiz name is required")
                return render_template("subject/show_subject.html", subject=subject)
            quiz.name = quiz_name
            quiz.description = quiz_description
            db.session.commit()
            flash("Chapter added successfully")
            return redirect(url_for("show_subject", id=id))
        return render_template(
            "quiz/show_quiz.html", subject=subject, chapter=chapter, quiz=quiz
        )

    @app.route(
        "/quiz/<int:subject_id>/<int:chapter_id>/<int:quiz_id>/edit",
        methods=["GET", "POST"],
    )
    @auth_required
    def edit_quiz(subject_id, chapter_id, quiz_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))

        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("show_subject", id=subject_id))

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Quiz not found")
            return redirect(url_for("show_subject", id=subject_id))

        if request.method == "POST":
            quiz_name = request.form.get("quiz_name")
            quiz_description = request.form.get("quiz_description")
            quiz_date_time_str = request.form.get("quiz_date_time")
            quiz_duration_str = request.form.get("quiz_duration")

            if not quiz_name:
                flash("Quiz name is required")
                return render_template("subject/show_subject.html", subject=subject)

            try:
                quiz_schedule_date = datetime.strptime(
                    quiz_date_time_str, "%Y-%m-%dT%H:%M"
                )
            except ValueError:
                flash("Invalid date/time format")
                return render_template(
                    "quiz/edit_quiz.html", subject=subject, chapter=chapter, quiz=quiz
                )

            try:
                quiz_duration = int(quiz_duration_str)
            except ValueError:
                flash("Invalid duration. Please enter a number.")
                return render_template(
                    "quiz/edit_quiz.html", subject=subject, chapter=chapter, quiz=quiz
                )

            quiz.name = quiz_name
            quiz.description = quiz_description
            quiz.quiz_schedule_date = quiz_schedule_date
            quiz.quiz_duration = quiz_duration

            db.session.commit()
            flash("Quiz updated successfully")
            return redirect(
                url_for("show_chapter", subject_id=subject_id, chapter_id=chapter_id)
            )
        return render_template(
            "quiz/edit_quiz.html", subject=subject, chapter=chapter, quiz=quiz
        )

    @app.route(
        "/quiz/<int:subject_id>/<int:chapter_id>/<int:quiz_id>/delete",
        methods=["GET", "POST"],
    )
    @auth_required
    def delete_quiz(subject_id, chapter_id, quiz_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("show_subject", id=subject_id))
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Quiz not found")
            return redirect(url_for("show_subject", id=subject_id))
        if request.method == "POST":
            db.session.delete(quiz)
            db.session.commit()
            flash("Quiz deleted successfully")
            return redirect(url_for("show_subject", id=subject_id))

        return render_template(
            "quiz/delete_quiz.html", subject=subject, chapter=chapter, quiz=quiz
        )

    # ------------------------------
    # Matter related to Questions
    # ------------------------------

    @app.route(
        "/question/<int:subject_id>/<int:chapter_id>/<int:quiz_id>/add",
        methods=["GET", "POST"],
    )
    @admin_required
    def add_question(subject_id, chapter_id, quiz_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("show_subject", id=subject_id))
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Quiz not found")
            return redirect(url_for("show_subject", id=subject_id))

        if request.method == "POST":
            question_text = request.form.get("question")
            option1 = request.form.get("option1")
            option2 = request.form.get("option2")
            option3 = request.form.get("option3")
            option4 = request.form.get("option4")
            correct_option_key = request.form.get("correct_option")

            if (
                not question_text
                or not option1
                or not option2
                or not option3
                or not option4
                or not correct_option_key
            ):
                flash("All fields are required")
                return render_template(
                    "question/add_question.html",
                    subject=subject,
                    chapter=chapter,
                    quiz=quiz,
                )

            if correct_option_key not in ["option1", "option2", "option3", "option4"]:
                flash("Correct option must be one of the options")
                return render_template(
                    "question/add_question.html",
                    subject=subject,
                    chapter=chapter,
                    quiz=quiz,
                )

            # Map the correct option key to the actual text value.
            if correct_option_key == "option1":
                correct_text = option1
            elif correct_option_key == "option2":
                correct_text = option2
            elif correct_option_key == "option3":
                correct_text = option3
            elif correct_option_key == "option4":
                correct_text = option4

            new_question = Question(
                question=question_text,
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4,
                correct_option=correct_text,
                quiz_id=quiz_id,
            )
            db.session.add(new_question)
            db.session.commit()
            flash("Question added successfully")
            return redirect(
                url_for(
                    "show_quiz",
                    subject_id=subject_id,
                    chapter_id=chapter_id,
                    quiz_id=quiz_id,
                )
            )

        return render_template(
            "question/add_question.html", subject=subject, chapter=chapter, quiz=quiz
        )

    @app.route(
        "/question/<int:subject_id>/<int:chapter_id>/<int:quiz_id>/<int:question_id>/edit",
        methods=["GET", "POST"],
    )
    @auth_required
    def edit_question(subject_id, chapter_id, quiz_id, question_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))

        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("show_subject", id=subject_id))

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Quiz not found")
            return redirect(url_for("show_subject", id=subject_id))

        question_obj = Question.query.get(question_id)
        if not question_obj:
            flash("Question not found")
            return redirect(url_for("admin_home"))

        if request.method == "POST":
            question_text = request.form.get("question")
            option1 = request.form.get("option1")
            option2 = request.form.get("option2")
            option3 = request.form.get("option3")
            option4 = request.form.get("option4")
            correct_option_key = request.form.get("correct_option")

            if (
                not question_text
                or not option1
                or not option2
                or not option3
                or not option4
                or not correct_option_key
            ):
                flash("All fields are required")
                return render_template(
                    "question/edit_question.html",
                    subject=subject,
                    chapter=chapter,
                    quiz=quiz,
                    question=question_obj,
                )

            if correct_option_key not in ["option1", "option2", "option3", "option4"]:
                flash("Correct option must be one of the options")
                return render_template(
                    "question/edit_question.html",
                    subject=subject,
                    chapter=chapter,
                    quiz=quiz,
                    question=question_obj,
                )

            if correct_option_key == "option1":
                correct_text = option1
            elif correct_option_key == "option2":
                correct_text = option2
            elif correct_option_key == "option3":
                correct_text = option3
            elif correct_option_key == "option4":
                correct_text = option4

            # Update the existing question object.
            question_obj.question = question_text
            question_obj.option1 = option1
            question_obj.option2 = option2
            question_obj.option3 = option3
            question_obj.option4 = option4
            question_obj.correct_option = correct_text

            db.session.commit()
            flash("Question updated successfully")
            return redirect(
                url_for(
                    "show_quiz",
                    subject_id=subject_id,
                    chapter_id=chapter_id,
                    quiz_id=quiz_id,
                )
            )

        return render_template(
            "question/edit_question.html",
            subject=subject,
            chapter=chapter,
            quiz=quiz,
            question=question_obj,
        )

    @app.route(
        "/question/<int:subject_id>/<int:chapter_id>/<int:quiz_id>/<int:question_id>",
        methods=["GET", "POST"],
    )
    @admin_required
    def show_question(subject_id, chapter_id, quiz_id, question_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("admin_home"))
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Quiz not found")
            return redirect(url_for("admin_home"))
        question = Question.query.get(question_id)
        if not question:
            flash("Question not found")
            return redirect(url_for("admin_home"))
        return render_template(
            "question/show_question.html",
            subject=subject,
            chapter=chapter,
            quiz=quiz,
            question=question,
        )

    @app.route(
        "/question/<int:subject_id>/<int:chapter_id>/<int:quiz_id>/<int:question_id>/delete",
        methods=["GET", "POST"],
    )
    @auth_required
    def delete_question(subject_id, chapter_id, quiz_id, question_id):
        subject = Subject.query.get(subject_id)
        if not subject:
            flash("Subject not found")
            return redirect(url_for("admin_home"))
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            flash("Chapter not found")
            return redirect(url_for("show_subject", id=subject_id))
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Quiz not found")
            return redirect(url_for("show_subject", id=subject_id))
        question = Question.query.get(question_id)
        if not question:
            flash("Question doesn't exist")
            return redirect(url_for("show_subject", id=subject_id))
        if request.method == "POST":
            db.session.delete(question)
            db.session.commit()
            flash("Question deleted successfully")
            return redirect(url_for("show_subject", id=subject_id))

        return render_template(
            "question/delete_question.html",
            subject=subject,
            chapter=chapter,
            quiz=quiz,
            question=question,
        )

    # --------------------------------
    # Matter related to User Dashboard
    # --------------------------------

    # non-admin user home

    @app.route("/home")
    @auth_required
    def home():
        if "admin" in session and session["admin"] is True:
            return redirect(url_for("admin_home"))
        else:
            subject = Subject.query.all()
            user = User.query.get(session["user_id"])
            recent_quizzes = (
                Quiz.query.order_by(Quiz.quiz_schedule_date.asc()).limit(5).all()
            )
            # popping any old quiz response when user is being redirected from quiz feedback page...
            if "quiz_responses" in session:
                session.pop("quiz_responses")

            return render_template(
                "user_dashboard/home.html",
                subject=subject,
                user=user,
                recent_quizzes=recent_quizzes,
            )

    # start quiz button
    @app.route("/start_quiz/<int:quiz_id>", methods=["GET", "POST"])
    @auth_required
    def start_quiz(quiz_id):
        quiz = Quiz.query.get(quiz_id)

        if not quiz:
            flash("Quiz not found")
            return redirect(url_for("home"))

        # calculate the start and end time of the quiz
        current_time = datetime.now()
        start_time = quiz.quiz_schedule_date
        end_time = quiz.quiz_schedule_date + timedelta(minutes=quiz.quiz_duration)

        # check if quiz has not yet started
        if current_time < start_time:
            remaining_time = start_time - current_time
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            flash(
                f"This quiz is not yet available. It starts in {hours} hours and {minutes} minutes."
            )
            return redirect(url_for("home"))

        # check if quiz has already ended
        if current_time > end_time:
            flash("This quiz has ended and is no longer available.")
            return redirect(url_for("home"))

        # fetch all questions for the quiz
        questions = Question.query.filter_by(quiz_id=quiz_id).all()

        if request.method == "POST":
            # calculating the score
            score = 0
            user_responses = {}

            # checking the selected option
            for question in questions:
                question_id = question.id
                selected_option_key = request.form.get(f"question{question_id}")

                user_responses[question_id] = selected_option_key

                selected_option_value = None
                if selected_option_key == "option1":
                    selected_option_value = question.option1
                elif selected_option_key == "option2":
                    selected_option_value = question.option2
                elif selected_option_key == "option3":
                    selected_option_value = question.option3
                elif selected_option_key == "option4":
                    selected_option_value = question.option4

                # for each correct answer giving +1 score
                if selected_option_value == question.correct_option:
                    score += 1

            # storing responses in session for the feedback page
            session["quiz_responses"] = user_responses

            # storing score to the database
            user_username = session.get("user_id")
            user_score = Score(user_id=user_username, quiz_id=quiz_id, score=score)
            db.session.add(user_score)
            db.session.commit()

            # redirecting to feedback page...
            return redirect(
                url_for("quiz_feedback", quiz_id=quiz_id, score_id=user_score.id)
            )

        return render_template(
            "user_dashboard/start_quiz.html", quiz=quiz, questions=questions
        )

    @app.route("/quiz_feedback/<int:quiz_id>/<int:score_id>", methods=["GET"])
    @auth_required
    def quiz_feedback(quiz_id, score_id):
        """Display detailed feedback for a quiz attempt with correct answers"""
        user_id = session.get("user_id")
        score = Score.query.get(score_id)

        # an attempt to make sure that user only sees their own results (Security check)
        if not score or score.user_id != user_id:
            flash("Score record not found")
            return redirect(url_for("quiz_results"))

        # checking if quiz exists or not (Security check)
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            flash("Quiz not found")
            return redirect(url_for("home"))

        # fetch all questions and responses for the quiz
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        total_questions = len(questions)
        percentage = (score.score / total_questions * 100) if total_questions > 0 else 0

        # fetch user responses from session (which we stored during quiz submission)
        user_responses = session.get("quiz_responses", {})

        return render_template(
            "user_dashboard/quiz_feedback.html",
            quiz=quiz,
            score=score,
            questions=questions,
            user_responses=user_responses,
            total_questions=total_questions,
            percentage=percentage,
        )

    @app.route("/quiz_results", methods=["GET"])
    @auth_required
    def quiz_results():
        """Display all quiz attempts for the current user"""
        user_id = session.get("user_id")
        scores = Score.query.filter_by(user_id=user_id).all()

        # grouping scores by quiz
        quiz_results = {}
        for score in scores:
            quiz = Quiz.query.get(score.quiz_id)
            if quiz:
                if quiz.id not in quiz_results:
                    quiz_results[quiz.id] = {
                        "quiz_name": quiz.name,
                        "attempts": 0,
                        "highest_score": 0,
                        "scores": [],
                    }

                quiz_results[quiz.id]["attempts"] += 1
                quiz_results[quiz.id]["highest_score"] = max(
                    quiz_results[quiz.id]["highest_score"], score.score
                )
                quiz_results[quiz.id]["scores"].append(
                    {
                        "score": score.score,
                        "total": len(quiz.included_questions),
                        "percentage": (score.score / len(quiz.included_questions) * 100)
                        if len(quiz.included_questions) > 0
                        else 0,
                        "date": score.id,  # Use this as a timestamp proxy since Score doesn't have a timestamp field
                    }
                )
        # popping any old quiz resonse when user is being redirected from quiz feedback page...
        if "quiz_responses" in session:
            session.pop("quiz_responses")
        return render_template(
            "user_dashboard/quiz_results.html", quiz_results=quiz_results
        )
