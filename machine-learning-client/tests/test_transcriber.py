"""Tests for transcriber.py"""

from unittest.mock import MagicMock, patch

import pytest
import transcriber


def make_mock_response(json_data):
    """Return a fake HTTP response."""
    mock = MagicMock()
    mock.json.return_value = json_data
    return mock


def test_build_transcript_payload_uses_universal_3_pro():
    """Test that the AssemblyAI payload uses the expected model."""
    payload = transcriber.build_transcript_payload("https://fake-url.com")

    assert payload == {
        "audio_url": "https://fake-url.com",
        "language_detection": True,
        "speech_models": ["universal-3-pro"],
    }


def test_build_polling_endpoint_uses_transcript_id():
    """Test that the polling endpoint is built from the transcript ID."""
    endpoint = transcriber.build_polling_endpoint("abc123")

    assert endpoint == "https://api.assemblyai.com/v2/transcript/abc123"


@patch("transcriber.requests.get")
@patch("transcriber.requests.post")
def test_transcriber_completed(mock_post, mock_get):
    """Test that transcribe_audio returns the transcript text when status is completed."""
    mock_post.side_effect = [
        make_mock_response({"upload_url": "https://fake-url.com"}),
        make_mock_response({"id": "abc123"}),
    ]
    mock_get.return_value = make_mock_response(
        {"status": "completed", "text": "hello world"}
    )

    result = transcriber.transcribe_audio(b"fake audio")

    assert result == "hello world"


@patch("transcriber.requests.get")
@patch("transcriber.requests.post")
def test_transcriber_error(mock_post, mock_get):
    """Test that transcribe_audio raises an error when status is error."""
    mock_post.side_effect = [
        make_mock_response({"upload_url": "https://fake-url.com"}),
        make_mock_response({"id": "abc123"}),
    ]
    mock_get.return_value = make_mock_response(
        {"status": "error", "text": None, "error": "bad audio"}
    )

    with pytest.raises(RuntimeError, match="Transcription failed: bad audio"):
        transcriber.transcribe_audio(b"fake audio")


@patch("transcriber.time.sleep", return_value=None)
@patch("transcriber.requests.get")
@patch("transcriber.requests.post")
def test_transcriber_processing(mock_post, mock_get, mock_sleep):
    """Test that transcribe_audio keeps polling until the status is completed."""
    mock_post.side_effect = [
        make_mock_response({"upload_url": "https://fake-url.com"}),
        make_mock_response({"id": "abc123"}),
    ]
    mock_get.side_effect = [
        make_mock_response({"status": "processing", "text": None}),
        make_mock_response({"status": "completed", "text": "final transcript"}),
    ]

    result = transcriber.transcribe_audio(b"fake audio")

    assert result == "final transcript"
    assert mock_sleep.call_count == 1
