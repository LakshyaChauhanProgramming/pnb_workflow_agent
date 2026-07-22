"""
RAG Retriever
=============
Runtime component: ek user query lo -> uska embedding banao -> ChromaDB se
sabse similar 'k' chunks nikaalo (source metadata ke saath).

ingest.py ne jo collection banayi thi (disk par 'chroma_db'), yeh usi ko
padhta hai. Baad mein RAG agent iske results ko LLM ke prompt mein context
ke roop mein daalega.

Zaroori: yahan WAHI embedding model use hona chahiye jo ingest.py ne use kiya,
warna query aur documents alag "vector space" mein honge aur match nahi hoga.
"""

from pathlib import Path

import logging
import os

# ChromaDB 0.5.23 ka telemetry buggy hai (capture() signature mismatch) aur
# har run pe "Failed to send telemetry event..." error LOG karta hai. Ye warning
# purely cosmetic hai. Do tarah se chup karate hain:
#  1) env var + Settings se telemetry off karne ki koshish (kabhi ignore hota),
#  2) PAKKA fix — us logger ka level CRITICAL kar do taaki error message chhupe.
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")
logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.CRITICAL)

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from app.rag.embed_model import embed_model_name

# --- Config: ingest.py se BILKUL match hona chahiye ---
CHROMA_DIR = str(Path(__file__).parent.parent.parent / "chroma_db")
COLLECTION_NAME = "pnb_kb"
# Embedding model: ingest.py wala hi (embed_model.py se resolve hota hai).

# Module load hone par ek hi baar client + collection banao (model reload mehenga hai).
# settings: ChromaDB ka anonymous telemetry band (0.5.23 me buggy warning deta tha).
_client = chromadb.PersistentClient(
    path=CHROMA_DIR, settings=Settings(anonymized_telemetry=False)
)
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embed_model_name())
_collection = _client.get_collection(name=COLLECTION_NAME, embedding_function=_ef)


def retrieve(query: str, k: int = 3, max_distance: float | None = None) -> list[dict]:
    """Query ke sabse similar top-k chunks laao.

    Args:
        query: user ka sawaal.
        k: kitne chunks laane hain (top-k).
        max_distance: safety gate. Agar diya, to sirf woh chunks rakho jinki
            distance <= max_distance ho (baaki "irrelevant" samajh ke hata do).
            None (default) = koi filter nahi (purana behaviour).

    Return: list of dicts — har ek mein text, source file, aur distance.
    'distance' jitni KAM, utna zyada similar (ye ChromaDB ki default L2 distance hai).

    NOTE: agar threshold ke baad kuch nahi bacha to KHAALI list [] milegi — matlab
    "koi relevant context nahi mila". Aage RAG agent isse jaan ke honestly bol sake
    ki jawab nahi pata, garbage chunk par hallucinate na kare.
    """
    results = _collection.query(query_texts=[query], n_results=k)

    # Chroma nested lists deta hai (kyunki ek saath kai queries ho sakti hain).
    # Humne ek hi query bheji, to index [0] lo.
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    hits = [
        {"text": doc, "source": meta["source"], "distance": round(dist, 3)}
        for doc, meta, dist in zip(docs, metas, dists)
    ]

    # Safety gate: threshold se door (zyada distance) wale chunks drop karo.
    if max_distance is not None:
        hits = [h for h in hits if h["distance"] <= max_distance]

    return hits


if __name__ == "__main__":
    # Threshold demo: in-domain query relevant chunk laata hai, out-of-domain khaali.
    THRESHOLD = 20.0

    for q in ["home loan ka interest rate kya hai", "credit card reward points"]:
        hits = retrieve(q, k=2, max_distance=THRESHOLD)
        print(f"\nQuery: {q!r}  (max_distance={THRESHOLD})")
        if not hits:
            print("  -> koi relevant context nahi mila (khaali).")
        for hit in hits:
            print(f"  [{hit['distance']}] {hit['source']}: {hit['text'][:70]}...")
