import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI
import re

load_dotenv()
client = OpenAI()

# Init Chroma with persistence
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Avoid duplicates on re-run
try:
    chroma_client.delete_collection(name="course")
except Exception as e:
    pass

collection = chroma_client.create_collection(name="course")

DATA_DIR = "data"

def chunk_text(text, chunk_size=800, overlap=100):
    # Split on sentence boundaries first
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= chunk_size:
            current += " " + sentence
        else:
            if current:
                chunks.append(current.strip())
            current = sentence

    if current:
        chunks.append(current.strip())

    return chunks

def embed(texts):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [e.embedding for e in response.data]

doc_id = 0

for filename in os.listdir(DATA_DIR):
    if not filename.endswith(".txt"):  # Only process .txt files
        continue

    module_name = os.path.splitext(filename)[0]

    with open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    embeddings = embed(chunks)

    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeddings[i]],
            ids=[f"{filename}_{i}"],
            metadatas=[{
                "source": filename,
                "module": module_name,
                "chunk_index": i
            }]
        )
        doc_id += 1

print("✅ Database built")