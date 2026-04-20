"""Summarizes the transcript using Googles API."""

from google import genai
from google.genai import errors as genai_errors

MODELS = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash-preview-04-17",
    "gemini-2.5-pro-preview-03-25",
    "gemini-2.0-flash",
]
SUMMARY_PROMPT = "Summarize the following transcript into concise bullet points, highlighting the key topics and takeaways. Use plain text only, no markdown formatting, no bold, no asterisks:\n"


def build_prompt(transcript):
    """Build the prompt for the Google Gemini APId."""
    return SUMMARY_PROMPT + transcript


def summarize_transcript(transcript):
    """Summarize the transcript using the Google Gemini API, with model fallback."""
    client = genai.Client()
    last_error = None
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=build_prompt(transcript),
            )
            print(f"Summarized using model: {model}", flush=True)
            return response.text
        except genai_errors.ServerError as e:
            last_error = e
            continue
    raise RuntimeError(
        "All Gemini models are unavailable. Please try again later."
    ) from last_error
