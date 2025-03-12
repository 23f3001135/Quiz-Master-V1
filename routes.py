from flask import render_template, request

def set_routes(app):
    @app.route("/")
    def index():
        return render_template("index.html")
    
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            full_name = request.form.get("full_name")
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            if password != confirm_password:
                print("Passwords do not match")
                return render_template("signup.html")
            print(full_name, username, email, password, confirm_password)
        
        return render_template("signup.html")
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            print(email, password)
        
        return render_template("login.html")
    
    @app.route("/home")
    def home():
        return render_template("home.html")