from app import app
from dotenv import load_dotenv
import os


try:
    load_dotenv()
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    )
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

except Exception as e:
    print("Error loading environment variables:", e)