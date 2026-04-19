"""Tests for ML client Flask routes."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

with patch("pymongo.MongoClient", MagicMock()):
    from app import app


def get_client():
    """Return a test client with testing enabled."""
    app.config["TESTING"] = True
    return app.test_client()


def test_health():
    """Health endpoint returns ok."""
    response = get_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
