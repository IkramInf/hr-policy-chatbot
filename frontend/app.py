
import streamlit as st

from frontend.components.sidebar import render_sidebar
from frontend.components.chat_view import render_chat_view
from frontend.components.message_composer import render_message_composer
from frontend.services.api_client import (
    APIClientError,
    send_chat_message,
)


st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_session() -> None:
    """Initialize the state needed for a conversation."""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("pending_question", None)


def process_question(question: str) -> None:
    """Add a question, call the API, and store the response."""
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    try:
        with st.spinner("Checking the leave policy..."):
            result = send_chat_message(question)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "sources": result.get("sources", []),
                "blocked": result.get("blocked", False),
            }
        )

    except APIClientError as exc:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    f"**Unable to get an answer**\n\n"
                    f"{exc}\n\n"
                    "Please try again. If the problem continues, "
                    "contact HR."
                ),
                "sources": [],
                "blocked": False,
            }
        )

    except ValueError as exc:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": str(exc),
                "sources": [],
                "blocked": False,
            }
        )


def main() -> None:
    initialize_session()

    selected_question = render_sidebar()

    if selected_question:
        st.session_state.pending_question = selected_question

    render_chat_view()

    typed_question = render_message_composer()

    question_to_process = (
        typed_question
        or st.session_state.pending_question
    )

    if question_to_process:
        st.session_state.pending_question = None
        process_question(question_to_process)
        st.rerun()


if __name__ == "__main__":
    main()
