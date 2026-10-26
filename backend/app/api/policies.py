
from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.policy import (
    PolicyResponse,
    PolicySectionsResponse,
)
from backend.app.services.policy_service import (
    get_policy_sections,
    list_policies,
)

router = APIRouter(tags=["Policies"])


@router.get("/policies", response_model=list[PolicyResponse])
def get_policies() -> list[PolicyResponse]:
    """List policies currently indexed in Qdrant."""
    try:
        return list_policies()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve policies right now.",
        ) from exc


@router.get(
    "/policies/{policy_id}/sections",
    response_model=PolicySectionsResponse,
)
def get_policy_sections_endpoint(
    policy_id: str,
) -> PolicySectionsResponse:
    """Return the sections of an indexed policy."""
    try:
        policy = get_policy_sections(policy_id)

        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Policy not found.",
            )

        return policy

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to retrieve policy sections right now.",
        ) from exc
