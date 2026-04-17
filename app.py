from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from query import ask, collection

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
    st.header("⚙️ Settings")

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
    st.subheader("📝 Summaries")

    if st.button("Generate All Summaries"):
        from summarise import summarise_all
        with st.spinner("Generating summaries..."):
            try:
                summarise_all()
                st.success("✅ Summaries saved to /summaries/")
            except RuntimeError as e:
                st.error(str(e))

    if modules:
        selected = st.selectbox("Generate for one module", [""] + modules)
        if selected and st.button("Generate Selected"):
            from summarise import summarise_module
            with st.spinner(f"Summarising {selected}..."):
                try:
                    summarise_module(selected)
                    st.success(f"✅ Saved to summaries/{selected}/summary.md")
                except RuntimeError as e:
                    st.error(str(e))

    st.divider()

    # Show available modules
    st.subheader("📂 Loaded Modules")
    if modules:
        for mod in modules:
            st.markdown(f"- `{mod}`")
    else:
        st.info("No modules loaded yet.")

    st.divider()
    st.markdown("**Mode Guide**")
    st.markdown("🔒 **Strict** — safe for exam prep")
    st.markdown("💡 **Explain** — better for understanding")

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