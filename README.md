# 📚 Learning AI Assistant

A local AI-powered study assistant that lets you upload your university lecture transcripts and ask questions about them. Built with OpenAI embeddings, ChromaDB and a Streamlit chat interface.

---

## ✨ Features

- 💬 Chat interface that runs locally in your browser
- 🔒 **Strict mode** — answers only from your lecture material (great for exam prep)
- 💡 **Explain mode** — adds external knowledge for deeper understanding
- 📂 Supports multiple modules/lectures simultaneously
- 🐛 Debug mode to inspect retrieved lecture chunks

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

Place your transcript `.txt` files inside the `data/` folder. Name them after the module:

```
data/
├── week1_intro.txt
├── week2_neural_networks.txt
├── week3_statistics.txt
```

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

## 📁 Project Structure

```
learning-ai-assistant/
├── data/            # Your lecture transcript .txt files
├── chroma_db/       # Auto-generated vector database (do not edit)
├── app.py           # Streamlit web interface
├── query.py         # Core RAG logic (retrieval + OpenAI)
├── build_db.py      # Transcript ingestion and embedding
├── requirements.txt
├── .env             # Your API key (never commit this)
└── README.md
```

---

## 💰 Cost Estimate

| Operation                     | Approx Cost      |
| ----------------------------- | ---------------- |
| Building DB (per transcript)  | ~$0.00002        |
| One question (strict/explain) | ~$0.001–0.005    |
| **$5 credit**                 | ~1000+ questions |

> 💡 Set a [monthly spend cap](https://platform.openai.com/settings/organization/limits) on your OpenAI account to avoid unexpected charges.

---

## 🔒 Security Tips

- Always keep your API key in `.env` — never hardcode it
- Set a hard spend limit on your OpenAI account
- If your key is compromised, delete it immediately at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

## 📝 Generating Module Summaries

After building the database, generate structured summaries for all modules:

```bash
python3 summarise.py
```

Or for a specific module:

```bash
python3 summarise.py week1_ml
```

Summaries are saved as markdown files:

```
summaries/
├── week1_ml/
│   └── summary.md
└── week2_neural_networks/
    └── summary.md
```

Each summary includes:

- 🎯 Overview
- 🔑 Key Concepts
- 📖 Detailed Notes
- ❓ Likely Exam Questions
- 🔗 Key Terms Glossary
