# backend/app/services/chat_service.py

from dataclasses import dataclass, field
import logging
import re

from backend.app.core.prompts import FALLBACK_ANSWER
from backend.app.services.llm_service import generate_answer
from backend.app.services.privacy_service import (
    PRIVACY_REFUSAL,
    check_privacy,
)
from backend.app.services.retrieval_service import (
    RetrievedChunk,
    format_policy_context,
    retrieve_policy_chunks,
)

logger = logging.getLogger(__name__)


@dataclass
class PolicySource:
    """A policy section used to answer an employee's question."""

    policy_id: str | None
    policy_title: str
    policy_version: str
    section_number: str
    section_heading: str


@dataclass
class ChatResult:
    """Structured result returned by the chat service."""

    answer: str
    sources: list[PolicySource] = field(default_factory=list)
    blocked: bool = False


def _build_sources(chunks: list[RetrievedChunk]) -> list[PolicySource]:
    """Extract citation metadata from retrieved policy passages."""
    sources: list[PolicySource] = []
    seen: set[tuple[str, str, str]] = set()

    for chunk in chunks:
        metadata = chunk.document.metadata

        policy_id = metadata.get("policy_id")
        section_number = str(metadata.get("section_number", ""))
        section_heading = str(
            metadata.get("section_heading", "Untitled section")
        )

        key = (
            str(policy_id or ""),
            section_number,
            section_heading,
        )

        if key in seen:
            continue

        seen.add(key)

        sources.append(
            PolicySource(
                policy_id=policy_id,
                policy_title=str(
                    metadata.get("policy_title", "Company policy")
                ),
                policy_version=str(
                    metadata.get("policy_version", "Unknown version")
                ),
                section_number=section_number,
                section_heading=section_heading,
            )
        )

    return sources


def _cited_sources(
    answer: str,
    sources: list[PolicySource],
) -> list[PolicySource]:
    """Keep only sources the answer cites; fall back to all retrieved."""
    cited = [
        source
        for source in sources
        if (
            source.section_number
            and re.search(
                rf"Section\s+{re.escape(source.section_number)}(?!\d)",
                answer,
            )
        )
        or source.section_heading.lower() in answer.lower()
    ]

    return cited or sources


def answer_question(question: str) -> ChatResult:
    """
    Process a question using privacy checks, retrieval, and Groq.

    The API layer should catch unexpected exceptions and return a
    safe error response without exposing internal details.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    question = question.strip()

    # 1. Privacy check: before retrieval and before any LLM call.
    privacy_decision = check_privacy(question)

    if privacy_decision.blocked:
        return ChatResult(
            answer=PRIVACY_REFUSAL,
            blocked=True,
        )

    # 2. Retrieve evidence from the indexed HR policy.
    chunks = retrieve_policy_chunks(question)

    # 3. Do not call the LLM if retrieval finds no adequate evidence.
    if not chunks:
        return ChatResult(answer=FALLBACK_ANSWER)

    # 4. Build context and capture source metadata.
    policy_context = format_policy_context(chunks)
    sources = _build_sources(chunks)

    if not policy_context.strip() or not sources:
        return ChatResult(answer=FALLBACK_ANSWER)

    logger.debug("Policy context sent to LLM:\n%s", policy_context)

    # 5. Generate an evidence-grounded answer.
    try:
        answer = generate_answer(
            question=question,
            policy_context=policy_context,
        )
    except Exception:
        logger.exception("Policy answer generation failed.")
        raise

    # 6. Keep the required fallback exact, even if the model adds text
    #    or quotes around it.
    normalized = answer.strip().strip("\"'“”").strip()

    if normalized.lower().startswith(FALLBACK_ANSWER.lower()):
        return ChatResult(answer=FALLBACK_ANSWER)

    # 7. A refusal produced by the LLM is still a privacy block.
    if normalized == PRIVACY_REFUSAL:
        return ChatResult(answer=PRIVACY_REFUSAL, blocked=True)

    return ChatResult(
        answer=answer,
        sources=_cited_sources(answer, sources),
    )
