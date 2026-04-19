"""Web app for recording and displaying class notes."""

from datetime import datetime
import os

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
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")

app.config["SECRET_KEY"] = SECRET_KEY
ML_CLIENT_URL = os.environ.get("ML_CLIENT_URL", "http://localhost:5001")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

# db setup
# has to be changed after we put this inside a container
client = MongoClient(MONGO_URI)
db = client["fantastic4"]
# stores users and passwords
users = db["users"]
# stores results of ml processing
class_notes = db["class_notes"]

# auth setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    """Represents an authenticated user."""

    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username


# auth routes
@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database by their ID."""
    user_data = users.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        return None
    return User(str(user_data["_id"]), user_data["username"])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
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
    """Handle new user registration."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if users.find_one({"username": username}):
            flash("That username is already taken")
            return redirect(url_for("register"))

        hashed = generate_password_hash(password, method='pbkdf2:sha256')

        users.insert_one({"username": username, "password": hashed})

        flash("Success! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Log out the current user."""
    logout_user()
    return redirect(url_for("login"))


@app.route("/favicon.ico")
def favicon():
    """Return an empty success response for browser favicon requests."""
    return "", 204


# route for loading home page and sending audio file to ml client
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Home Page"""
    if request.method == "POST":
        file = request.files.get("audio_file")
        if not file:
            return jsonify({"error": "No audio data received"}), 400

        try:
            files = {"file": (file.filename, file.stream, "audio/wav")}
            payload = {"user_id": current_user.id}

            # Send recorded audio to ML client for transcription and summary
            ml_response = requests.post(
                f"{ML_CLIENT_URL}/generate",
                files=files,
                data=payload,
                timeout=120,
            )
            try:
                ml_data = ml_response.json()
            except ValueError:
                return jsonify({"error": "ML client returned invalid JSON"}), 502

            return jsonify(ml_data), ml_response.status_code

        except requests.exceptions.RequestException as e:
            return (
                jsonify({"error": f"Error communicating with ML client: {str(e)}"}),
                500,
            )
    # send all past ml results
    notes = list(class_notes.find({"user_id": current_user.id}).sort("timestamp", -1))
    return render_template("index.html", notes=notes)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
