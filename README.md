# 📚 Learning AI Assistant

A local AI-powered study assistant that lets you upload university lecture transcripts and PDFs, then ask questions about them. Built with OpenAI, ChromaDB and Streamlit.

---

## ✨ Features

- 💬 Chat interface that runs locally in your browser
- 🔒 **Strict mode** — answers only from your lecture material
- 💡 **Explain mode** — adds external knowledge for deeper understanding
- 📂 Supports multiple modules simultaneously
- 📄 PDF and `.txt` transcript upload
- 📝 AI-generated structured summaries with append capability
- 🐛 Debug mode to inspect retrieved lecture chunks

---

## 🗂️ Project Structure

```
learning-ai-assistant-dev/
rag_app/
│   ├── app.py                  # Streamlit UI
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingest.py           # File processing + chunking
│   │   ├── embed.py            # OpenAI embeddings + ChromaDB
│   │   ├── retrieve.py         # Vector retrieval logic
│   │   ├── summarize.py        # Summary generation + append
│   │   └── chat.py             # Chatbot (strict + explain modes)
│   ├── data/                   # Uploaded files
│   ├── summaries/              # Saved markdown summaries
│   └── db/                     # ChromaDB persistent storage
├── .env                        # API key (never commit)
├── requirements.txt
└── README.md
```

---

## 🛠️ Requirements

- Python 3.9+
- An [OpenAI API key](https://platform.openai.com/api-keys) with billing set up

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/anamariafovo/learning-ai-assistant.git
cd learning-ai-assistant
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 4. Add your OpenAI API key

```bash
touch .env
```

Add inside:

```ini
OPENAI_API_KEY=sk-proj-your-key-here
```

> ⚠️ Never share or commit your `.env` file. It is already listed in `.gitignore`.

---

## 🚀 How to Use

### Start the assistant

```bash
python3 -m streamlit run rag_app/app.py
```

Your browser will open at `http://localhost:8501`.

---

## 📤 Uploading Content

From the **sidebar**:

1. Upload one or more `.txt` transcripts and/or PDF files
2. Enter a module name (e.g. `module1_databases`) or select an existing one
3. Click **Save module content** to add to the vector database
4. Click **Summarise Module** to generate a structured summary

> 💡 **"Append to existing summary"** is on by default — the LLM merges new content into the existing summary without duplicating anything already covered.

**Naming convention:** `moduleN_shortname` (lowercase, underscores only)

---

### Adding multiple files to the same module

You can build up a module from several files, either all at once or incrementally.

**Option A — Upload all files at once**

1. Select all the files you want (e.g. one `.txt` transcript and several PDFs) in the upload widgets
2. Select or type the module name
3. Click **Save module content** — all files are chunked and stored together under that module
4. Click **Summarise Module** to generate one combined summary

**Option B — Add files incrementally (after an initial ingest + summary already exists)**

1. Upload the new file(s) you want to add
2. Select the **existing** module from the "Select existing module" dropdown
3. Click **Save module content** — the new chunks are appended to the module in the database
4. Make sure **"Append to existing summary"** is checked
5. Click **Summarise Module** — the LLM reads the current summary alongside all stored chunks (old + new) and merges only the new material in, without repeating what is already there

---

## 💬 Chat Interface

| Element         | Description                             |
| --------------- | --------------------------------------- |
| 🔒 Strict mode  | Answers sourced only from your lectures |
| 💡 Explain mode | Adds external context for clarity       |
| 🐛 Debug toggle | Reveals which chunks were retrieved     |
| 🗑️ Clear chat   | Resets the conversation history         |

### Example questions

- _"Summarise the key concepts from module 1"_
- _"What did the lecturer say about gradient descent?"_
- _"Explain what a neural network is"_

---

## 📝 Summaries

Summaries are saved as markdown files in `rag_app/summaries/<module_name>/summary.md`.

Click any **📄 module name** in the sidebar to view its summary.

---

## 🔒 Security Notes

- Your `.env` file is in `.gitignore` — never commit it
- The assistant uses prompt injection guards to ignore instructions embedded in transcripts

---

## 📦 Dependencies

| Package         | Purpose               |
| --------------- | --------------------- |
| `streamlit`     | Web UI                |
| `chromadb`      | Local vector database |
| `openai`        | Embeddings + LLM      |
| `pypdf`         | PDF text extraction   |
| `python-dotenv` | Load `.env` file      |
