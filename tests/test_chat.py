
from unittest.mock import patch

import pytest
from langchain_core.documents import Document

from backend.app.services.chat_service import answer_question
from backend.app.services.privacy_service import PRIVACY_REFUSAL


@patch("backend.app.services.chat_service.retrieve_policy_chunks")
def test_returns_fallback_when_no_policy_evidence(mock_retrieve):
    mock_retrieve.return_value = []

    result = answer_question("What is the company's leave policy?")

    assert result.answer == "I don't know, please contact HR."
    assert result.sources == []
    mock_retrieve.assert_called_once()


@patch("backend.app.services.chat_service.generate_answer")
@patch("backend.app.services.chat_service.retrieve_policy_chunks")
def test_generates_answer_when_policy_evidence_exists(
    mock_retrieve,
    mock_generate,
):
    mock_retrieve.return_value = [
        type(
            "RetrievedChunk",
            (),
            {
                "document": Document(
                    page_content="Employees may apply for leave.",
                    metadata={
                        "policy_id": "leave-policy",
                        "policy_title": "Company Leave Policy",
                        "policy_version": "2.0",
                        "section_number": "3",
                        "section_heading": "Leave Applications",
                    },
                ),
                "score": 0.85,
            },
        )()
    ]
    mock_generate.return_value = (
        "Employees may apply for leave under Section 3."
    )

    result = answer_question("How do I apply for leave?")

    assert "Section 3" in result.answer
    assert len(result.sources) == 1
    assert result.sources[0].section_heading == "Leave Applications"
    mock_generate.assert_called_once()


@patch("backend.app.services.chat_service.generate_answer")
@patch("backend.app.services.chat_service.retrieve_policy_chunks")
def test_preserves_exact_fallback_from_llm(
    mock_retrieve,
    mock_generate,
):
    mock_retrieve.return_value = [
        type(
            "RetrievedChunk",
            (),
            {
                "document": Document(
                    page_content="A policy passage.",
                    metadata={
                        "policy_id": "leave-policy",
                        "policy_title": "Company Leave Policy",
                        "policy_version": "2.0",
                        "section_number": "1",
                        "section_heading": "Introduction",
                    },
                ),
                "score": 0.85,
            },
        )()
    ]
    mock_generate.return_value = "I don't know, please contact HR."

    result = answer_question("A question not answered by the policy")

    assert result.answer == "I don't know, please contact HR."
