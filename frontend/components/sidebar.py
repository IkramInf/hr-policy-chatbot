
import streamlit as st

from frontend.utils.date_utils import get_formatted_date


POLICY_VERSION = "2.0"
HR_EMAIL = "hr@xyz-company.example"  # Replace with the real HR email.

SUGGESTED_QUESTIONS = [
    "How do I apply for annual leave?",
    "What types of leave are available?",
    "Is a medical certificate required for sick leave?",
    "Can unused leave be carried forward?",
    "What is the leave approval process?",
    "What leave rules apply during probation?",
    "Is compensatory leave available?",
    "Whom should I contact if my question is not covered?",
]


def render_sidebar() -> str | None:
    """
    Render the sidebar and return a selected FAQ question, if any.

    The parent app should clear the conversation when New Chat
    is clicked and process any returned FAQ question.
    """
    selected_question: str | None = None

    with st.sidebar:
        st.markdown("## Your HR Policy Assistant")
        st.caption("Clear answers from your company leave policy.")

        st.divider()

        if st.button("＋ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()

        with st.expander("Frequently Asked Questions", expanded=True):
            st.caption("Select a question to get started.")

            for index, question in enumerate(SUGGESTED_QUESTIONS):
                if st.button(
                    question,
                    key=f"faq_{index}",
                    use_container_width=True,
                ):
                    selected_question = question

        with st.expander("Contact HR"):
            st.write(
                "For questions the policy does not answer, "
                "please contact your HR team."
            )
            st.markdown(f"[Email HR](mailto:{HR_EMAIL})")

        with st.expander("Chat Tips"):
            st.markdown(
                """
                - Ask one question at a time.
                - Mention the type of leave you mean.
                - Check the cited policy section.
                - Contact HR when the policy is unclear.
                """
            )

        st.divider()
        st.caption(f"Policy version: {POLICY_VERSION}")
        st.caption(f"Today: {get_formatted_date()}")
        st.caption("Answers are based on indexed policy documents.")

    return selected_question
