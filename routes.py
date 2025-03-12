from flask import render_template

def set_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")