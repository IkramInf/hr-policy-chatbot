
import html

import streamlit as st

from frontend.components.sidebar import HR_EMAIL, SUGGESTED_QUESTIONS

ASSISTANT_AVATAR = ":material/support_agent:"

_HERO_HTML = (
    '<div class="hero">'
    '<div class="hero-icon">'
    '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#fff" '
    'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true">'
    '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.4-4.6A8 8 0 1 1 21 12z"/>'
    '<path d="m8.5 12 2.4 2.4 4.6-4.8"/></svg></div>'
    "<div>"
    "<h1>HR Policy Assistant</h1>"
    "<p>Instant answers to your company's policy questions, "
    "with source references.</p>"
    '<div class="hero-chips">'
    '<span class="chip live">Ready to help</span>'
    '<span class="chip">Source references</span>'
    '<span class="chip">Private data protected</span>'
    "</div></div></div>"
)

NOT_FOUND_PREFIX = "i don't know"
STARTER_COUNT = 4


def _format_source(source: dict) -> str:
    """Format a policy source as a readable citation (plain markdown)."""
    title = source.get("policy_title", "Company policy")
    version = source.get("policy_version", "Unknown version")
    section_number = str(source.get("section_number", "")).strip()
    heading = source.get("section_heading", "Untitled section")

    if section_number:
        section = f"Section {section_number} — {heading}"
    else:
        section = heading

    return f"**{title} (v{version})** · {section}"


def _source_row_html(source: dict) -> str:
    """Build one styled citation row. All values are HTML-escaped."""
    title = html.escape(str(source.get("policy_title", "Company policy")))
    version = html.escape(str(source.get("policy_version", "Unknown")))
    number = str(source.get("section_number", "")).strip()
    heading = html.escape(str(source.get("section_heading", "Untitled section")))
    badge = html.escape(number) if number else "§"

    return (
        '<div class="source-row">'
        f'<div class="source-badge">{badge}</div>'
        "<div>"
        f'<div class="source-title">{heading}</div>'
        f'<div class="source-meta">{title} · v{version}</div>'
        "</div>"
        "</div>"
    )


def _hr_link() -> str:
    email = html.escape(HR_EMAIL)
    return f'<a href="mailto:{email}">Email HR</a>'


def _render_sources(sources: list[dict]) -> None:
    label = f"Policy sources ({len(sources)})"
    with st.expander(label, icon=":material/menu_book:"):
        st.markdown(
            "".join(_source_row_html(source) for source in sources),
            unsafe_allow_html=True,
        )


def _render_assistant_message(message: dict) -> None:
    content = message.get("content", "")
    sources = message.get("sources", []) or []

    if message.get("error"):
        st.markdown(
            '<div class="notice notice-error">'
            '<span class="notice-icon">⚠️</span>'
            f"<div><strong>Couldn't get an answer.</strong><br>"
            f"{html.escape(str(content))}</div></div>",
            unsafe_allow_html=True,
        )
        return

    if message.get("blocked", False):
        st.markdown(content)
        st.markdown(
            '<div class="notice notice-warn">'
            '<span class="notice-icon">🔒</span>'
            "<div>This request involves private employee information. "
            f"For authorized assistance, contact HR · {_hr_link()}</div></div>",
            unsafe_allow_html=True,
        )
        return

    if not sources and content.strip().lower().startswith(NOT_FOUND_PREFIX):
        st.markdown(content)
        st.markdown(
            '<div class="notice notice-warn">'
            '<span class="notice-icon">💡</span>'
            "<div>The leave policy doesn't clearly cover this. "
            f"HR can confirm the right answer · {_hr_link()}</div></div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(content)

    if sources:
        _render_sources(sources)


def _render_message(message: dict, index: int) -> None:
    role = message.get("role", "assistant")

    if role not in ("user", "assistant"):
        return

    # The default user avatar is kept so the UI can style user messages.
    avatar = None if role == "user" else ASSISTANT_AVATAR

    with st.chat_message(role, avatar=avatar):
        if role == "assistant":
            _render_assistant_message(message)
        else:
            st.markdown(message.get("content", ""))

        timestamp = message.get("time")
        if timestamp:
            st.markdown(
                f'<div class="msg-time">{html.escape(str(timestamp))}</div>',
                unsafe_allow_html=True,
            )


def _render_retry(messages: list[dict]) -> None:
    """Offer a retry when the latest assistant message is an error."""
    last = messages[-1]

    if not (last.get("role") == "assistant" and last.get("error")):
        return

    if len(messages) < 2 or messages[-2].get("role") != "user":
        return

    if st.button(
        "Try again",
        icon=":material/refresh:",
        key=f"retry_{len(messages)}",
    ):
        question = messages[-2].get("content", "")
        del messages[-2:]
        st.session_state.pending_question = question
        st.rerun()


def _render_pending(question: str) -> None:
    """Show the question just asked plus a typing indicator."""
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        st.markdown(
            '<div class="typing"><span class="dots">'
            "<span></span><span></span><span></span></span>"
            "Checking the leave policy…</div>",
            unsafe_allow_html=True,
        )


def _render_welcome() -> None:
    st.markdown(
        '<div class="welcome">'
        "<h2>How can I help you today?</h2>"
        "<p>Ask anything about your company's leave policy. Every answer "
        "points to the policy section it came from, so you can check it "
        "yourself.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="starter-label">Try one of these</div>',
        unsafe_allow_html=True,
    )

    starters = SUGGESTED_QUESTIONS[:STARTER_COUNT]
    columns = st.columns(2)

    for index, question in enumerate(starters):
        with columns[index % 2]:
            if st.button(
                question,
                key=f"starter_{index}",
                use_container_width=True,
            ):
                st.session_state.pending_question = question
                st.rerun()


def render_chat_view(pending_question: str | None = None) -> None:
    """
    Render the conversation and any available policy citations.

    If pending_question is given, it is shown immediately with a typing
    indicator while the parent app waits for the backend.
    """
    st.markdown(_HERO_HTML, unsafe_allow_html=True)

    messages = st.session_state.setdefault("messages", [])

    if not messages and not pending_question:
        _render_welcome()
        return

    for index, message in enumerate(messages):
        _render_message(message, index)

    if pending_question:
        _render_pending(pending_question)
    elif messages:
        _render_retry(messages)
