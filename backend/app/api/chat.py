
import logging

from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    PolicySourceResponse,
)
from backend.app.services.chat_service import answer_question
from backend.app.core.security import validate_question

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Answer an employee's question using the indexed HR policy."""
    try:
        question = validate_question(request.question)
        result = answer_question(question)
        
        return ChatResponse(
            answer=result.answer,
            sources=[
                PolicySourceResponse(
                    policy_id=source.policy_id,
                    policy_title=source.policy_title,
                    policy_version=source.policy_version,
                    section_number=source.section_number,
                    section_heading=source.section_heading,
                )
                for source in result.sources
            ],
            blocked=result.blocked,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Chat request failed.")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The HR Policy Assistant is temporarily unavailable. Please try again.",
        ) from exc
