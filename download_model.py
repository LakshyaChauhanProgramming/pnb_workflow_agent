"""
Embedding model ko OFFLINE use ke liye download karo.
=====================================================
Isse ek baar aisi machine/network par chalao jahan internet KHULA ho.
Corporate wifi par huggingface.co block hai — is liye:

    -> Sabse aasaan: is laptop ko PHONE HOTSPOT (mobile data) se connect karo,
       phir yeh script chalao. Mobile data corporate firewall bypass karta hai.
    -> Ya ghar ke wifi par chalao.

Yeh model ko 'app/rag/models/<model>' folder mein save karega. Uske baad
ingest.py / retriever.py bina internet ke chalenge (fully offline).

Chalane ke liye (project root se):
    venv\\Scripts\\python.exe download_model.py     # Windows
    .venv/bin/python download_model.py               # macOS/Linux
"""

from pathlib import Path

from sentence_transformers import SentenceTransformer

MODEL_ID = "paraphrase-multilingual-MiniLM-L12-v2"
OUT_DIR = Path(__file__).parent / "app" / "rag" / "models" / MODEL_ID


def main() -> None:
    if (OUT_DIR / "config.json").exists():
        print(f"Model pehle se maujood hai: {OUT_DIR.resolve()}")
        print("Kuch karne ki zaroorat nahi. Seedha chalao: python -m app.rag.ingest")
        return

    print(f"Downloading '{MODEL_ID}' ... (~500MB, pehli baar thoda time lagega)")
    model = SentenceTransformer(MODEL_ID)   # HuggingFace se download
    OUT_DIR.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(OUT_DIR))

    print(f"\nDone. Model saved -> {OUT_DIR.resolve()}")
    print("Ab internet ke bina chal jayega:  python -m app.rag.ingest")


if __name__ == "__main__":
    main()
