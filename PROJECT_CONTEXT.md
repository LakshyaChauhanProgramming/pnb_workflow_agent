# PROJECT_CONTEXT — PNB Workflow Agent

> **Claude, naye system pe kaam shuru karne se pehle yeh poori file padho.** Yeh project ka
> compressed context + kaam karne ka tarika hai. Iske baad seedha "NEXT" section se continue karo.

---

## 1. Project kya hai
**PNB Workflow Agent** — multi-agent AI banking assistant (Punjab National Bank themed).
- **Maqsad:** (a) strong resume differentiator (agentic AI + banking domain), (b) GenAI seekhna. Baad mein production.
- **Agent kya karega:** balance/account query, complaint/dispute registration, loan status, FAQ answering (policies/charges/rates), form-filling assist (account/loan), branch/ATM locator.
- Real PNB APIs nahi hain → **mock banking APIs** banaye hain jo real system jaisa behave karte hain.

## 2. Mujhse (Claude) kaam kaise karwana hai — IMPORTANT
- **Hinglish mein baat** (Hindi in Latin script + English tech terms). Code/filenames/terms English.
- **Teach mode:** har step pe teen cheezein do — **Kya** (what), **Kaise** (how, step-by-step, hand-held), **Kyun** (reasoning + interview mein kaise samjhaoge). Trade-offs + alternatives batao. Slow chalo, ek chhota step at a time, confirm karke aage badho. User career switch kar raha hai GenAI mein — interview-ready understanding chahiye, sirf working code nahi.
- **Absolute basics se** samjhana (venv, env vars, API call kya hai — sab explain).
- **Git commit SIRF jab user explicitly bole.** Proactively kabhi commit mat karo. Staging (`git add`) theek hai.

## 3. Tech stack + finalized decisions
- **Orchestration:** LangGraph (multi-agent)
- **LLM provider:** OpenRouter (OpenAI-compatible gateway; `.env` mein `OPENROUTER_API_KEY`, model `anthropic/claude-sonnet-5`)
- **Vector DB:** ChromaDB (local, free, persist dir `chroma_db/` — gitignored)
- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` (local, via sentence-transformers) — Hindi/Hinglish ke liye chosen (eval ke baad; English-only default fail hua tha)
- **Backend:** FastAPI · **Frontend:** Streamlit pehle, React baad · **Observability:** Langfuse/LangSmith · **Deploy:** Docker → AWS/Render
- **LLM-app hai** → latest Claude models default; LLM client code likhne se pehle `claude-api` skill dekho.

## 4. Environment gotchas
- Python **3.12.3**, venv at `.venv/`. **Claude Code ka Bash har command fresh shell mein chalata hai** → `source .venv/bin/activate` persist NAHI hota. Hamesha `.venv/bin/python` / `.venv/bin/pip` directly use karo (user apne terminal mein activate karke `python` chala sakta hai).
- Install reproduce karne ke liye: `.venv/bin/pip install -r requirements.txt` (chromadb + sentence-transformers ka `tokenizers` version warning aayega — **benign**, runtime pe kuch nahi tootta).
- **git identity abhi placeholder hai** (`test123`, `--local`). GitHub pe push karne se PEHLE real name/email set karna hai (personal email, office nahi).

## 5. Folder structure (scaffolded)
```
app/           main.py, api/, agents/[supervisor, rag_agent, tool_agent, human_loop, graph.py],
               tools/, rag/[ingest.py, retriever.py, test_rag.py, knowledge_base/],
               guardrails/[pii_filter, prompt_injection_check], memory/, observability/, core/[config, llm_client]
mock_bank/     mock_banking_api.py  (ALAG package — external backend decouple karne ke liye, app/ se bahar)
evaluation/    eval_dataset.jsonl, run_ragas_eval.py
frontend/      streamlit_app.py
docker/ · tests/ · .env.example · requirements.txt · README.md
```
Package dirs mein `__init__.py`, data dirs mein `.gitkeep`.

## 6. Build order (plan)
1. mock_banking_api.py ✅ → 2. RAG (ingest + retriever) ✅ → **3. LangGraph flow ← ABHI YAHAN** →
4. guardrails + human-in-loop → 5. observability (Langfuse) → 6. evaluation (RAGAS) + Docker deploy

## 7. DONE tak (git commits on `main`)
| Commit | Kya |
|---|---|
| `73b423c` | .gitignore |
| `75a9426` | folder structure scaffold |
| `ccbbf51` | **mock banking API** |
| `e960ce3` | **RAG pipeline** (ingest + retriever + KB + test playground) |

**Mock bank (`mock_bank/mock_banking_api.py`)** — FastAPI, in-memory fake data.
Endpoints: `GET /`, `/health`, `/accounts/{acct}`, `/accounts/{acct}/balance`, `/loans/{id}/status`,
`POST /complaints` (Pydantic `ComplaintIn`, 201), `GET /complaints/{id}`.
Fake data: accounts `1111000011110000` (Amit), `2222000022220000` (Priya); loans `LN1001`, `LN1002`.
Run: `.venv/bin/uvicorn mock_bank.mock_banking_api:app --port 8001` → docs at `/docs`.

**RAG (`app/rag/`)** —
- `ingest.py`: KB `.md` → chunk (CHUNK_SIZE=500, OVERLAP=100) → embed → ChromaDB collection `pnb_kb`. Run: `.venv/bin/python -m app.rag.ingest` (3 files → 9 chunks).
- `retriever.py`: `retrieve(query, k=3)` → top-k chunks + source + L2 distance (kam = zyada similar).
- `test_rag.py`: 7 hands-on examples. Run: `python -m app.rag.test_rag <n|all>`. #6 = known limitation (transliterated formal Hindi "griha rin"), #7 = out-of-domain (credit card KB mein nahi).
- `knowledge_base/`: savings_account.md, loans.md, complaints.md.

## 8. Key learnings (interview-ready)
- **Embeddings semantic hote hain** (meaning, keyword nahi). Eval se pakda: English-only model Hinglish pe fail → multilingual model. Model native Devanagari + casual Hinglish samajhta hai, par *pure transliterated formal Hindi* pe kamzor (mitigation: query ko Devanagari transliterate / bilingual KB).
- **Chunking retrieval quality affect karta hai:** naive fixed-size se "home loan interest" ka sahi chunk #2 pe aaya, #1 pe personal/car loan. → `k>1` retrieve karo; heading-aware/semantic chunking = future improvement.
- **Out-of-domain queries** bhi chunk return karte hain (high distance) → real system mein **distance threshold** lagao warna LLM ko galat context milega.
- **Pydantic validation** declarative — galat POST body auto 422, business logic clean.

## 9. NEXT (Step 3: LangGraph multi-agent flow — project ka dil)
Teach LangGraph basics first (state, nodes, edges, conditional routing). Likely order:
1. `app/core/llm_client.py` — OpenRouter client (`claude-api` skill dekho; user ko `.env` mein `OPENROUTER_API_KEY` daalni hogi)
2. Supervisor/router agent — intent classification (query vs complaint vs transaction)
3. RAG agent — retriever.py + LLM → grounded answer with citations
4. Tool agent — mock_bank APIs call kare
5. Human-in-the-loop node — sensitive actions (fund transfer) pe approval
6. `app/agents/graph.py` — sabko wire karo

---
*Yeh file repo ke saath travel karti hai (git). Naye system pe: `git clone` → `.venv` banao →
`pip install -r requirements.txt` → yeh file mujhe padhne ko bolo → NEXT se continue.*
