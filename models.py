from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class User(db.Model):
    username = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    fullname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passhash = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    scores = db.relationship("Score", backref="user", lazy=True)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120), default="Not available")

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120), default="Not available")
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id"), nullable=False)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120), default="Not available")
    included_questions = db.relationship("Question", backref="quiz", lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    question = db.Column(db.String(120), nullable=False)
    option1 = db.Column(db.String(120), nullable=False)
    option2 = db.Column(db.String(120), nullable=False)
    option3 = db.Column(db.String(120), nullable=False)
    option4 = db.Column(db.String(120), nullable=False)
    correct_option = db.Column(db.String(120), nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), db.ForeignKey("user.username"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    time_taken = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)

def create_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        # checking if admins already exist if not create one
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            passhash = generate_password_hash("admin")
            new_admin = User(
                fullname="Admin", username="admin", email="admin@example.com", passhash=passhash, is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()