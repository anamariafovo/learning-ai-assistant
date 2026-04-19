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
git clone https://github.com/your-username/learning-ai-assistant-dev.git
cd learning-ai-assistant-dev
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
python -m streamlit run rag_app/app.py
```

Your browser will open at `http://localhost:8501`.

---

## 📤 Uploading Content

From the **sidebar**:

1. Upload a `.txt` transcript or `.pdf` file
2. Enter a module name (e.g. `module1_intro`)
3. Click **💾 Ingest** to add to the vector database
4. Click **📝 Summarise** to generate a structured summary

> 💡 Check **"Append to existing summary"** to merge new content into an existing summary without duplication.

**Naming convention:** `moduleN_shortname` (lowercase, underscores only)

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
