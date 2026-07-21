"""
Embedding model resolver (offline-friendly)
============================================
ingest.py aur retriever.py dono ko WAHI embedding model chahiye. Yeh helper
decide karta hai model kahan se load hoga:

- Agar model locally download ho chuka hai (models/ folder mein) -> local folder
  se load karo aur HuggingFace ko bilkul contact mat karo (fully offline).
- Warna -> HuggingFace Hub se naam ke through (pehli baar internet chahiye).

Kyun: corporate network par huggingface.co block hai (SSL handshake fail). Is liye
model ko ek baar kisi khule network par 'download_model.py' se download karke yahan
rakh lete hain, phir sab offline chalta hai.
"""

import os
from pathlib import Path

MODEL_ID = "paraphrase-multilingual-MiniLM-L12-v2"   # Hindi + Hinglish samajhta hai
MODELS_DIR = Path(__file__).parent / "models"        # local downloaded models yahan
_LOCAL_DIR = MODELS_DIR / MODEL_ID


def embed_model_name() -> str:
    """Local folder path (offline) ya HF model id return karo.

    Agar local copy mili to HF ko offline pin kar dete hain — taaki koi bhi
    library galti se network hit na kare (varna handshake error aayega).
    """
    if (_LOCAL_DIR / "config.json").exists():
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        return str(_LOCAL_DIR)
    return MODEL_ID
