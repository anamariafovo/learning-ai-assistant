import os
import re
from pypdf import PdfReader

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ALLOWED_EXTENSIONS = {".txt", ".pdf"}
MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB
MAX_CHUNK_SIZE = 8000
MIN_CHUNK_SIZE = 100


def save_uploaded_file(uploaded_file, dest_dir: str = DATA_DIR) -> str:
    # Validate extension before saving
    safe_name = os.path.basename(uploaded_file.name)
    ext = os.path.splitext(safe_name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext!r}. Allowed: {ALLOWED_EXTENSIONS}")

    # Enforce file size limit
    data = uploaded_file.getbuffer()
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError(f"File exceeds maximum allowed size of {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.")

    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, safe_name)

    # Guard against path traversal
    if not os.path.realpath(dest_path).startswith(os.path.realpath(dest_dir) + os.sep):
        raise ValueError("Invalid file path: path traversal detected.")

    with open(dest_path, "wb") as f:
        f.write(data)
    return dest_path


def clean_text(text: str) -> str:
    # Remove VTT/SRT timestamps
    text = re.sub(r"\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}", "", text)
    text = re.sub(r"^\d+\s*$", "", text, flags=re.MULTILINE)
    # Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def load_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return clean_text(f.read())


def load_pdf(filepath: str) -> str:
    reader = PdfReader(filepath)
    pages = [page.extract_text() or "" for page in reader.pages]
    return clean_text("\n\n".join(pages))


def load_file(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".txt":
        return load_txt(filepath)
    elif ext == ".pdf":
        return load_pdf(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    if not (MIN_CHUNK_SIZE <= chunk_size <= MAX_CHUNK_SIZE):
        raise ValueError(f"chunk_size must be between {MIN_CHUNK_SIZE} and {MAX_CHUNK_SIZE}.")
    if not (0 <= overlap < chunk_size):
        raise ValueError("overlap must be >= 0 and less than chunk_size.")
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= chunk_size:
            current += " " + sentence
        else:
            if current:
                chunks.append(current.strip())
            # Start next chunk with overlap from previous
            overlap_text = current[-overlap:] if len(current) > overlap else current
            current = overlap_text + " " + sentence

    if current:
        chunks.append(current.strip())

    return chunks