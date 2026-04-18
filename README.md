# 📚 Learning AI Assistant

A local AI-powered study assistant that lets you upload your university lecture transcripts and ask questions about them. Built with OpenAI embeddings, ChromaDB and a Streamlit chat interface.

---

## ✨ Features

- 💬 Chat interface that runs locally in your browser
- 🔒 **Strict mode** — answers only from your lecture material (great for exam prep)
- 💡 **Explain mode** — adds external knowledge for deeper understanding
- 📂 Supports multiple modules/lectures simultaneously
- 🐛 Debug mode to inspect retrieved lecture chunks
- 📝 AI-generated structured summaries per module

---

## 🛠️ Requirements

- Python 3.9+
- An [OpenAI API key](https://platform.openai.com/api-keys) with billing set up

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/learning-ai-assistant.git
cd learning-ai-assistant
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your OpenAI API key

Create a `.env` file in the project root:

```bash
touch .env
```

Add your key inside it:

```ini
OPENAI_API_KEY=sk-proj-your-key-here
```

> ⚠️ Never share or commit your `.env` file. It is already listed in `.gitignore`.

### 5. Add your lecture transcripts

Place your transcript `.txt` files inside the `data/` folder. Each file represents **one module** — concatenate all video transcripts for that module into a single `.txt` file.

**Naming convention:** `moduleN_shortname.txt` (lowercase, underscores only)

```
data/
├── module1_algorithms.txt       # All videos for Module 1 combined
├── module2_databases.txt        # All videos for Module 2 combined
└── module3_networks.txt         # All videos for Module 3 combined
```

**Inside each file**, separate individual videos with headers:

```
# Week 1 - Introduction
[Video: What is ML?]
transcript content here...

[Video: Types of Learning]
transcript content here...

# Week 2 - Supervised Learning
[Video: Linear Regression]
transcript content here...
```

> 💡 Large files are fine — the database automatically splits them into small chunks for retrieval. Only the most relevant passages are used when you ask a question.

> If you have `.vtt` subtitle files from YouTube, convert them to `.txt` before adding them.

### 6. Build the vector database

Run this once (and again every time you add new transcripts):

```bash
python3 build_db.py
```

You should see:

```
✅ Database built
```

---

## 🚀 How to Use

### Start the assistant

```bash
python3 -m streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`.

### Using the interface

| Element         | Description                             |
| --------------- | --------------------------------------- |
| 💬 Chat box     | Type your question and press Enter      |
| 🔒 Strict mode  | Answers sourced only from your lectures |
| 💡 Explain mode | Adds external context for clarity       |
| 📂 Sidebar      | Shows all loaded lecture modules        |
| 🐛 Debug toggle | Reveals which chunks were retrieved     |
| 🗑️ Clear chat   | Resets the conversation history         |

### Example questions

- _"Summarise the key concepts from week 1"_
- _"Explain what a neural network is"_
- _"What did the lecturer say about gradient descent?"_

---

## 📝 Generating & Viewing Module Summaries

### Generate summaries

After building the database you can generate a summary for a specific module in two ways:

**From the sidebar (recommended):**

1. Select a module from the **"Select module"** dropdown
2. Click **"🔄 Generate Summary"**

**From the terminal:**

```bash
# Summarise a specific module
python3 summarise.py module1_mobileDev --append
```

### Updating summaries with new content

If you add new content to an existing `.txt` file, always rebuild the database first, then regenerate the summary:

```bash
python3 build_db.py
python3 summarise.py module1_mobileDev --append
```

> 💡 Summaries use **append mode** by default — the model merges new content into the existing summary without rewriting what's already there, saving API costs.

Summaries are saved as markdown files:

```
summaries/
├── module1_mobileDev/
│   └── summary.md
└── module2_databases/
    └── summary.md
```

Each summary includes:

- 🎯 Overview
- 🔑 Key Concepts
- 📖 Detailed Notes
- ❓ Likely Exam Questions
- 🔗 Key Terms Glossary

### View summaries in the UI

Once generated, summaries can be read directly in the app:

1. In the sidebar, find **"📖 View Summary"**
2. Click the module button to open its summary
3. The summary replaces the chat view in the main area
4. Click **"✖ Close Summary"** to return to the chat

> 💡 If no summaries appear, generate them first using the sidebar.

---

## 📁 Project Structure

```
learning-ai-assistant/
├── data/            # Your lecture transcript .txt files
├── chroma_db/       # Auto-generated vector database (do not edit)
├── summaries/       # Auto-generated module summaries (markdown)
├── app.py           # Streamlit web interface
├── query.py         # Core RAG logic (retrieval + OpenAI)
├── build_db.py      # Transcript ingestion and embedding
├── summarise.py     # Summary generation script
├── requirements.txt
├── .env             # Your API key (never commit this)
└── README.md
```

---

## 💰 Cost Estimate

| Operation                       | Approx Cost      |
| ------------------------------- | ---------------- |
| Building DB (per transcript)    | ~$0.00002        |
| One question (strict/explain)   | ~$0.001–0.005    |
| Summary generation (per module) | ~$0.01–0.03      |
| **$5 credit**                   | ~1000+ questions |

> 💡 Set a [monthly spend cap](https://platform.openai.com/settings/organization/limits) on your OpenAI account to avoid unexpected charges.

---

## 🔒 Security Tips

- Always keep your API key in `.env` — never hardcode it
- Set a hard spend limit on your OpenAI account
- If your key is compromised, delete it immediately at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
