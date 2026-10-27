# backend/app/services/llm_service.py

import logging
from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from backend.app.core.config import get_settings
from backend.app.core.prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    """Create and cache the configured Groq chat model."""
    settings = get_settings()

    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key.get_secret_value(),
        temperature=0,
        timeout=settings.request_timeout_seconds,
        max_retries=1,
    )


def generate_answer(question: str, policy_context: str) -> str:
    """
    Generate an answer grounded in the retrieved policy context.

    Raises an exception if the Groq request fails. The API layer
    should handle failures without exposing secrets or internal errors.
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not policy_context or not policy_context.strip():
        raise ValueError("Policy context cannot be empty.")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=build_user_prompt(
                question=question,
                policy_context=policy_context,
            )
        ),
    ]

    response = get_llm().invoke(messages)
    answer = response.content

    logger.debug("Raw LLM response: %r", answer)

    if isinstance(answer, str):
        cleaned_answer = answer.strip()
    elif isinstance(answer, list):
        # Handle providers that return content in multiple blocks.
        cleaned_answer = "\n".join(
            block["text"]
            for block in answer
            if isinstance(block, dict)
            and isinstance(block.get("text"), str)
        ).strip()
    else:
        cleaned_answer = ""

    if not cleaned_answer:
        raise RuntimeError("The LLM returned an empty response.")

    return cleaned_answer
