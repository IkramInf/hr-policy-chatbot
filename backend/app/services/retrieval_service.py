# backend/app/services/retrieval_service.py

import logging

from dataclasses import dataclass
from langchain_core.documents import Document
from backend.app.core.config import get_settings
from backend.app.infrastructure.vector_store import search_policy

logger = logging.getLogger(__name__)

@dataclass
class RetrievedChunk:
    """A policy passage retrieved from Qdrant with its similarity score."""

    document: Document
    score: float



def retrieve_policy_chunks(
    question: str,
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    """Retrieve policy passages and log their threshold decisions."""
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    settings = get_settings()
    results = search_policy(question=question, top_k=top_k)

    retrieved: list[RetrievedChunk] = []

    for document, score in results:
        similarity = float(score)
        passed = similarity >= settings.retrieval_score_threshold

        metadata = document.metadata
        logger.info(
            "Retrieval | score=%.4f | threshold=%.4f | passed=%s "
            "| section=%s | heading=%s | content=%.180s",
            similarity,
            settings.retrieval_score_threshold,
            passed,
            metadata.get("section_number", ""),
            metadata.get("section_heading", ""),
            document.page_content.replace("\n", " "),
        )

        if not passed:
            continue

        retrieved.append(
            RetrievedChunk(document=document, score=similarity)
        )

    return retrieved


def format_policy_context(chunks: list[RetrievedChunk]) -> str:
    """
    Format retrieved passages for the LLM.

    Include section metadata so the LLM can cite the source of its answer.
    """
    if not chunks:
        return ""

    formatted_sections: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk.document.metadata

        policy_title = metadata.get("policy_title", "Company policy")
        section_number = metadata.get("section_number", "")
        section_heading = metadata.get("section_heading", "Untitled section")
        policy_version = metadata.get("policy_version", "Unknown version")

        section_reference = (
            f"Section {section_number}: {section_heading}"
            if section_number
            else section_heading
        )

        formatted_sections.append(
            f"[Source {index}]\n"
            f"Policy: {policy_title}\n"
            f"Version: {policy_version}\n"
            f"Reference: {section_reference}\n"
            f"Content:\n{chunk.document.page_content.strip()}"
        )

    return "\n\n---\n\n".join(formatted_sections)
