
import streamlit as st


def render_message_composer() -> str | None:
    """Render the chat input and return a submitted question."""
    question = st.chat_input(
        "Ask a question about your leave policy...",
        max_chars=2000,
        key="chat_input",
    )

    if question is None:
        return None

    question = question.strip()

    if not question:
        st.warning("Please enter a question.")
        return None

    return question
