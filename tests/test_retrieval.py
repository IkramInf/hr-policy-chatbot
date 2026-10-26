
from unittest.mock import patch

from langchain_core.documents import Document

from backend.app.services.retrieval_service import (
    RetrievedChunk,
    format_policy_context,
    retrieve_policy_chunks,
)


def make_chunk(
    content: str,
    score: float,
    section_number: str = "3",
    section_heading: str = "Annual Leave",
) -> RetrievedChunk:
    return RetrievedChunk(
        document=Document(
            page_content=content,
            metadata={
                "policy_id": "leave-policy",
                "policy_title": "Company Leave Policy",
                "policy_version": "2.0",
                "section_number": section_number,
                "section_heading": section_heading,
            },
        ),
        score=score,
    )


@patch("backend.app.services.retrieval_service.get_settings")
@patch("backend.app.services.retrieval_service.search_policy")
def test_excludes_low_scoring_chunks(mock_search, mock_settings):
    mock_settings.return_value.retrieval_score_threshold = 0.45
    mock_search.return_value = [
        (
            Document(
                page_content="Relevant policy content.",
                metadata={
                    "section_heading": "Annual Leave",
                },
            ),
            0.80,
        ),
        (
            Document(
                page_content="Unrelated policy content.",
                metadata={
                    "section_heading": "Other",
                },
            ),
            0.20,
        ),
    ]

    results = retrieve_policy_chunks("How does annual leave work?")

    assert len(results) == 1
    assert results[0].document.page_content == "Relevant policy content."
    assert results[0].score == 0.80


def test_formats_policy_context_with_citations():
    chunks = [
        make_chunk(
            content="Employees may apply for annual leave.",
            score=0.85,
            section_number="3.1",
            section_heading="Annual Leave",
        )
    ]

    context = format_policy_context(chunks)

    assert "Company Leave Policy" in context
    assert "Version: 2.0" in context
    assert "Section 3.1: Annual Leave" in context
    assert "Employees may apply for annual leave." in context


def test_empty_chunks_produce_empty_context():
    assert format_policy_context([]) == ""
