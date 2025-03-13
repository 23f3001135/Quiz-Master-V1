import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()
app = Flask(__name__)
# adding config for database and secret key...
try:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default-secret-key")
except Exception as e:
    print("Error loading environment variables:", e)

# creating db
try:
    from models import create_db

    create_db(app)
except Exception as e:
    print("Error initializing database:", e)

# setting routes using set_routes function from routes.py
try:
    from routes import set_routes

    set_routes(app)
except Exception as e:
    print("Error importing routes:", e)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
