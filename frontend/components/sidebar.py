
import html

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
        st.markdown(
            """
            <div class="brand">
              <div class="brand-mark">💬</div>
              <div>
                <div class="brand-name">HR Policy Assistant</div>
                <div class="brand-tag">Clear answers from your leave policy</div>
              </div>
            </div>
            """.replace("\n", ""),
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button(
            "New chat",
            icon=":material/add:",
            type="primary",
            use_container_width=True,
            key="new_chat",
        ):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()

        with st.expander("Frequently asked questions", expanded=True):
            for index, question in enumerate(SUGGESTED_QUESTIONS):
                if st.button(
                    question,
                    key=f"faq_{index}",
                    use_container_width=True,
                ):
                    selected_question = question

        with st.expander("Contact HR"):
            st.markdown(
                '<div class="contact-card">'
                "Your question isn't covered? Our HR team can help.<br>"
                f'<a href="mailto:{html.escape(HR_EMAIL)}">'
                f"{html.escape(HR_EMAIL)}</a>"
                "</div>",
                unsafe_allow_html=True,
            )

        with st.expander("Tips for better answers"):
            st.markdown(
                """
                - Ask one question at a time.
                - Name the type of leave you mean.
                - Check the cited policy section.
                - Contact HR when the policy is unclear.
                """
            )

        st.divider()
        st.markdown(
            '<div class="side-meta">'
            f"Policy version {html.escape(POLICY_VERSION)}<br>"
            f"{html.escape(get_formatted_date())}<br>"
            "Answers are based on indexed policy documents."
            "</div>",
            unsafe_allow_html=True,
        )

    return selected_question
