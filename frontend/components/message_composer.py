
import streamlit as st


def render_message_composer() -> str | None:
    """Render the chat input and return a submitted question."""
    question = st.chat_input(
        "Ask a policy question…",
        max_chars=2000,
        key="chat_input",
    )

    if question is None:
        return None

    question = question.strip()

    if not question:
        st.toast("Please enter a question.", icon=":material/info:")
        return None

    return question
