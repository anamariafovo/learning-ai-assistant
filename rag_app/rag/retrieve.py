import re
from rag.embed import get_collection, embed_texts

MAX_QUERY_CHARS = 2000
MAX_K = 20
MIN_K = 1


def retrieve(query: str, k: int = 5, module: str = None) -> tuple[list[str], list[dict]]:
    if len(query) > MAX_QUERY_CHARS:
        raise ValueError(f"Query exceeds maximum length of {MAX_QUERY_CHARS} characters.")

    if not (MIN_K <= k <= MAX_K):
        raise ValueError(f"k must be between {MIN_K} and {MAX_K}.")

    if module is not None:
        if not re.match(r'^[\w\-]{1,100}$', module):
            raise ValueError(f"Invalid module name: {module!r}")

    collection = get_collection()
    query_embedding = embed_texts([query])[0]

    kwargs = dict(query_embeddings=[query_embedding], n_results=k)
    if module:
        kwargs["where"] = {"module": module}

    results = collection.query(**kwargs)
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    return documents, metadatas