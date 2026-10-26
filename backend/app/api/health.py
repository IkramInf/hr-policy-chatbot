
from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the API's basic health status."""
    return {
        "status": "ok",
        "service": "hr-policy-chatbot-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
