
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from frontend.components.sidebar import render_sidebar
from frontend.components.chat_view import render_chat_view
from frontend.components.message_composer import render_message_composer
from frontend.services.api_client import (
    APIClientError,
    check_backend_health,
    send_chat_message,
)
from frontend.styles import inject_styles
from frontend.utils.date_utils import DEFAULT_TIMEZONE


st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="auto",
)


def _wake_backend() -> None:
    try:
        check_backend_health()
    except Exception:
        pass  # Only a wake-up call; real errors surface on the chat request.


def initialize_session() -> None:
    """Initialize the state needed for a conversation."""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("pending_question", None)

    # Wake a sleeping backend (e.g. Render free tier) while the user types.
    if not st.session_state.get("backend_pinged"):
        st.session_state.backend_pinged = True
        threading.Thread(target=_wake_backend, daemon=True).start()


def _now_label() -> str:
    """Return the current time, e.g. 9:05 AM, for message timestamps."""
    return (
        datetime.now(ZoneInfo(DEFAULT_TIMEZONE))
        .strftime("%I:%M %p")
        .lstrip("0")
    )


def process_question(question: str) -> None:
    """Add a question, call the API, and store the response."""
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
            "time": _now_label(),
        }
    )

    try:
        result = send_chat_message(question)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "sources": result.get("sources", []),
                "blocked": result.get("blocked", False),
                "time": _now_label(),
            }
        )

    except APIClientError as exc:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": f"{exc} If the problem continues, "
                "contact HR.",
                "sources": [],
                "blocked": False,
                "error": True,
                "time": _now_label(),
            }
        )

    except ValueError as exc:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": str(exc),
                "sources": [],
                "blocked": False,
                "error": True,
                "time": _now_label(),
            }
        )


def main() -> None:
    initialize_session()
    inject_styles()

    selected_question = render_sidebar()
    typed_question = render_message_composer()

    question_to_process = (
        typed_question
        or selected_question
        or st.session_state.pending_question
    )

    # Show history plus the new question and a typing indicator
    # while the backend is working.
    render_chat_view(pending_question=question_to_process)

    if question_to_process:
        st.session_state.pending_question = None
        process_question(question_to_process)
        st.rerun()


if __name__ == "__main__":
    main()
