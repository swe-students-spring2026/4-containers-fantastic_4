"""Transcribes audio using the AssemblyAI API."""

import os
import time
import requests

BASE_URL = "https://api.assemblyai.com"

headers = {"authorization": os.environ.get("ASSEMBLYAI_API_KEY")}


def transcribe_audio(audio_bytes):
    """Upload audio bytes to AssemblyAI and return the transcript text."""
    upload_response = requests.post(
        BASE_URL + "/v2/upload", headers=headers, data=audio_bytes, timeout=30
    )
    audio_url = upload_response.json()["upload_url"]

    data = {
        "audio_url": audio_url,
        "language_detection": True,
        "speech_models": ["universal-3-pro", "universal-2"],
    }

    url = BASE_URL + "/v2/transcript"
    response = requests.post(url, json=data, headers=headers, timeout=30)

    transcript_id = response.json()["id"]
    polling_endpoint = BASE_URL + "/v2/transcript/" + transcript_id

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
