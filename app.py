from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

try:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default-secret-key")
except Exception as e:
    print("Error loading environment variables:", e)

try:
    from models import create_db
    create_db(app)
except Exception as e:
    print("Error initializing database:", e)
    
try:

    from routes import set_routes
    set_routes(app)
except Exception as e:
    print("Error importing routes:", e)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
