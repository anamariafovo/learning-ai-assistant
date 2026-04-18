from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from query import ask, collection
import os

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
except Exception as e:
    modules = []
    st.warning(f"⚠️ Could not load modules: {e}")

# -------------------------
# Sidebar Settings
# -------------------------
with st.sidebar:
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

    st.divider()
    st.markdown("### 📝 Summaries")
    st.caption("Generate AI summaries from your lecture material")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate All", use_container_width=True):
            from summarise import summarise_all
            with st.spinner("Generating..."):
                try:
                    summarise_all()
                    st.success("✅ Done")
                except RuntimeError as e:
                    st.error(str(e))

    if modules:
        selected = st.selectbox("Module", [""] + modules, label_visibility="collapsed", placeholder="Select a module...")
        with col2:
            if selected and st.button("Generate", use_container_width=True):
                from summarise import summarise_module
                with st.spinner(f"Summarising..."):
                    try:
                        summarise_module(selected)
                        st.success(f"✅ Saved")
                    except RuntimeError as e:
                        st.error(str(e))

    st.divider()

    # -------------------------
    # View Summaries
    # -------------------------
    st.markdown("### 📖 View Summary")
    SUMMARIES_DIR = "summaries"

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

    st.divider()

    # Show available modules
    st.markdown("### 📂 Loaded Modules")
    if modules:
        st.caption("\n".join([f"• `{mod}`" for mod in modules]))
    else:
        st.caption("No modules loaded yet.")

    st.divider()
    st.caption("**Strict** — safe for exam prep · **Explain** — better for understanding")

# -------------------------
# Main Area — Summary Viewer or Chat
# -------------------------
if st.session_state.get("viewing_summary"):
    mod = st.session_state["viewing_summary"]
    summary_path = os.path.join("summaries", mod, "summary.md")
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
if "messages" not in st.session_state:
    st.session_state.messages = []

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
            try:
                answer = ask(prompt, mode=mode, debug=debug)
                st.markdown(answer)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })
            except Exception as e:
                st.error(f"❌ Error: {e}")

# -------------------------
# Clear Chat Button
# -------------------------
if st.session_state.messages:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()