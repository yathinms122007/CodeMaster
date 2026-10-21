import os
import base64
import io
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from database import (
    init_db,
    create_chat_session,
    get_all_sessions,
    delete_chat_session,
    save_message,
    get_session_messages,
    add_improvement_note,
    get_improvement_notes,
    get_improvement_notes_with_ids,
    delete_improvement_note,
)

# 1. Initialize Environment & SQLite Schema
load_dotenv()
init_db()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ GROQ_API_KEY not found in .env file! Please check your setup.")
    st.stop()

client = Groq(api_key=api_key)

# Embedded Official CodeMentor Logo (Transparent Glassy Flux PNG)
CODEMENTOR_LOGO_B64 = "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"
LOGO_DATA_URI = f"data:image/png;base64,{CODEMENTOR_LOGO_B64}"
LOGO_BYTES = base64.b64decode(CODEMENTOR_LOGO_B64)

# 2. Page Configuration (Uses your custom CodeMentor logo as the website tab icon)
st.set_page_config(
    page_title="CodeMentor",
    page_icon=io.BytesIO(LOGO_BYTES),
    layout="wide",
    initial_sidebar_state="expanded"
)

# 3. Sleek Black & Navy Blue + Unboxed Glassy Flux Hero CSS
st.markdown("""
<style>
    /* Main App Background: Deep Obsidian Black-Navy */
    .stApp {
        background-color: #0B0F19 !important;
        color: #E2E8F0 !important;
    }

    /* Top Header Bar */
    header[data-testid="stHeader"] {
        background-color: #0B0F19 !important;
    }

    /* Left Sidebar Dashboard: Rich Midnight Navy */
    section[data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1E293B !important;
    }
    section[data-testid="stSidebar"] * {
        color: #E2E8F0 !important;
    }

    /* Primary "New Chat" Button: Electric Royal Blue */
    button[kind="primary"] {
        background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3) !important;
    }
    button[kind="primary"] * {
        color: #FFFFFF !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
        border-color: #60A5FA !important;
    }

    /* "+ Add Rule" Form Submit Button: Glassy Cyan-Indigo Flux Theme */
    div[data-testid="stFormSubmitButton"] > button,
    button[kind="primaryFormSubmit"],
    button[kind="secondaryFormSubmit"] {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.85) 0%, rgba(37, 99, 235, 0.9) 50%, rgba(79, 70, 229, 0.85) 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(56, 189, 248, 0.55) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stFormSubmitButton"] > button *,
    button[kind="primaryFormSubmit"] * {
        color: #FFFFFF !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover,
    button[kind="primaryFormSubmit"]:hover {
        background: linear-gradient(135deg, #0EA5E9 0%, #3B82F6 50%, #6366F1 100%) !important;
        border-color: #7DD3FC !important;
        box-shadow: 0 6px 18px rgba(56, 189, 248, 0.4) !important;
    }

    /* Remove bulky border around sidebar form */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    /* Secondary Sidebar & Starter Buttons: Dark Navy Slate */
    button[kind="secondary"] {
        background-color: #172033 !important;
        color: #E2E8F0 !important;
        border: 1px solid #26334D !important;
        border-radius: 10px !important;
        text-align: left !important;
        transition: all 0.15s ease-in-out;
    }
    button[kind="secondary"]:hover {
        background-color: #1E293B !important;
        border-color: #38BDF8 !important;
        color: #FFFFFF !important;
    }

    /* Sidebar Rule Input & Text Inputs */
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div {
        background-color: #0F172A !important;
        border: 1px solid #26334D !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
    }
    div[data-baseweb="input"] input {
        background-color: transparent !important;
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }
    div[data-baseweb="input"] input::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
    }

    /* Sidebar Brand Header with Custom Logo */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 11px;
        font-size: 1.5rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-bottom: 4px;
    }
    .sidebar-brand-logo {
        width: 36px;
        height: 34px;
        object-fit: contain;
        filter: drop-shadow(0 0 8px rgba(56, 189, 248, 0.4));
    }
    .sidebar-section-title {
        display: flex;
        align-items: center;
        gap: 9px;
        font-size: 1.05rem;
        font-weight: 600;
        color: #E2E8F0;
        margin: 8px 0 10px 0;
    }
    .sidebar-section-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        border-radius: 7px;
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid rgba(56, 189, 248, 0.35);
    }

    /* Center Hero Section: Enlarged Unboxed Glassy Flux "CodeMentor" at the Top */
    .hero-wrapper {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 32px 20px 26px 20px;
        margin-bottom: 18px;
    }
    .hero-ambient-glow {
        position: absolute;
        top: 10px;
        width: 650px;
        height: 240px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.20) 0%, rgba(99, 102, 241, 0.12) 45%, rgba(11, 15, 25, 0) 75%);
        filter: blur(42px);
        z-index: 0;
        pointer-events: none;
    }
    .hero-brand-row {
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        margin-bottom: 18px;
    }
    .hero-logo-img {
        width: 86px;
        height: 80px;
        object-fit: contain;
        filter: drop-shadow(0 6px 24px rgba(56, 189, 248, 0.45));
    }
    .glassy-flux-text {
        font-size: 5.6rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        line-height: 1.02;
        background: linear-gradient(100deg, #F0F9FF 0%, #7DD3FC 25%, #38BDF8 50%, #60A5FA 75%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 8px 30px rgba(56, 189, 248, 0.38));
        user-select: none;
    }
    .hero-welcome-title {
        position: relative;
        z-index: 2;
        font-size: 2.85rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.01em;
        margin: 0 0 8px 0;
        line-height: 1.15;
    }
    .hero-welcome-subtitle {
        position: relative;
        z-index: 2;
        font-size: 1.3rem;
        font-weight: 400;
        color: #94A3B8;
        margin: 0;
        letter-spacing: 0.01em;
    }

    /* Chat Message Cards */
    div[data-testid="stChatMessage"] {
        background-color: #131B2E !important;
        border: 1px solid #1E293B !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        color: #F1F5F9 !important;
    }
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] span {
        color: #E2E8F0 !important;
    }

    /* Code Blocks inside Chat Messages */
    div[data-testid="stChatMessage"] pre {
        background-color: #090D16 !important;
        border: 1px solid #1E293B !important;
        border-radius: 8px !important;
    }

    /* Bottom Chat Input Bar */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div {
        background-color: #0B0F19 !important;
    }
    div[data-testid="stChatInput"],
    div[data-testid="stChatInput"] > div {
        background-color: #131B2E !important;
        border: 1px solid #26334D !important;
        border-radius: 12px !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #64748B !important;
        -webkit-text-fill-color: #64748B !important;
    }

    /* Dividers */
    hr {
        border-color: #1E293B !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. Session State Initialization
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None


def generate_chat_title(first_message: str) -> str:
    """Generates a short 3-5 word topic title related to the conversation using Groq."""
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate a concise 3 to 5 word title summarizing the user's message. "
                        "Return ONLY the title text, with no quotes or punctuation."
                    )
                },
                {"role": "user", "content": first_message}
            ],
            max_tokens=20
        )
        title = resp.choices[0].message.content.strip().strip('"').strip("'")
        if title:
            return title[:45]
    except Exception:
        pass
    words = first_message.strip().split()
    short = " ".join(words[:5])
    return short[:40] + ("..." if len(words) > 5 else "")


def build_system_prompt() -> dict:
    """Builds the system prompt dynamically including active rules from SQLite."""
    base = (
        "You are CodeMentor, a friendly, expert AI coding mentor helping a 2nd-year engineering student "
        "master programming, computer science fundamentals, and placement preparation."
    )
    rules = get_improvement_notes()
    if rules:
        formatted_rules = "\n".join(f"- {r}" for r in rules)
        base += f"\n\nIMPORTANT USER PREFERENCES (Follow strictly):\n{formatted_rules}"
    return {"role": "system", "content": base}


# ==========================================
# 5. LEFT SIDEBAR DASHBOARD
# ==========================================
with st.sidebar:
    # Brand Header with Custom Uploaded CodeMentor Logo
    st.markdown(f"""
    <div class="sidebar-brand">
        <img src="{LOGO_DATA_URI}" class="sidebar-brand-logo" alt="CodeMentor Logo" />
        <span>CodeMentor</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Session & Adaptive Rule Dashboard")

    # Top "New Chat" Button
    if st.button("➕ New Chat", type="primary", use_container_width=True):
        st.session_state.current_session_id = None
        st.rerun()

    st.divider()

    # Saved Chats Header with Sleek SVG Icon
    st.markdown("""
    <div class="sidebar-section-title">
        <span class="sidebar-section-icon">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
        </span>
        <span>Saved Chats</span>
    </div>
    """, unsafe_allow_html=True)

    sessions = get_all_sessions()

    if not sessions:
        st.caption("No saved chats yet. Ask a question to create your first chat!")
    else:
        for sess in sessions:
            col_chat, col_del = st.columns([0.82, 0.18])
            is_active = (st.session_state.current_session_id == sess["id"])
            label = f"💠 {sess['title']}" if is_active else f"▹ {sess['title']}"

            if col_chat.button(label, key=f"sess_{sess['id']}", use_container_width=True):
                st.session_state.current_session_id = sess["id"]
                st.rerun()

            if col_del.button("🗑️", key=f"del_sess_{sess['id']}", help="Delete this chat"):
                delete_chat_session(sess["id"])
                if st.session_state.current_session_id == sess["id"]:
                    st.session_state.current_session_id = None
                st.rerun()

    st.divider()

    # Response Rules Header with Sleek SVG Tuning Sliders Icon
    st.markdown("""
    <div class="sidebar-section-title">
        <span class="sidebar-section-icon">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="4" y1="21" x2="4" y2="14"></line>
                <line x1="4" y1="10" x2="4" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12" y2="3"></line>
                <line x1="20" y1="21" x2="20" y2="16"></line>
                <line x1="20" y1="12" x2="20" y2="3"></line>
                <line x1="1" y1="14" x2="7" y2="14"></line>
                <line x1="9" y1="8" x2="15" y2="8"></line>
                <line x1="17" y1="16" x2="23" y2="16"></line>
            </svg>
        </span>
        <span>Response Rules</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Add or delete custom instructions for how the AI should reply:")

    with st.form("add_rule_form", clear_on_submit=True):
        new_rule = st.text_input(
            "New rule",
            placeholder="e.g., Keep answers under 4 bullets",
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("➕ Add Rule", use_container_width=True)
        if submitted and new_rule.strip():
            add_improvement_note(new_rule.strip())
            st.rerun()

    rules_list = get_improvement_notes_with_ids()
    if not rules_list:
        st.caption("No custom rules active.")
    else:
        for rule_item in rules_list:
            r_col, d_col = st.columns([0.82, 0.18])
            r_col.markdown(f"• {rule_item['note']}")
            if d_col.button("✕", key=f"del_rule_{rule_item['id']}", help="Remove this rule"):
                delete_improvement_note(rule_item["id"])
                st.rerun()


# ==========================================
# 6. MAIN CHAT INTERFACE
# ==========================================
sample_prompt = None

if st.session_state.current_session_id is None:
    # Unboxed Enlarged "CodeMentor" + Custom Logo at the Top, followed by Welcome! and Subtitle
    st.markdown(f"""
    <div class="hero-wrapper">
        <div class="hero-ambient-glow"></div>
        <div class="hero-brand-row">
            <span class="glassy-flux-text">CodeMentor</span>
        </div>
        <h1 class="hero-welcome-title">Welcome!</h1>
        <p class="hero-welcome-subtitle">What Would You Like to Learn Today</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    if c1.button("📌 Java Constructors & OOPs", use_container_width=True):
        sample_prompt = "Explain constructors and OOPs principles in Java with simple examples."
    if c2.button("🗄️ SQL Joins for Placements", use_container_width=True):
        sample_prompt = "Explain INNER, LEFT, and RIGHT JOIN in SQL with an interview example."
    if c3.button("💻 DSA Roadmap for 2nd Year", use_container_width=True):
        sample_prompt = "Give me a practical Data Structures & Algorithms roadmap for a 2nd-year engineering student."
    messages_to_display = []
else:
    # Load Messages for the Selected Saved Chat
    active_sessions = [
        s for s in sessions if s["id"] == st.session_state.current_session_id
    ]
    current_title = active_sessions[0]["title"] if active_sessions else "Saved Chat"
    st.markdown(f"### 💠 {current_title}")
    messages_to_display = get_session_messages(st.session_state.current_session_id)

# Render Conversation Messages
for msg in messages_to_display:
    avatar = "🧑‍💻" if msg["role"] == "user" else io.BytesIO(LOGO_BYTES)
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Chat Input Box
typed_input = st.chat_input("Ask CodeMentor anything about coding, DSA, or placements...")
user_prompt = typed_input or sample_prompt

if user_prompt:
    # If currently on a New Chat, create a named session in SQLite automatically
    if st.session_state.current_session_id is None:
        auto_title = generate_chat_title(user_prompt)
        new_session_id = create_chat_session(auto_title)
        st.session_state.current_session_id = new_session_id

    current_sid = st.session_state.current_session_id

    # Display and save user message
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_prompt)
    save_message("user", user_prompt, session_id=current_sid)

    # Build context from system prompt (with active rules) + current chat's messages
    context = [build_system_prompt()] + get_session_messages(current_sid, limit=15)

    # Generate AI reply via Groq
    with st.chat_message("assistant", avatar=io.BytesIO(LOGO_BYTES)):
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=context
            )
            reply = response.choices[0].message.content
            st.markdown(reply)

    # Save AI reply to this session in SQLite and refresh sidebar so the new chat title appears
    save_message("assistant", reply, session_id=current_sid)
    st.rerun()