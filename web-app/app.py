from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secure-key"

# db setup
# has to be changed after we put this inside a container
client = MongoClient("mongodb://localhost:27017/")
db = client["project4"]
# stores users and passwords
users = db["users"]
# stores results of ml processing
class_notes = db["class_notes"]

# auth setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


# auth routes
@login_manager.user_loader
def load_user(user_id):
    user_data = users.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        return None
    return User(str(user_data["_id"]), user_data["username"])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_data = users.find_one({"username": username})

        if user_data and check_password_hash(user_data["password"], password):
            user_obj = User(str(user_data["_id"]), user_data["username"])
            login_user(user_obj)
            return redirect(url_for("index"))

        flash("Invalid username or password")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if users.find_one({"username": username}):
            flash("That username is already taken")
            return redirect(url_for("register"))

        hashed = generate_password_hash(password)

        users.insert_one({"username": username, "password": hashed})

        flash("Success! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


# route for loading home page and sending audio file to ml client
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        file = request.files.get("audio_file")
        if not file:
            return jsonify({"error": "No audio data received"}), 400

        try:
            files = {"file": (file.filename, file.stream, "audio/wav")}
            payload = {"user_id": current_user.id}

            # sends file to ml client api - won't work for now bc ml client api doesn't exist yet
            ml_response = requests.post(
                # we will need to change this once we put this in a container
                "http://localhost:5001/process",
                files=files,
                data=payload,
                timeout=120,
            )

            return jsonify(ml_response.json()), ml_response.status_code

        except Exception as e:
            return (
                jsonify({"error": f"Error communicating with ML client: {str(e)}"}),
                500,
            )
    # send all past ml results
    notes = list(class_notes.find({"user_id": current_user.id}).sort("timestamp", -1))
    return render_template("index.html", notes=notes)
