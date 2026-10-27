
import os
from typing import Any

import requests


DEFAULT_API_URL = "http://127.0.0.1:8000/api"
# Generous: a free-tier backend can take ~1 minute to wake from sleep.
REQUEST_TIMEOUT_SECONDS = 90


class APIClientError(Exception):
    """Raised when the backend request fails."""


def get_api_base_url() -> str:
    """Read the backend URL from the frontend environment."""
    base_url = os.getenv(
        "BACKEND_API_URL",
        DEFAULT_API_URL,
    ).strip().rstrip("/")

    if not base_url:
        raise APIClientError("The backend API URL is not configured.")

    return base_url


def _request(
    method: str,
    endpoint: str,
    **kwargs: Any,
) -> Any:
    """Send an HTTP request and handle expected failures."""
    url = f"{get_api_base_url()}/{endpoint.lstrip('/')}"

    try:
        response = requests.request(
            method=method,
            url=url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            **kwargs,
        )
        response.raise_for_status()

    except requests.Timeout as exc:
        raise APIClientError(
            "The request timed out. Please try again."
        ) from exc

    except requests.ConnectionError as exc:
        raise APIClientError(
            "Cannot connect to the HR Policy Assistant backend."
        ) from exc

    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response else None

        if status_code == 422:
            message = "The question or request format is invalid."
        elif status_code == 503:
            message = (
                "The assistant is temporarily unavailable. "
                "Please try again shortly."
            )
        elif status_code == 404:
            message = "The requested resource was not found."
        else:
            message = "The backend could not complete the request."

        raise APIClientError(message) from exc

    except requests.RequestException as exc:
        raise APIClientError(
            "An unexpected network error occurred. Please try again."
        ) from exc

    try:
        return response.json()
    except ValueError as exc:
        raise APIClientError(
            "The backend returned an invalid response."
        ) from exc


def send_chat_message(question: str) -> dict[str, Any]:
    """Submit an employee question to POST /api/chat."""
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("Please enter a question.")

    if len(cleaned_question) > 2000:
        raise ValueError("Your question cannot exceed 2,000 characters.")

    result = _request(
        "POST",
        "/chat",
        json={"question": cleaned_question},
    )

    if not isinstance(result, dict) or "answer" not in result:
        raise APIClientError("The backend returned an unexpected chat response.")

    return result


def get_policies() -> list[dict[str, Any]]:
    """Retrieve the policies currently indexed in the backend."""
    result = _request("GET", "/policies")

    if not isinstance(result, list):
        raise APIClientError("The backend returned an invalid policy list.")

    return result


def get_policy_sections(policy_id: str) -> dict[str, Any]:
    """Retrieve the sections belonging to a policy."""
    if not policy_id or not policy_id.strip():
        raise ValueError("Policy ID cannot be empty.")

    return _request(
        "GET",
        f"/policies/{requests.utils.quote(policy_id.strip(), safe='')}/sections",
    )


def check_backend_health() -> dict[str, Any]:
    """Check whether the backend API is responding."""
    return _request("GET", "/health")
