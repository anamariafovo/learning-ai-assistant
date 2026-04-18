import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from query import ask, collection
from summarise import summarise_module, sanitise_module_name

SUMMARIES_DIR = "summaries"

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="📚 Learning Assistant",
    page_icon="📚",
    layout="centered"
)

st.title("📚 Learning Assistant")
st.caption("Ask questions about your lecture transcripts")

# -------------------------
# DB Check
# -------------------------
if collection is None:
    st.warning(
        "⚠️ No course database found. "
        "Please add transcripts to the `data/` folder and run:\n\n"
        "```bash\npython3 build_db.py\n```"
    )
    st.stop()

# Define modules BEFORE the sidebar renders
try:
    all_metas = collection.get(include=["metadatas"])["metadatas"]
    modules = sorted(set(m["module"] for m in all_metas))
except Exception:
    modules = []
    st.warning("⚠️ Could not load modules. Check the database.")

# -------------------------
# Session State
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "viewing_summary" not in st.session_state:
    st.session_state["viewing_summary"] = None

# -------------------------
# Sidebar Settings
# -------------------------
with st.sidebar:
    st.markdown("""
        <style>
            [data-testid="stSidebarHeader"] {
                margin-bottom: 0px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Settings")

    mode = st.radio(
        "Mode",
        options=["strict", "explain"],
        captions=[
            "Only uses your lecture material",
            "Adds external explanations for clarity"
        ]
    )

    debug = st.toggle("Show retrieved context", value=False)

    st.markdown("<hr style='margin: 4px 0'>", unsafe_allow_html=True)

    st.markdown("### 📖 View Summary")
    available_summaries = []
    if os.path.exists(SUMMARIES_DIR):
        available_summaries = [
            d for d in os.listdir(SUMMARIES_DIR)
            if os.path.isfile(os.path.join(SUMMARIES_DIR, d, "summary.md"))
        ]

    if available_summaries:
        for summary in sorted(available_summaries):
            if st.button(f"📄 {summary}", use_container_width=True, key=f"sum_{summary}"):
                st.session_state["viewing_summary"] = summary
                st.rerun()

        if st.session_state.get("viewing_summary"):
            if st.button("✖ Close Summary", use_container_width=True):
                st.session_state["viewing_summary"] = None
                st.rerun()
    else:
        st.caption("No summaries generated yet.")

    st.markdown("<hr style='margin: 4px 0'>", unsafe_allow_html=True)
    st.markdown("### 📝 Generate Summary")
    st.caption("Appends new content to existing summary.")

    if modules:
        selected_module = st.selectbox("Select module", modules, key="summarise_module_select")

        if st.button("🔄 Generate Summary", use_container_width=True, help="Append new content to existing summary"):
            with st.spinner(f"Generating {selected_module}..."):
                try:
                    summarise_module(selected_module, append=True)
                    st.success("✅ Done!")
                except Exception:
                    st.error(f"❌ Failed to generate summary. Please try again.")

    st.markdown("<hr style='margin: 4px 0'>", unsafe_allow_html=True)

    st.markdown("### 📂 Loaded Modules")
    if modules:
        st.caption("\n".join([f"• `{mod}`" for mod in modules]))
    else:
        st.caption("No modules loaded yet.")

    st.markdown("<hr style='margin: 4px 0'>", unsafe_allow_html=True)
    st.caption("**Strict** — safe for exam prep · **Explain** — better for understanding")

# -------------------------
# Main Area — Summary Viewer or Chat
# -------------------------
if st.session_state.get("viewing_summary"):
    mod = st.session_state["viewing_summary"]
    safe_mod = sanitise_module_name(mod)   # add this
    summary_path = os.path.join(SUMMARIES_DIR, safe_mod, "summary.md")
    st.subheader(f"📖 Summary: `{mod}`")
    if os.path.exists(summary_path):
        with open(summary_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.warning("Summary file not found.")
    st.stop()

# -------------------------
# Chat History
# -------------------------
# Render previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------
# Chat Input
# -------------------------
if prompt := st.chat_input("Ask about your lectures..."):

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get answer
    with st.chat_message("assistant"):
        with st.spinner("Searching lecture material..."):
            answer, context = ask(prompt, mode=mode, debug=debug)
            st.markdown(answer)
            if debug and context:
                with st.expander("🔍 Retrieved Context (preview)"):
                    st.code(context[:500], language="text")

    st.session_state.messages.append({"role": "assistant", "content": answer})

# -------------------------
# Clear Chat Button
# -------------------------
if st.session_state.messages:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()