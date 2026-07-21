#!/usr/bin/env bash
# =============================================================================
# One-command setup for Linux / macOS.
# Clone karne ke baad project root se chalao:   bash setup.sh
#
# HAR STEP PEHLE CHECK karta hai — jo pehle se hai use SKIP, sirf jo missing hai
# wahi karta hai. Isliye dobara chalana safe + fast hai (idempotent).
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")"

PY=venv/bin/python
MODEL_CFG=app/rag/models/paraphrase-multilingual-MiniLM-L12-v2/config.json
CHROMA_DB=chroma_db/chroma.sqlite3

# --- [0/5] python3 maujood hai? ---
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 nahi mila. Pehle Python 3.12+ install karo."
    exit 1
fi

echo "==> [1/5] Virtual environment (venv/)"
if [ -x "$PY" ]; then
    echo "    venv pehle se hai — skip."
else
    python3 -m venv venv
    echo "    venv banaya."
fi

echo "==> [2/5] Dependencies"
# Check: zaroori packages import ho jaate hain? Ho to pip bilkul mat chalao.
if "$PY" -c "import chromadb, sentence_transformers, fastapi, uvicorn" >/dev/null 2>&1; then
    echo "    Dependencies pehle se installed — skip."
else
    echo "    Kuch missing hai — installing..."
    "$PY" -m pip install --upgrade pip >/dev/null
    "$PY" -m pip install -r requirements.txt
fi

echo "==> [3/5] .env file"
if [ -f .env ]; then
    echo "    .env pehle se hai — skip."
else
    cp .env.example .env
    echo "    .env banaya (.env.example se). ISME apni OPENROUTER_API_KEY daalna!"
fi

echo "==> [4/5] Embedding model (~470MB)"
if [ -f "$MODEL_CFG" ]; then
    echo "    Model pehle se maujood — skip."
else
    echo "    Model missing — downloading (open internet chahiye)..."
    "$PY" download_model.py
fi

echo "==> [5/5] RAG index (ChromaDB)"
if [ -f "$CHROMA_DB" ]; then
    echo "    Index pehle se bana hai — skip. (Rebuild ke liye: rm -rf chroma_db && $PY -m app.rag.ingest)"
else
    "$PY" -m app.rag.ingest
fi

echo ""
echo "Setup complete. Test: $PY -m app.rag.retriever"
