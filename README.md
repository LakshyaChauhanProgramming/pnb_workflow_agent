# PNB Workflow Agent

A multi-agent AI banking assistant (Punjab National Bank themed) built to learn agentic GenAI end-to-end: RAG, LangGraph orchestration, tool-calling against mock banking APIs, guardrails, and observability.

> Capabilities (in progress): balance / account queries, complaint registration, loan status, FAQ answering over PNB policies, and form-filling assist. Real PNB APIs are replaced by local **mock banking APIs**.

## Tech stack

| Area | Choice |
|------|--------|
| Orchestration | LangGraph (multi-agent) |
| LLM gateway | OpenRouter (OpenAI-compatible) |
| Vector DB | ChromaDB (local, persisted to `chroma_db/`) |
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` (local, Hindi/Hinglish) |
| Backend | FastAPI |
| Frontend | Streamlit → React (later) |

## Setup

Works on **Linux/macOS** and **Windows**. Requires Python 3.12.

### 1. Clone & create a virtual environment

```bash
git clone https://github.com/LakshyaChauhanProgramming/pnb_workflow_agent.git
cd pnb_workflow_agent
python -m venv venv
```

Activate it:

```bash
# Linux / macOS
source venv/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

Then edit `.env` and add your `OPENROUTER_API_KEY`.

### 4. Download the embedding model (once)

The RAG pipeline uses a local embedding model that is **not** committed to the repo (~470 MB). On a machine with open internet:

```bash
python download_model.py
```

This saves it to `app/rag/models/`. If `huggingface.co` is blocked on your network, run `download_model.py` on another machine/network (or an EC2 instance), then copy the resulting `app/rag/models/paraphrase-multilingual-MiniLM-L12-v2/` folder over. The code auto-detects the local folder and runs fully offline.

### 5. Build the RAG index

```bash
# Linux / macOS
python -m app.rag.ingest

# Windows
venv\Scripts\python.exe -m app.rag.ingest
```

Then test retrieval:

```bash
python -m app.rag.retriever
```

## Running the mock banking API

```bash
uvicorn mock_bank.mock_banking_api:app --port 8001
```

API docs at http://localhost:8001/docs

## Project layout

```
app/
  rag/          ingest.py, retriever.py, embed_model.py, knowledge_base/
  agents/       (LangGraph flow — in progress)
  tools/, guardrails/, memory/, observability/, core/
mock_bank/      mock_banking_api.py  (standalone FastAPI backend)
evaluation/     RAGAS eval (planned)
frontend/       Streamlit app (planned)
```

## Notes

- `venv/`, `chroma_db/`, the downloaded model, and `.env` are gitignored — never committed.
- `.gitattributes` normalizes line endings so the repo is safe to work on across Linux and Windows.
