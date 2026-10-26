
from fastapi.testclient import TestClient

from backend.app.main import app
from unittest.mock import patch


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "HR Policy Assistant API"
    assert "timestamp" in data


def test_chat_rejects_empty_question():
    response = client.post(
        "/api/chat",
        json={"question": "   "},
    )

    assert response.status_code == 422


def test_chat_rejects_question_over_2000_characters():
    response = client.post(
        "/api/chat",
        json={"question": "a" * 2001},
    )

    assert response.status_code == 422


def test_chat_rejects_unexpected_fields():
    response = client.post(
        "/api/chat",
        json={
            "question": "How do I apply for leave?",
            "unexpected_field": "value",
        },
    )

    assert response.status_code == 422


@patch("backend.app.api.chat.answer_question")
def test_chat_returns_answer(mock_answer):
    mock_answer.return_value = {
        "answer": "Please consult Section 3.",
        "sources": [],
        "blocked": False,
    }

    response = client.post(
        "/api/chat",
        json={"question": "How do I apply for leave?"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Please consult Section 3."
    mock_answer.assert_called_once()
