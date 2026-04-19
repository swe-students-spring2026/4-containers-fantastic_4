"""ML client API for processing audio and storing results."""

from datetime import datetime
import os

from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pymongo import MongoClient

from transcriber import transcribe_audio
from summarizer import summarize_transcript

app = Flask(__name__)

# Environment variables from machine-learning-client/.env
load_dotenv()
MONGO_URI = os.environ.get("MONGO_URI") or os.environ.get(
    "MONGODB_URI", "mongodb://localhost:27017/"
)
client = MongoClient(MONGO_URI)
db = client["fantastic4"]
class_notes = db["class_notes"]


@app.route("/health", methods=["GET"])
def health():
    """Basic health endpoint for service readiness checks."""
    return jsonify({"status": "ok"}), 200


@app.route("/generate", methods=["POST"])
def generate():
    """Receive audio, transcribe, summarize, and save to database."""
    file = request.files.get("file")
    user_id = request.form.get("user_id")

    if not file:
        return jsonify({"error": "No audio file received"}), 400

    audio_bytes = file.read()
    transcript = transcribe_audio(audio_bytes)
    summary = summarize_transcript(transcript)

    result = class_notes.insert_one(
        {
            "user_id": user_id,
            "transcript": transcript,
            "summary": summary,
            "timestamp": datetime.utcnow(),
        }
    )

    return jsonify(
        {
            "transcript": transcript,
            "summary": summary,
            "note_id": str(result.inserted_id),
        }
    )


@app.route("/process", methods=["POST"])
def process():
    """Alias for the original ML processing endpoint."""
    return generate()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
