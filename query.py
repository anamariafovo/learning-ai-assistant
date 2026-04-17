from dotenv import load_dotenv
# Load environment variables
load_dotenv()

import os
import chromadb
from openai import OpenAI

# Init OpenAI client
client = OpenAI()

# Init Chroma client — persistent, same path as build_db.py
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Load collection
try:
    collection = chroma_client.get_collection(name="course")
except Exception as e:
    collection = None


# -------------------------
# Embedding
# -------------------------
def embed_query(query):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[query]
    )
    return response.data[0].embedding


# -------------------------
# Retrieval
# -------------------------
def retrieve(query, k=5):
    if collection is None:
        return [], []

    query_embedding = embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    return documents, metadatas


# -------------------------
# Ask function (CORE)
# -------------------------
def ask(query, mode="strict", debug=False):
    docs, metas = retrieve(query)

    if not docs:
        return "⚠️ No relevant course material found."

    context = "\n\n".join([
        f"[{m.get('source', 'unknown')}]\n{d}"
        for d, m in zip(docs, metas)
    ])

    if debug:
        print("\n--- Retrieved Context (preview) ---\n")
        print(context[:500])
        print("\n----------------------------------\n")

    # Mode rules
    if mode == "strict":
        rules = """
- ONLY use the provided context
- DO NOT use outside knowledge
- DO NOT infer beyond the text
- If unsure, say: "Not found in course material"
- Preserve technical terminology
"""
    else:
        rules = """
- Use the provided context as the primary source
- You MAY add external explanations for clarity
- Clearly separate:
  (1) Course-based information
  (2) Additional explanation
"""

    prompt = f"""
You are a university course assistant.

RULES:
{rules}

Context:
{context}

Question:
{query}

Answer in structured format:
- Key points
- Explanation
- Sources
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text


# -------------------------
# CLI Loop
# -------------------------
if __name__ == "__main__":
    print("📚 Course Assistant Ready")
    print("Type 'exit' to quit\n")

    while True:
        query = input("Ask: ").strip()

        if query.lower() in ["exit", "quit"]:
            break

        mode = input("Mode (strict/explain) [default=strict]: ").strip().lower()
        if mode not in ["strict", "explain"]:
            mode = "strict"

        debug_input = input("Debug? (y/n): ").strip().lower()
        debug = debug_input == "y"

        print("\n🤖 Answer:\n")
        try:
            answer = ask(query, mode=mode, debug=debug)
            print(answer)
        except Exception as e:
            print(f"❌ Error: {e}")

        print("\n" + "="*50 + "\n")