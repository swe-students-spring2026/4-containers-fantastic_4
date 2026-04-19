"""Transcribes audio using the AssemblyAI API."""

import os
import time

import requests

BASE_URL = "https://api.assemblyai.com"
MODEL_NAME = "universal-3-pro"


def build_headers():
    """Build the HTTP headers for AssemblyAI requests."""
    api_key = os.environ.get("ASSEMBLYAI_API_KEY")
    return {"authorization": api_key}


def build_transcript_payload(audio_url):
    """Build the transcript request payload."""
    return {
        "audio_url": audio_url,
        "language_detection": True,
        "speech_models": [MODEL_NAME, "universal-2"],
    }


def build_polling_endpoint(transcript_id):
    """Build the transcript polling URL."""
    return BASE_URL + "/v2/transcript/" + transcript_id


def transcribe_audio(audio_bytes):
    """Transcribe audio bytes provided by another subsystem (for example, the web app)."""
    headers = build_headers()
    upload_response = requests.post(
        BASE_URL + "/v2/upload", headers=headers, data=audio_bytes, timeout=30
    )
    audio_url = upload_response.json()["upload_url"]

    data = build_transcript_payload(audio_url)

    url = BASE_URL + "/v2/transcript"
    response = requests.post(url, json=data, headers=headers, timeout=30)

    transcript_id = response.json()["id"]
    polling_endpoint = build_polling_endpoint(transcript_id)

    while True:
        transcription_result = requests.get(
            polling_endpoint, headers=headers, timeout=30
        ).json()
        transcript_text = transcription_result["text"]

        if transcription_result["status"] == "completed":
            return transcript_text

        if transcription_result["status"] == "error":
            raise RuntimeError(f"Transcription failed: {transcription_result['error']}")

        time.sleep(3)
