import os
import sys
import time
import logging
sys.path.insert(0, os.path.dirname(__file__))

logger = logging.getLogger(__name__)

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from rag.ingest import save_uploaded_file, load_file, chunk_text
from rag.embed import ingest_chunks, get_all_modules, get_module_chunks, delete_module
from rag.chat import ask
from rag.summarize import generate_summary, list_summaries, read_summary
import shutil

DEBUG_ENABLED = os.getenv("APP_DEBUG", "false").lower() == "true"
MAX_CHAT_HISTORY = 100

st.set_page_config(page_title="📚 Course Assistant", page_icon="📚", layout="centered")
st.title("📚 Course Assistant")

st.html("""
    <style>
        [data-testid="stSidebar"] hr {
            margin-top: 14px;
            margin-bottom: 14px;
        }
    </style>
""")

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "viewing_summary" not in st.session_state:
    st.session_state.viewing_summary = None
if "upload_key" not in st.session_state:
    st.session_state.upload_key = 0

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Summaries")

    summaries = list_summaries()
    if summaries:
        for s in sorted(summaries):
            if st.button(f"📄 {s}", key=f"view_{s}", use_container_width=True):
                st.session_state.viewing_summary = s
                st.rerun()
        if st.session_state.viewing_summary:
            if st.button("✖ Close", use_container_width=True):
                st.session_state.viewing_summary = None
                st.rerun()
    else:
        st.caption("No summaries yet.")

    st.markdown("---")
    st.markdown("### Modules")
    modules = get_all_modules()
    st.caption("\n".join(f"• `{m}`" for m in modules) if modules else "None loaded.")

    st.markdown("---")
    st.markdown("### Upload Module Content")

    _uk = st.session_state.upload_key
    txt_files = st.file_uploader("Transcript (.txt)", type=["txt"], key=f"txt_{_uk}", accept_multiple_files=True)
    pdf_files = st.file_uploader("PDFs", type=["pdf"], key=f"pdf_{_uk}", accept_multiple_files=True)

    existing_modules = get_all_modules()
    selected_module = st.selectbox(
        "Select existing module",
        options=["— new module —"] + existing_modules,
        key=f"module_select_{_uk}",
    )
    module_name = st.text_input("Or enter new module name (e.g. module1_databases)", key=f"module_name_{_uk}")

    effective_module = module_name.strip() if module_name.strip() else (
        selected_module if selected_module != "— new module —" else ""
    )

    ingest_btn = st.button("Save module content", use_container_width=True)

    if ingest_btn:
        all_files = list(txt_files or []) + list(pdf_files or [])
        if not all_files:
            st.error("Please upload at least one file.")
        elif not effective_module:
            st.error("Please enter or select a module name.")
        else:
            with st.spinner("Processing..."):
                try:
                    total_chunks = 0
                    for uploaded in all_files:
                        path = save_uploaded_file(uploaded)
                        text = load_file(path)
                        chunks = chunk_text(text)
                        n = ingest_chunks(chunks, effective_module, uploaded.name)
                        total_chunks += n
                    st.success(f"✅ Ingested {total_chunks} chunks into '{effective_module}'")
                    time.sleep(2)
                    st.session_state.upload_key += 1
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ {e}")
                except Exception:
                    logger.exception("Error during file processing")
                    st.error("❌ An error occurred while processing the file. Please try again.")

    st.markdown("---")
    st.markdown("### Summarise Loaded Module")
    loaded_modules = get_all_modules()
    if loaded_modules:
        module_to_summarise = st.selectbox("Select module", loaded_modules, key="summarise_module_select")
        append_existing = st.checkbox("Append to existing summary", value=True, key="summarise_append")
        summary_language = st.selectbox(
            "Summary language",
            ["English", "Romanian", "French", "German", "Spanish", "Italian", "Portuguese", "Dutch", "Polish", "Other"],
            key="summarise_language",
        )
        if summary_language == "Other":
            summary_language = st.text_input("Enter language", key="summarise_language_custom").strip() or "English"
        if st.button("Summarise Module", use_container_width=True):
            with st.spinner("Summarising..."):
                try:
                    chunks = get_module_chunks(module_to_summarise)
                    if not chunks:
                        st.error("No chunks found for this module.")
                    else:
                        text = "\n\n".join(chunks)
                        generate_summary(module_to_summarise, text, append=append_existing, language=summary_language)
                        st.success(f"✅ Summary saved for '{module_to_summarise}'")
                        time.sleep(2)
                        st.rerun()
                except ValueError as e:
                    st.error(f"❌ {e}")
                except Exception:
                    logger.exception("Error summarising module")
                    st.error("❌ An error occurred while summarising. Please try again.")
    else:
        st.caption("No modules loaded yet.")

    st.markdown("---")
    st.markdown("### Delete Module")
    all_modules_for_delete = get_all_modules()
    if all_modules_for_delete:
        module_to_delete = st.selectbox("Select module to delete", all_modules_for_delete, key="delete_module_select")
        if "confirm_delete" not in st.session_state:
            st.session_state.confirm_delete = False
        if not st.session_state.confirm_delete:
            if st.button("🗑️ Delete module", use_container_width=True):
                st.session_state.confirm_delete = True
                st.rerun()
        else:
            st.warning(f"Delete **{module_to_delete}** and its summary? This cannot be undone.")
            if st.button("Yes, delete", use_container_width=True):
                try:
                    n = delete_module(module_to_delete)
                    summary_dir = os.path.join(
                        os.path.dirname(__file__), "summaries", module_to_delete
                    )
                    if os.path.isdir(summary_dir):
                        shutil.rmtree(summary_dir)
                    if st.session_state.viewing_summary == module_to_delete:
                        st.session_state.viewing_summary = None
                    st.session_state.confirm_delete = False
                    st.success(f"✅ Deleted '{module_to_delete}' ({n} chunks)")
                    time.sleep(2)
                    st.rerun()
                except Exception:
                    logger.exception("Error deleting module")
                    st.error("❌ An error occurred while deleting. Please try again.")
            if st.button("Cancel", use_container_width=True):
                st.session_state.confirm_delete = False
                st.rerun()
    else:
        st.caption("No modules to delete.")

    st.markdown("---")
    st.markdown("### Chat Settings")
    mode = st.radio("Mode", ["strict", "explain"], horizontal=True,
                    captions=["Lecture only", "Adds external context"])
    debug = st.toggle("Show retrieved context")

# ── Main area ──────────────────────────────────────────────────────────────────
if st.session_state.viewing_summary:
    mod = st.session_state.viewing_summary
    content = read_summary(mod)
    st.subheader(f"{mod}")
    if content:
        st.markdown(content)
    else:
        st.warning("Summary not found.")
    st.stop()

# ── Chat ───────────────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about your lectures..."):
    # Enforce chat history size limit
    if len(st.session_state.messages) >= MAX_CHAT_HISTORY * 2:
        st.session_state.messages = st.session_state.messages[-(MAX_CHAT_HISTORY * 2):]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer, context = ask(prompt, mode=mode, debug=debug)
            except ValueError as e:
                answer = f"⚠️ {e}"
                context = None
            except Exception:
                logger.exception("Error during chat")
                answer = "⚠️ An error occurred. Please try again."
                context = None
            st.markdown(answer)
            if debug and context:
                with st.expander("🔍 Retrieved context"):
                    st.code(context[:600], language="text")

    st.session_state.messages.append({"role": "assistant", "content": answer})

if st.session_state.messages:
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()