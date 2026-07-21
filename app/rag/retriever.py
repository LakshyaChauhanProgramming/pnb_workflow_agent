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

import chromadb
from chromadb.utils import embedding_functions

from app.rag.embed_model import embed_model_name

# --- Config: ingest.py se BILKUL match hona chahiye ---
CHROMA_DIR = str(Path(__file__).parent.parent.parent / "chroma_db")
COLLECTION_NAME = "pnb_kb"
# Embedding model: ingest.py wala hi (embed_model.py se resolve hota hai).

# Module load hone par ek hi baar client + collection banao (model reload mehenga hai).
_client = chromadb.PersistentClient(path=CHROMA_DIR)
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embed_model_name())
_collection = _client.get_collection(name=COLLECTION_NAME, embedding_function=_ef)


def retrieve(query: str, k: int = 3) -> list[dict]:
    """Query ke sabse similar top-k chunks laao.

    Return: list of dicts — har ek mein text, source file, aur distance.
    'distance' jitni KAM, utna zyada similar (ye ChromaDB ki default L2 distance hai).
    """
    results = _collection.query(query_texts=[query], n_results=k)

    # Chroma nested lists deta hai (kyunki ek saath kai queries ho sakti hain).
    # Humne ek hi query bheji, to index [0] lo.
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    return [
        {"text": doc, "source": meta["source"], "distance": round(dist, 3)}
        for doc, meta, dist in zip(docs, metas, dists)
    ]


if __name__ == "__main__":
    # Quick manual check
    for hit in retrieve("home loan ka interest rate kya hai", k=2):
        print(f"[{hit['distance']}] {hit['source']}: {hit['text'][:80]}...")
