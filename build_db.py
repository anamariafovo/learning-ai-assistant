import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI
import re

load_dotenv()
client = OpenAI()

MAX_FILE_SIZE_MB = 10

# Init Chroma with persistence
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Avoid duplicates on re-run
try:
    chroma_client.delete_collection(name="course")
except Exception:
    pass

collection = chroma_client.create_collection(name="course")

DATA_DIR = "data"

def chunk_text(text, chunk_size=800):
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

for filename in os.listdir(DATA_DIR):
    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join(DATA_DIR, filename)
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        print(f"⚠️ Skipping {filename} — too large ({size_mb:.1f} MB, limit is {MAX_FILE_SIZE_MB} MB)")
        continue

    module_name = os.path.splitext(filename)[0]

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except (UnicodeDecodeError, OSError) as e:
        print(f"⚠️ Skipping {filename} — could not read file: {e}")
        continue

    try:
        chunks = chunk_text(text)
        embeddings = embed(chunks)
    except Exception as e:
        print(f"⚠️ Skipping {filename} — embedding failed: {e}")
        continue

    for i, chunk in enumerate(chunks):
        try:
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
        except Exception as e:
            print(f"⚠️ Failed to add chunk {i} of {filename}: {e}")

print("✅ Database built")