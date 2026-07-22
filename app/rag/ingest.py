"""
RAG Ingestion Pipeline
======================
Knowledge base (PNB policies/FAQ .md files) ko padho -> chhote chunks mein todo
-> embeddings banao -> ChromaDB (local vector DB) mein store karo.

Yeh ek baar (ya jab bhi KB update ho) chalana hota hai — "indexing" step.
Baad mein retriever.py in stored vectors se relevant chunks nikalega.

Chalane ke liye (project root se):
    venv\\Scripts\\python.exe -m app.rag.ingest    # Windows
    .venv/bin/python -m app.rag.ingest              # macOS/Linux

NOTE: pehli baar model download hota hai (internet chahiye). Corporate network par
huggingface.co block ho to pehle 'download_model.py' chalao (see us file).
"""

from pathlib import Path

import logging
import os

# ChromaDB 0.5.23 telemetry buggy warning band (cosmetic). Us logger ko chup karo.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from app.rag.embed_model import embed_model_name

# --- Config (baad mein core/config.py mein move karenge) ---
KB_DIR = Path(__file__).parent / "knowledge_base"   # .md files kahan hain
CHROMA_DIR = "chroma_db"                             # vectors disk par yahan persist honge (gitignored)
COLLECTION_NAME = "pnb_kb"                            # collection = ek "table" of vectors
# Model naam ya local offline folder — embed_model.py decide karta hai (see us file).

# Chunking knobs
CHUNK_SIZE = 500      # ek chunk mein max ~500 characters
CHUNK_OVERLAP = 100   # lagatar chunks 100 chars overlap karenge (context na toote)


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Text ko overlapping tukdon mein todo.

    Kyun overlap: agar ek important sentence chunk ke boundary par aa jaye,
    to overlap ki wajah se wo agle chunk mein bhi poora aa jata hai — retrieval
    ke waqt context nahi tootta.
    """
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        # Agla chunk 'overlap' characters peeche se shuru — isliye overlap.
        start += size - overlap
    return chunks


def main() -> None:
    # 1) PersistentClient = vectors disk par save karega (in-memory nahi).
    client = chromadb.PersistentClient(
        path=CHROMA_DIR, settings=Settings(anonymized_telemetry=False)
    )

    # 2) Embedding function — har document/query ko vector mein badlega.
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embed_model_name())

    # 3) Fresh start: purani collection ho to hata do (re-ingest idempotent rahe).
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # pehli baar collection exist nahi karti — koi baat nahi
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)

    # 4) Har .md file padho, chunk karo, aur collection mein add karo.
    md_files = sorted(KB_DIR.glob("*.md"))
    if not md_files:
        print(f"Koi .md file nahi mili: {KB_DIR}")
        return

    total_chunks = 0
    for md in md_files:
        text = md.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        # IDs unique hone chahiye. metadata = source track karne ke liye (citations!).
        ids = [f"{md.stem}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": md.name, "chunk": i} for i in range(len(chunks))]

        collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        total_chunks += len(chunks)
        print(f"  {md.name}: {len(chunks)} chunks")

    print(f"\nDone.  {len(md_files)} files -> {total_chunks} chunks -> collection '{COLLECTION_NAME}'")
    print(f"Vectors persisted at: {Path(CHROMA_DIR).resolve()}")


if __name__ == "__main__":
    main()
