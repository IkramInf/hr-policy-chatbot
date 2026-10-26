
import streamlit as st


def _format_source(source: dict) -> str:
    """Format a policy source as a readable citation."""
    title = source.get("policy_title", "Company policy")
    version = source.get("policy_version", "Unknown version")
    section_number = str(source.get("section_number", "")).strip()
    heading = source.get("section_heading", "Untitled section")

    if section_number:
        section = f"Section {section_number} — {heading}"
    else:
        section = heading

    return f"**{title} (v{version})** · {section}"


def render_chat_view() -> None:
    """Render the conversation and any available policy citations."""
    st.title("Your HR Policy Assistant")
    st.caption(
        "Ask questions about your company's leave policy. "
        "Answers include references to relevant policy sections."
    )

    messages = st.session_state.setdefault("messages", [])

    if not messages:
        st.markdown("### How can I help you today?")
        st.write(
            "Choose a suggested question from the sidebar, "
            "or type your own question below."
        )
        return

    for index, message in enumerate(messages):
        role = message.get("role", "assistant")
        content = message.get("content", "")

        if role not in ("user", "assistant"):
            continue

        with st.chat_message(role):
            st.markdown(content)

            sources = message.get("sources", [])

            if role == "assistant" and sources:
                with st.expander("Policy sources"):
                    for source in sources:
                        st.markdown(_format_source(source))

            if role == "assistant" and message.get("blocked", False):
                st.caption(
                    "For authorized assistance, please contact HR."
                )
