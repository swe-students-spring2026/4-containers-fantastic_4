"""Web app for recording and displaying class notes."""

from datetime import datetime

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

        hashed = generate_password_hash(password)

        users.insert_one({"username": username, "password": hashed})

        flash("Success! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    """Log out the current user."""
    logout_user()
    return redirect(url_for("login"))


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

            # sends file to ml client api - won't work for now bc ml client api doesn't exist yet
            ml_response = requests.post(
                # we will need to change this once we put this in a container
                "http://localhost:5001/process",
                files=files,
                data=payload,
                timeout=120,
            )

            ml_data = ml_response.json()

            result = class_notes.insert_one(
                {
                    "user_id": current_user.id,
                    "transcript": ml_data.get("transcript", ""),
                    "summary": None,
                    "timestamp": datetime.utcnow(),
                }
            )

            ml_data["note_id"] = str(result.inserted_id)

            return jsonify(ml_data), ml_response.status_code

        except requests.exceptions.RequestException as e:
            return (
                jsonify({"error": f"Error communicating with ML client: {str(e)}"}),
                500,
            )
    # send all past ml results
    notes = list(class_notes.find({"user_id": current_user.id}).sort("timestamp", -1))
    return render_template("index.html", notes=notes)


# Generate AI summary
@app.route("/summarize/<note_id>", methods=["POST"])
@login_required
def summarize(note_id):
    """Generate an AI summary for an existing note."""

    note = class_notes.find_one({"_id": ObjectId(note_id), "user_id": current_user.id})

    if not note:
        return jsonify({"error": "Note not found"}), 404

    summary = "placeholder"

    class_notes.update_one({"_id": ObjectId(note_id)}, {"$set": {"summary": summary}})

    return jsonify({"summary": summary})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
