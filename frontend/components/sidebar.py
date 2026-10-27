
import html

import streamlit as st

from frontend.utils.date_utils import get_formatted_date


POLICY_VERSION = "1.0"
HR_EMAIL = "hr@xyz.com"

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
        # Header (sticky at the top of the sidebar)
        st.markdown(
            '<div class="brand"><div class="brand-mark">💬</div><div>'
            '<div class="brand-name">HR Policy Assistant</div>'
            '<div class="brand-subtitle">Ask questions about HR policies</div>'
            "</div></div>",
            unsafe_allow_html=True,
        )

        if st.button(
            "New chat",
            icon=":material/add_comment:",
            type="primary",
            use_container_width=True,
            key="new_chat",
        ):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()

        with st.expander(
            "Frequently Asked Questions",
            expanded=True,
            icon=":material/help:",
        ):
            for index, question in enumerate(SUGGESTED_QUESTIONS):
                if st.button(
                    question,
                    key=f"faq_{index}",
                    icon=":material/chat_bubble_outline:",
                    use_container_width=True,
                ):
                    selected_question = question

        with st.expander("Chat Tips", icon=":material/lightbulb:"):
            tips = [
                ("Ask one thing at a time", "Short, specific questions work best."),
                ("Name the leave type", "For example annual, sick or casual leave."),
                ("Check the cited section", "Every answer points to its policy section."),
                ("Still unsure?", "Contact HR for anything the policy does not cover."),
            ]
            st.markdown(
                '<ul class="tips">'
                + "".join(
                    f'<li><span class="n">{i}</span><span><b>{html.escape(t)}</b>'
                    f"{html.escape(d)}</span></li>"
                    for i, (t, d) in enumerate(tips, start=1)
                )
                + "</ul>",
                unsafe_allow_html=True,
            )

        with st.expander("Contact HR", icon=":material/mail:"):
            st.markdown(
                '<div class="contact-card">Your question isn\'t covered? '
                "Our HR team can help.<br>"
                f'<a href="mailto:{html.escape(HR_EMAIL)}">Email HR</a></div>',
                unsafe_allow_html=True,
            )

        # Footer (sticky at the bottom of the sidebar)
        st.markdown(
            '<div class="sidebar-footer">'
            '<div class="row">'
            f'<span class="pill">Policy v{html.escape(POLICY_VERSION)}</span>'
            f"<span>{html.escape(get_formatted_date())}</span></div>"
            "</div>",
            unsafe_allow_html=True,
        )

    return selected_question
