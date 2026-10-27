"""Global styling for the HR Policy Assistant (presentation only)."""

import streamlit as st

# Palette
#   Pine      #0F766E  primary actions, assistant identity
#   Deep pine #0B4F4A  headings, user bubbles
#   Mist      #F6F8F8  page background
#   Line      #DDE6E5  borders
#   Ink       #16302F  body text
#   Amber     #B45309  notices (privacy / not found)

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {
  --pine: #0F766E;
  --pine-deep: #0B4F4A;
  --pine-tint: #E6F2F0;
  --mist: #F6F8F8;
  --line: #DDE6E5;
  --ink: #16302F;
  --muted: #5B7371;
  --amber: #B45309;
  --amber-tint: #FEF3E2;
  --red: #B42318;
  --red-tint: #FDECEA;
}

html, body, [class*="css"], .stApp, button, input, textarea {
  font-family: 'Plus Jakarta Sans', -apple-system, 'Segoe UI', Roboto, sans-serif;
}

/* ---------- Page frame ---------- */
.stApp { background: var(--mist); }
#MainMenu, footer, [data-testid="stDecoration"] { visibility: hidden; height: 0; }
header[data-testid="stHeader"] { background: transparent; }

.block-container {
  max-width: 880px;
  padding-top: 2rem;
  padding-bottom: 7rem;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
  background: #FFFFFF;
  border-right: 1px solid var(--line);
}
/* collapse arrow: a clear, tappable round button in the top-right corner */
[data-testid="stSidebarHeader"] {
  position: absolute; top: .9rem; right: .75rem; z-index: 30;
  padding: 0; height: auto; background: transparent;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"],
[data-testid="stExpandSidebarButton"] button,
[data-testid="collapsedControl"] button {
  width: 34px; height: 34px; border-radius: 50%;
  background: var(--pine-tint); color: var(--pine-deep);
  border: 1px solid var(--line);
  transition: background .15s, color .15s;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stExpandSidebarButton"] button:hover,
[data-testid="collapsedControl"] button:hover {
  background: var(--pine); color: #fff;
}
[data-testid="stSidebarCollapseButton"] button svg,
[data-testid="stExpandSidebarButton"] svg { color: inherit; }

[data-testid="stSidebarUserContent"] { padding: 0 !important; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] {
  min-height: 100vh; gap: 0;
  padding: 0 1rem;
}
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] { margin-bottom: .6rem; }
section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] [data-testid="stVerticalBlock"] { gap: .1rem; }
section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] [data-testid="stElementContainer"] { margin: 0; }

/* sticky header (brand) and footer (version, date) */
[data-testid="stElementContainer"]:has(.brand) {
  position: sticky; top: 0; z-index: 20; background: #fff;
  margin: 0 -1rem .9rem; width: calc(100% + 2rem) !important; max-width: none !important; box-sizing: border-box;
  padding: 1.1rem 3.6rem 1rem 1rem;
  border-bottom: 1px solid var(--line);
}
[data-testid="stElementContainer"]:has(.sidebar-footer) {
  position: sticky; bottom: 0; z-index: 20; background: #fff;
  margin: auto -1rem 0; width: calc(100% + 2rem) !important; max-width: none !important; box-sizing: border-box;
  padding: .9rem 1rem 1rem;
  border-top: 1px solid var(--line);
}
.brand { display: flex; align-items: center; gap: .75rem; }
.brand-mark {
  width: 42px; height: 42px; border-radius: 12px; flex: none;
  display: grid; place-items: center; color: #fff; font-size: 20px;
  background: linear-gradient(135deg, var(--pine) 0%, var(--pine-deep) 100%);
  box-shadow: 0 4px 10px rgba(11, 79, 74, .25);
}
.brand-name { font-weight: 700; font-size: .95rem; white-space: nowrap; color: var(--pine-deep); line-height: 1.2; }
.brand-tag { font-size: .74rem; color: var(--muted); line-height: 1.35; margin-top: 2px; }

.side-label {
  font-size: .72rem; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted); margin: .6rem 0 0;
}
.sidebar-footer { display: flex; flex-direction: column; gap: .3rem; font-size: .78rem; color: var(--muted); }
.sidebar-footer .row { display: flex; justify-content: space-between; align-items: center; }
.sidebar-footer .pill {
  background: var(--pine-tint); color: var(--pine-deep);
  font-weight: 600; border-radius: 999px; padding: .1rem .6rem;
}
.sidebar-footer .note { font-size: .72rem; line-height: 1.4; }

/* new chat + FAQ buttons */
section[data-testid="stSidebar"] .stButton > button {
  justify-content: flex-start; text-align: left;
  border: 1px solid transparent; background: transparent;
  color: var(--ink); font-weight: 500; font-size: .85rem;
  border-radius: 10px; padding: .45rem .6rem; min-height: 0;
  transition: background .15s, border-color .15s, padding .15s;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--pine-tint); color: var(--pine-deep);
  border-color: transparent; padding-left: .8rem;
}
section[data-testid="stSidebar"] .stButton > button [data-testid="stIconMaterial"] {
  color: var(--pine); font-size: 1.1rem;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: var(--pine); border-color: var(--pine); color: #fff;
  font-weight: 600; padding: .6rem .9rem;
  box-shadow: 0 4px 12px rgba(15, 118, 110, .25);
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] [data-testid="stIconMaterial"] { color: #fff; }
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
  background: var(--pine-deep); border-color: var(--pine-deep); color: #fff; padding-left: .9rem;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] > div,
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p { justify-content: center; text-align: center; }

/* FAQ / contact / tips as soft cards */
section[data-testid="stSidebar"] [data-testid="stExpander"] {
  border: 1px solid var(--line); border-radius: 14px;
  background: #FBFDFD; overflow: hidden;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] details { border: none; background: transparent; }
section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
  font-weight: 600; font-size: .88rem; color: var(--pine-deep); padding: .7rem .85rem;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover { background: var(--pine-tint); }
section[data-testid="stSidebar"] [data-testid="stExpander"] summary svg,
section[data-testid="stSidebar"] [data-testid="stExpander"] summary [data-testid="stIconMaterial"] { color: var(--pine); }
section[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] { padding: 0 .5rem .6rem; }

.contact-card { font-size: .85rem; color: var(--ink); line-height: 1.5; padding: .2rem .4rem; }
.contact-card a {
  display: inline-block; margin-top: .4rem; background: var(--pine); color: #fff !important;
  font-weight: 600; text-decoration: none; padding: .35rem .8rem; border-radius: 8px;
}
.contact-card a:hover { background: var(--pine-deep); }
.tips { list-style: none; margin: 0; padding: 0 .3rem; }
.tips li { display: flex; gap: .6rem; padding: .45rem 0; font-size: .82rem; line-height: 1.4; color: var(--muted); }
.tips li b { display: block; color: var(--ink); font-weight: 600; }
.tips .n {
  flex: none; width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center;
  background: var(--pine-tint); color: var(--pine-deep); font-size: .72rem; font-weight: 700;
}

/* ---------- Page header ---------- */
.page-head { margin-bottom: 1.25rem; }
.page-head h1 {
  font-size: 1.6rem; font-weight: 700; color: var(--pine-deep);
  margin: 0; padding: 0; letter-spacing: -.01em;
}
.page-head p { color: var(--muted); font-size: .95rem; margin: .25rem 0 0; }

/* ---------- Welcome ---------- */
.welcome {
  background: #FFFFFF; border: 1px solid var(--line); border-radius: 20px;
  padding: 1.6rem 1.75rem; margin-bottom: .75rem;
}
.welcome h2 { font-size: 1.35rem; font-weight: 700; color: var(--ink); margin: 0 0 .35rem; padding: 0; }
.welcome p { color: var(--muted); margin: 0; font-size: .95rem; line-height: 1.55; }
.starter-label { font-size: .85rem; font-weight: 600; color: var(--muted); margin: .25rem 0 .1rem; }

[data-testid="stMainBlockContainer"] .stButton > button {
  width: 100%;
  min-height: 3.1rem;
  justify-content: flex-start;
  text-align: left;
  border: 1px solid var(--line);
  background: #FFFFFF;
  color: var(--ink);
  font-weight: 500;
  font-size: .9rem;
  border-radius: 14px;
  padding: .7rem 1rem;
  transition: border-color .15s, background .15s, box-shadow .15s;
}
[data-testid="stMainBlockContainer"] .stButton > button:hover {
  border-color: var(--pine);
  background: var(--pine-tint);
  color: var(--pine-deep);
  box-shadow: 0 2px 10px rgba(15, 118, 110, .12);
}

.stButton > button > div,
.stButton > button > div > span,
.stButton > button [data-testid="stMarkdownContainer"],
.stButton > button p {
  width: 100%; justify-content: flex-start; text-align: left;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] > div,
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p { justify-content: center; text-align: center; }

/* ---------- Chat messages ---------- */
[data-testid="stChatMessage"] {
  background: transparent;
  padding: .35rem 0;
  gap: .75rem;
  align-items: flex-start;
}
[data-testid="stChatMessageContent"] {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 4px 18px 18px 18px;
  padding: .85rem 1.1rem !important;
  max-width: 100%;
  color: var(--ink);
  line-height: 1.6;
  font-size: .96rem;
}
[data-testid="stChatMessageContent"] p { margin-bottom: .5rem; }
[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0; }
[data-testid="stChatMessageContent"] ul,
[data-testid="stChatMessageContent"] ol { margin: .25rem 0 .5rem; }

[data-testid="stChatMessageAvatarAssistant"],
[data-testid="stChatMessageAvatarCustom"] {
  background: linear-gradient(135deg, var(--pine) 0%, var(--pine-deep) 100%);
  color: #fff; border-radius: 12px;
}
[data-testid="stChatMessageAvatarUser"] {
  background: var(--pine-tint); color: var(--pine-deep); border-radius: 12px;
}

/* user messages: right aligned, filled bubble */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  flex-direction: row-reverse;
  justify-content: flex-start;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
  [data-testid="stChatMessageContent"] {
  background: var(--pine-deep);
  border-color: var(--pine-deep);
  color: #FFFFFF;
  border-radius: 18px 4px 18px 18px;
  flex: 0 1 auto !important;
  width: fit-content;
  max-width: 85%;
  margin: 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p { color: #FFFFFF; }

.msg-time { font-size: .72rem; color: var(--muted); margin-top: .35rem; line-height: 1.3; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .msg-time { color: rgba(255,255,255,.72); text-align: right; }
[data-testid="stChatMessageAvatarCustom"] [data-testid="stIconMaterial"],
[data-testid="stChatMessageAvatarAssistant"] [data-testid="stIconMaterial"] { color: #FFFFFF !important; }

/* notices inside assistant bubbles */
.notice {
  display: flex; gap: .6rem; align-items: flex-start;
  border-radius: 12px; padding: .7rem .85rem; margin-top: .6rem;
  font-size: .86rem; line-height: 1.5;
}
.notice a { font-weight: 600; text-decoration: none; }
.notice a:hover { text-decoration: underline; }
.notice-warn { background: var(--amber-tint); color: #7A3A06; }
.notice-warn a { color: var(--amber); }
.notice-error { background: var(--red-tint); color: #7A1710; }
.notice-icon { font-size: 1rem; line-height: 1.4; }

/* sources */
[data-testid="stChatMessageContent"] [data-testid="stExpander"] {
  border: 1px solid var(--line); border-radius: 12px; background: var(--mist);
  margin-top: .75rem;
}
[data-testid="stChatMessageContent"] [data-testid="stExpander"] summary {
  font-size: .85rem; font-weight: 600; color: var(--pine-deep);
}
.source-row {
  display: flex; gap: .7rem; align-items: flex-start;
  padding: .55rem 0; border-top: 1px solid var(--line);
}
.source-row:first-child { border-top: none; padding-top: .1rem; }
.source-badge {
  flex: none; min-width: 2.4rem; text-align: center;
  background: var(--pine-tint); color: var(--pine-deep);
  font-weight: 700; font-size: .78rem; border-radius: 8px; padding: .2rem .4rem;
}
.source-title { font-weight: 600; font-size: .88rem; color: var(--ink); line-height: 1.35; }
.source-meta { font-size: .78rem; color: var(--muted); }

/* typing indicator */
.typing { display: flex; align-items: center; gap: .6rem; color: var(--muted); font-size: .88rem; }
.dots { display: inline-flex; gap: 4px; }
.dots span {
  width: 7px; height: 7px; border-radius: 50%; background: var(--pine);
  animation: bounce 1.2s infinite ease-in-out;
}
.dots span:nth-child(2) { animation-delay: .15s; }
.dots span:nth-child(3) { animation-delay: .3s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: .45; }
  30% { transform: translateY(-5px); opacity: 1; }
}

/* ---------- Chat input ---------- */
[data-testid="stChatInput"] {
  border: 1px solid var(--line);
  border-radius: 16px;
  background: #FFFFFF;
  box-shadow: 0 4px 20px rgba(11, 79, 74, .08);
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--pine);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, .18);
}
[data-testid="stChatInput"] textarea { font-size: .95rem; }
[data-testid="stBottomBlockContainer"] { max-width: 880px; }
[data-testid="stBottom"] > div { background: linear-gradient(to top, var(--mist) 70%, transparent); }

/* ---------- Accessibility ---------- */
button:focus-visible, a:focus-visible, summary:focus-visible {
  outline: 3px solid rgba(15, 118, 110, .45) !important;
  outline-offset: 2px;
}
@media (prefers-reduced-motion: reduce) {
  .dots span { animation: none; }
  * { transition: none !important; }
}

/* ---------- Mobile ---------- */
@media (max-width: 640px) {
  .block-container, [data-testid="stMainBlockContainer"] { padding: 3.25rem .9rem 5.5rem; }
  .welcome { padding: 1.25rem 1.1rem; border-radius: 16px; }
  .page-head { margin: 1.4rem 0 .75rem; }
  .page-head h1 { font-size: 1.3rem; }
  .page-head p { display: none; }
  .welcome h2 { font-size: 1.15rem; }
  .welcome p { font-size: .88rem; }
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
    [data-testid="stChatMessageContent"] { max-width: 92%; }
}
</style>
"""


def inject_styles() -> None:
    """Inject the global stylesheet once per script run."""
    st.markdown(_CSS, unsafe_allow_html=True)
