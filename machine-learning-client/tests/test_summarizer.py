"""Tests for summarizer.py"""

from unittest.mock import MagicMock, patch

import summarizer


def test_build_prompt_includes_transcript():
    """Test that the prompt includes the transcript."""
    prompt = summarizer.build_prompt("some transcript")

    assert "some transcript" in prompt
    assert prompt.startswith("Summarize the following transcript")


def test_build_prompt_includes_summary_prompt():
    """Test that the SUMMARY_PROMPT is appended to the transcript."""
    prompt = summarizer.build_prompt("some transcript")

    assert prompt == summarizer.SUMMARY_PROMPT + "some transcript"


@patch("summarizer.genai.Client")
def test_summarize_transcript_returns_text(mock_client_class):
    """Test that summarize_transcript returns the model's response text."""
    mock_response = MagicMock()
    mock_response.text = "- Key point one\n- Key point two"
    mock_client = mock_client_class.return_value
    mock_client.models.generate_content.return_value = mock_response

    result = summarizer.summarize_transcript("some transcript")

    assert result == "- Key point one\n- Key point two"


@patch("summarizer.genai.Client")
def test_summarize_transcript_uses_correct_model(mock_client_class):
    """Test that the correct model is used."""
    mock_response = MagicMock()
    mock_response.text = "summary"
    mock_client = mock_client_class.return_value
    mock_client.models.generate_content.return_value = mock_response

    summarizer.summarize_transcript("some transcript")

    mock_client.models.generate_content.assert_called_once_with(
        model="gemini-3-flash-preview",
        contents=summarizer.build_prompt("some transcript"),
    )
