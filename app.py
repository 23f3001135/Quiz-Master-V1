from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__) # creating instance of flask

import config # importing configs from .env etc
import models # importing models like User, Post etc
import routes # importing routes like index, login, register etc




if __name__ == "__main__":
    app.run(debug=True, port=5000) # running the app on port 5000
