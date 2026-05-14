import json
import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# On Streamlit Cloud there is no .env file; secrets come from st.secrets.
# Inject them into os.environ before load_dotenv() so all downstream os.getenv()
# calls (including module-level ones in tools/) see the values.
try:
    for _k, _v in st.secrets.items():
        os.environ.setdefault(_k, str(_v))
except Exception:
    pass  # no secrets.toml locally — that's fine, .env handles it

load_dotenv()

from agent import SYSTEM_PROMPT, TOOLS, MODEL, _call_tool, _chat, _RAW_TOOL_RE, _strip_leaked_tool_syntax
from tools.profile import get_garden_profile, update_garden_profile

# ── Human-readable labels shown in the status widget while tools run ────────────
_TOOL_LABELS = {
    "get_current_weather":  "Checking current weather",
    "get_forecast":         "Fetching forecast",
    "get_frost_dates":      "Looking up frost dates",
    "lookup_plant_care":    "Checking plant care guide",
    "get_garden_profile":   "Loading garden profile",
    "update_garden_profile": "Updating garden profile",
}

# ── Theme ───────────────────────────────────────────────────────────────────────
_BG           = "#130F08"
_SECONDARY_BG = "#2E1F14"
_INPUT_BG     = "#1A1208"
_TEXT         = "#EDD9A0"
_PRIMARY      = "#6EC44A"
_BORDER       = "#2E3A1A"

def _inject_theme() -> None:
    st.markdown(f"""
    <style>
    /* ── Backgrounds ── */
    .stApp, .stMain {{ background-color: {_BG} !important; }}
    section[data-testid="stSidebar"] > div {{ background-color: {_SECONDARY_BG}; }}
    .main .block-container {{ background-color: {_BG}; }}

    /* ── Text ── */
    .stApp, p, li, label, .stCaption, .stAlert p,
    [data-testid="stText"], h1, h2, h3, h4, h5, h6 {{ color: {_TEXT} !important; }}
    .stMarkdown p, .stMarkdown li, .stMarkdown h1,
    .stMarkdown h2, .stMarkdown h3 {{ color: {_TEXT} !important; }}

    /* ── Inputs ── */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {{
        background-color: {_INPUT_BG};
        color: {_TEXT};
        border-color: {_BORDER};
    }}

    /* ── Chat input ── */
    [data-testid="stChatInput"] textarea {{
        background-color: {_SECONDARY_BG};
        color: {_TEXT};
        border-color: {_BORDER};
    }}
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div {{
        background-color: {_SECONDARY_BG} !important;
        border-radius: 0.75rem !important;
    }}
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div {{
        background-color: {_BG} !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background-color: {_PRIMARY};
        color: #130F08;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }}
    .stButton > button:hover {{
        background-color: {_PRIMARY};
        filter: brightness(1.12);
        color: #130F08;
    }}
    /* Clear conversation button (standalone, outside columns) */
    section[data-testid="stSidebar"] .stButton > button {{
        background-color: #3a8c26;
        color: #130F08;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: #3a8c26;
        filter: brightness(1.12);
    }}
    /* Load / Save buttons (inside the two-column block) */
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button {{
        background-color: {_PRIMARY};
    }}
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] .stButton > button:hover {{
        background-color: {_PRIMARY};
    }}

    /* ── Chat messages ── */
    [data-testid="stChatMessage"] {{
        background-color: {_BG};
        border-radius: 10px;
    }}

    /* ── Status widget ── */
    [data-testid="stStatus"] {{
        background-color: {_BG};
        color: {_TEXT};
    }}

    /* ── Alert / info boxes ── */
    [data-testid="stAlert"] {{
        background-color: #3a8c26;
        border-left-color: {_PRIMARY};
    }}
    [data-testid="stAlert"] svg {{
        fill: {_PRIMARY} !important;
        color: {_PRIMARY} !important;
    }}
    [data-testid="stAlert"] [data-testid="stAlertContentIcon"] svg path {{
        fill: {_PRIMARY} !important;
    }}

    /* ── JSON display ── */
    [data-testid="stJson"] {{ background-color: {_INPUT_BG}; }}

    /* ── Dividers ── */
    hr {{ border-color: {_BORDER}; }}
    </style>
    """, unsafe_allow_html=True)

# ── Page config ─────────────────────────────────────────────────────────────────
st.set_page_config(page_title="GardenMind", page_icon="🌱", layout="wide")

# ── Session state ────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []   # full Groq message history (all roles)
if "user_id" not in st.session_state:
    st.session_state.user_id = "default"
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "groq_client" not in st.session_state:
    st.session_state.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

_inject_theme()

# ── Sidebar ──────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🌱 GardenMind")
    st.caption("AI-powered gardening advice")
    st.divider()

    st.subheader("Garden Profile")

    user_id = st.text_input("User ID", value=st.session_state.user_id)

    location = st.text_input(
        "Location",
        value=st.session_state.profile.get("location", ""),
        placeholder="e.g. Denver, CO",
    )

    plants_value = "\n".join(st.session_state.profile.get("plants", []))
    plants_input = st.text_area(
        "Plants you're growing (one per line)",
        value=plants_value,
        placeholder="tomato\nbasil\nmarigold",
        height=140,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load", use_container_width=True, help="Load saved profile"):
            result = get_garden_profile(user_id)
            if "error" in result:
                st.warning(result["error"])
            else:
                st.session_state.profile = result
                st.session_state.user_id = user_id
                st.rerun()
    with col2:
        if st.button("Save", use_container_width=True, help="Save profile"):
            plants_list = [p.strip() for p in plants_input.splitlines() if p.strip()]
            result = update_garden_profile(user_id, {"location": location, "plants": plants_list})
            st.session_state.profile = result["profile"]
            st.session_state.user_id = user_id
            st.success("Saved!")

    # Summary of active profile
    prof = st.session_state.profile
    if prof:
        st.divider()
        st.caption("**Active profile**")
        if prof.get("location"):
            st.markdown(f"📍 {prof['location']}")
        if prof.get("plants"):
            for plant in prof["plants"]:
                st.markdown(f"&nbsp;&nbsp;🌿 {plant}")

    st.divider()
    if st.button("🗑 Clear conversation", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.caption(f"Model: `{MODEL}`")

def _build_system_prompt() -> str:
    """Append loaded profile to the system prompt so the model always has it."""
    prof = st.session_state.profile
    if not prof:
        return SYSTEM_PROMPT
    lines = []
    if prof.get("location"):
        lines.append(f"Location: {prof['location']}")
    if prof.get("plants"):
        lines.append(f"Plants they're growing: {', '.join(prof['plants'])}")
    if not lines:
        return SYSTEM_PROMPT
    profile_block = "\n".join(lines)
    return SYSTEM_PROMPT + f"\n\nThe user's garden profile is already loaded:\n{profile_block}\nUse this information to personalize your responses without calling get_garden_profile."


# ── Main chat area ───────────────────────────────────────────────────────────────
st.header("GardenMind 🌱")
st.caption("Ask me anything about your garden — weather, frost dates, plant care, and more.")

# Empty-state welcome card
if not st.session_state.history:
    st.markdown(
        """
        <div style="background-color:#3a8c26;padding:1rem 1.25rem;border-radius:0.5rem;color:#ffffff;">
        🌿 <strong>Welcome to GardenMind!</strong><br>
        Try asking:<br>
        &bull; <em>What should I be doing in my garden this week?</em><br>
        &bull; <em>Is it safe to plant tomatoes in Denver right now?</em><br>
        &bull; <em>What's wrong with my zucchini?</em><br>
        &bull; <em>Save my profile — I'm in Austin growing peppers and basil.</em>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Replay existing conversation (skip intermediate tool/assistant-tool turns)
for msg in st.session_state.history:
    role = msg["role"]
    content = msg.get("content") or ""
    if role == "user":
        with st.chat_message("user"):
            st.markdown(content)
    elif role == "assistant" and content and not msg.get("tool_calls"):
        # Only show final assistant replies — not the intermediate turn that holds tool_calls
        with st.chat_message("assistant"):
            st.markdown(content)

# ── Chat input and agent loop ───────────────────────────────────────────────────
if prompt := st.chat_input("Ask about your garden, weather, frost dates, plants..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        reply = ""

        with st.status("🌱 Thinking...", expanded=True) as status:
            xml_retries = 0
            while True:
                response = _chat(
                    st.session_state.groq_client,
                    [{"role": "system", "content": _build_system_prompt()}]
                    + st.session_state.history,
                )

                message = response.choices[0].message

                # No tool calls — final answer
                if not message.tool_calls:
                    reply = message.content or ""
                    if _RAW_TOOL_RE.search(reply):
                        if xml_retries < 2:
                            xml_retries += 1
                            continue
                        reply = _strip_leaked_tool_syntax(reply)
                    status.update(label="✅ Done", state="complete", expanded=False)
                    break

                # Record the assistant turn that contains the tool call requests
                st.session_state.history.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ],
                })

                # Execute each tool and display inline
                for tc in message.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)

                    label = _TOOL_LABELS.get(name, name)
                    status.update(label=f"🔧 {label}...")

                    result_str = _call_tool(name, args)
                    result = json.loads(result_str)

                    # Friendly inline display of the tool call
                    args_repr = ", ".join(f"{k}={v!r}" for k, v in args.items())
                    st.markdown(f"**`{name}({args_repr})`**")
                    st.json(result, expanded=False)

                    st.session_state.history.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result_str,
                    })

        st.markdown(reply)
        st.session_state.history.append({"role": "assistant", "content": reply})
