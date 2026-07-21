# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Read these first

- **`PROJECT_CONTEXT.md`** — source of truth for status, decisions, key learnings, and the current `NEXT` step. Read it at the start of every session and keep it updated. This file (CLAUDE.md) holds only the stable rules/commands and does **not** duplicate progress.
- **`README.md`** — cross-platform setup / onboarding details.

## Working style (overrides defaults)

- **Reply in Hinglish** (Hindi in Latin script + English tech terms). Code, filenames, and identifiers stay English.
- **Teach mode** — this is a learning + resume project, not just shipping code. For each step give **Kya** (what), **Kaise** (hand-held how), **Kyun** (reasoning + how to explain it in an interview), plus trade-offs/alternatives. Go slow, one small step at a time, confirm before moving on, explain from basics.
- **Commit only when the user explicitly asks.** Never `git commit` proactively; `git add` is fine.

## Environment gotcha

Claude Code's Bash runs **every command in a fresh shell**, so `source .../activate` does **not** persist. Always call the venv binaries directly.

- The setup scripts create the venv as **`venv/`** (no dot). Windows: `venv\Scripts\python.exe`. Linux/macOS: `venv/bin/python`.
- The `tokenizers` version warning from chromadb/sentence-transformers is **benign**.
- On Windows the console is cp1252 — avoid non-ASCII (emoji) in `print()`, it raises `UnicodeEncodeError`.

## Common commands

```bash
# One-command idempotent setup (venv + deps + .env + model download + RAG index)
bash setup.sh          # Linux/macOS
.\setup.ps1            # Windows PowerShell

# Download embedding model for offline use (run on open internet; ~470MB)
venv/bin/python download_model.py            # (venv\Scripts\python.exe on Windows)

# Mock banking API (FastAPI) — docs at http://localhost:8001/docs
venv/bin/python -m uvicorn mock_bank.mock_banking_api:app --port 8001

# Build/refresh RAG index (KB .md -> chunks -> embeddings -> ChromaDB). Idempotent.
venv/bin/python -m app.rag.ingest

# RAG retriever quick check / playground
venv/bin/python -m app.rag.retriever
venv/bin/python -m app.rag.test_rag <n|all>
```

Run everything from the **project root** (`-m` package paths). No test suite yet (`tests/` is empty).

## Architecture (big picture)

Planned **multi-agent AI banking assistant** (PNB-themed). Real bank APIs unavailable, so a mock backend simulates them. Stack: **LangGraph** orchestration · **OpenRouter** LLM gateway (`OPENROUTER_API_KEY`, model `anthropic/claude-sonnet-5` in `.env`) · **ChromaDB** local vector DB · **`paraphrase-multilingual-MiniLM-L12-v2`** embeddings (chosen after eval — English-only model failed on Hinglish) · FastAPI · Streamlit-then-React frontend.

- **`mock_bank/`** — deliberately a **separate top-level package** (not under `app/`) to decouple the external backend from the agent. FastAPI app, in-memory fake data.
- **`app/rag/`** — built RAG pipeline: `ingest.py`, `retriever.py`, `embed_model.py`, `test_rag.py`, `knowledge_base/`, `models/` (git-ignored, offline copy). `embed_model.py` resolves the embedding model: local `models/` folder if present (sets `HF_HUB_OFFLINE=1` — for corporate networks where huggingface.co is blocked) else the HF hub name. **`ingest.py` and `retriever.py` must resolve the identical model + `COLLECTION_NAME`** — otherwise query and documents land in different vector spaces and nothing matches.
- **`app/`** (mostly placeholder) — target: `core/` (config, llm_client), `agents/` (supervisor, rag_agent, tool_agent, human_loop, graph.py), `tools/`, `guardrails/`, `memory/`, `observability/`, `api/`.
- **`chroma_db/`** — persisted vectors (git-ignored), rebuilt by `ingest.py`.
- **Cross-platform:** `setup.sh`/`setup.ps1` (idempotent setup), `download_model.py` (offline model), `.gitattributes` (LF repo, CRLF for `.ps1`/`.bat`/`.cmd`).

Intended flow: supervisor/router (intent) → RAG agent (grounded answers w/ citations) or tool agent (calls `mock_bank`) → human-in-the-loop approval for sensitive actions, with conversation memory; wired in `app/agents/graph.py`.

## LLM code note

This is an LLM app — default to the latest Claude models and consult the `claude-api` skill for model IDs/pricing **before** writing LLM client code (e.g. `app/core/llm_client.py`).
