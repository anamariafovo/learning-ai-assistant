import os
import re
import uuid
import logging
import chromadb
from openai import OpenAI

logger = logging.getLogger(__name__)

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "db")
COLLECTION_NAME = "course"
EMBED_MODEL = "text-embedding-3-small"
MAX_CHUNK_CHARS = 8000  # ~2000 tokens; text-embedding-3-small supports 8191 tokens

client = OpenAI()
chroma_client = chromadb.PersistentClient(path=DB_DIR)


def get_collection(reset: bool = False):
    if reset:
        try:
            chroma_client.delete_collection(COLLECTION_NAME)
        except Exception as e:
            logger.warning("Could not delete collection '%s': %s", COLLECTION_NAME, e)
    try:
        return chroma_client.get_or_create_collection(COLLECTION_NAME)
    except Exception as e:
        raise RuntimeError(f"Failed to get/create collection: {e}") from e


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [e.embedding for e in response.data]


def _validate_module_name(module_name: str) -> None:
    if not re.match(r'^[\w\-]{1,100}$', module_name):
        raise ValueError(f"Invalid module_name: {module_name!r}")


def ingest_chunks(chunks: list[str], module_name: str, source_file: str):
    _validate_module_name(module_name)
    if not re.match(r'^[\w\-./]{1,200}$', source_file):
        raise ValueError(f"Invalid source_file: {source_file!r}")

    oversized = [i for i, c in enumerate(chunks) if len(c) > MAX_CHUNK_CHARS]
    if oversized:
        raise ValueError(f"Chunks at indices {oversized} exceed max length of {MAX_CHUNK_CHARS} characters.")

    collection = get_collection()
    embeddings = embed_texts(chunks)

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        doc_id = str(uuid.uuid4())
        collection.add(
            documents=[chunk],
            embeddings=[embedding],
            ids=[doc_id],
            metadatas=[{
                "source": source_file,
                "module": module_name,
                "chunk_index": i,
            }],
        )

    return len(chunks)


def get_module_chunks(module_name: str) -> list[str]:
    """Return all stored text chunks for a given module."""
    _validate_module_name(module_name)
    try:
        collection = get_collection()
        result = collection.get(
            where={"module": module_name},
            include=["documents", "metadatas"],
        )
        # Sort by chunk_index so text is reassembled in order
        pairs = sorted(
            zip(result.get("documents", []), result.get("metadatas", [])),
            key=lambda p: p[1].get("chunk_index", 0),
        )
        return [doc for doc, _ in pairs]
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve chunks for module '{module_name}': {e}") from e


def get_all_modules() -> list[str]:
    try:
        collection = get_collection()
        result = collection.get(include=["metadatas"])
        return sorted(set(m["module"] for m in result.get("metadatas", [])))
    except Exception:
        return []


def delete_module(module_name: str) -> int:
    """Delete all chunks for a module from ChromaDB. Returns number of chunks deleted."""
    _validate_module_name(module_name)
    collection = get_collection()
    result = collection.get(where={"module": module_name}, include=[])
    ids = result.get("ids", [])
    if ids:
        collection.delete(ids=ids)
    return len(ids)