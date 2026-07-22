"""
Embedding Projector Export
==========================
ChromaDB collection ('pnb_kb') mein store vectors ko do TSV files mein nikaalo,
jinhe TensorFlow Embedding Projector mein load karke embedding space visually
(2D/3D, PCA/t-SNE/UMAP) explore kar sakte ho.

Kyun 2 files:
  - vectors.tsv   -> har row = ek chunk ka poora 384-dim vector (tab-separated).
  - metadata.tsv  -> har row ka label (source file + text preview). Header zaroori
                     hai jab ek se zyada column ho.

NOTE: yahan embedding MODEL load karne ki zaroorat NAHI — hum sirf pehle se store
kiye gaye vectors PADH rahe hain (collection.get), naya text embed nahi kar rahe.
Isliye get_collection bina embedding_function ke — fast, model download nahi hota.

Chalane ke liye (project root se):
    venv/bin/python -m app.rag.export_embeddings          # Linux/macOS
    venv\\Scripts\\python.exe -m app.rag.export_embeddings  # Windows

Uske baad:
  1. https://projector.tensorflow.org kholo
  2. "Load" -> vectors.tsv (Step 1) aur metadata.tsv (Step 2) select karo
  3. Neeche PCA / t-SNE / UMAP toggle karke ghuma ke dekho; point pe hover = text.
"""

from pathlib import Path

import logging
import os

# ChromaDB 0.5.23 telemetry buggy warning band (cosmetic). Us logger ko chup karo.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)

import chromadb
from chromadb.config import Settings

# --- Config: ingest.py / retriever.py se match ---
CHROMA_DIR = str(Path(__file__).parent.parent.parent / "chroma_db")
COLLECTION_NAME = "pnb_kb"
OUT_DIR = Path(__file__).parent.parent.parent / "embedding_export"  # gitignored


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    # Sirf padhna hai -> embedding_function ki zaroorat nahi (koi naya text embed nahi karte).
    client = chromadb.PersistentClient(
        path=CHROMA_DIR, settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_collection(name=COLLECTION_NAME)

    data = collection.get(include=["embeddings", "documents", "metadatas"])
    embs, docs, metas = data["embeddings"], data["documents"], data["metadatas"]

    if len(embs) == 0:
        print("Collection khaali hai — pehle 'python -m app.rag.ingest' chalao.")
        return

    dim = len(embs[0])
    print(f"Chunks: {len(embs)}   |   Real dimensions per vector: {dim}")

    # 1) vectors.tsv — poore vectors, tab-separated, ek chunk per line.
    vectors_path = OUT_DIR / "vectors.tsv"
    with vectors_path.open("w") as f:
        for v in embs:
            f.write("\t".join(f"{x:.6f}" for x in v) + "\n")

    # 2) metadata.tsv — labels. Header row zaroori (multi-column).
    meta_path = OUT_DIR / "metadata.tsv"
    with meta_path.open("w", encoding="utf-8") as f:
        f.write("source\tpreview\n")
        for doc, m in zip(docs, metas):
            preview = doc[:60].replace("\t", " ").replace("\n", " ")
            f.write(f"{m['source']}\t{preview}\n")

    print("\nDone. Files:")
    print(f"  {vectors_path}")
    print(f"  {meta_path}")
    print("\nAb: https://projector.tensorflow.org -> Load -> vectors.tsv + metadata.tsv")


if __name__ == "__main__":
    main()
