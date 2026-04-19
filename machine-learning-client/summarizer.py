"""Summarizes the transcript using Googles API."""

from google import genai

MODEL_NAME = "gemini-3-flash-preview"
SUMMARY_PROMPT = "Summarize the following transcript into concise bullet points, highlighting the key topics and takeaways. Use plain text only, no markdown formatting, no bold, no asterisks:\n"


def build_prompt(transcript):
    """Build the prompt for the Google Gemini APId."""
    return SUMMARY_PROMPT + transcript


def summarize_transcript(transcript):
    """Summarize the transcript using the Google Gemini API."""
    client = genai.Client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=build_prompt(transcript),
    )
    return response.text
