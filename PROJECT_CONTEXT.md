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
- Python **3.13.3**, venv at **`venv/`** (NOTE: `.venv` NAHI — folder ka naam `venv` hai). **Claude Code ka Bash har command fresh shell mein chalata hai** → `source venv/bin/activate` persist NAHI hota. Hamesha direct use karo: Windows pe `venv/Scripts/python.exe`, Linux/mac pe `venv/bin/python`.
- Install reproduce: `venv/Scripts/python.exe -m pip install -r requirements.txt` (chromadb + sentence-transformers ka `tokenizers` version warning aayega — **benign**, runtime pe kuch nahi tootta).
- **git identity (repo-local) ab GitHub noreply hai:** name `LakshyaChauhanProgramming`, email `210909994+LakshyaChauhanProgramming@users.noreply.github.com` → commits GitHub profile se link + real email chhupi. (Purani `lakshya.chauhan@programming.com` replace kar di; saare commits re-authored.) GitHub repo LIVE (private): https://github.com/LakshyaChauhanProgramming/pnb_workflow_agent
  - **Linux dev machine se SSH auth set hai** (`~/.ssh/id_rsa.pub` GitHub pe add) → remote `origin` = `git@github.com:...`. HTTPS/`gh` nahi. Windows se banayi cross-platform repo is Linux repo me merge ho chuki (unrelated history → origin ko canonical base banaya).
  - NOTE: is Linux box pe abhi bhi purana `.venv/` (Python 3.12.3) use ho raha (doc ka `venv/` Windows-side hai). Dono gitignored.
- **Offline embedding model:** corporate network par `huggingface.co` block hai (SSL handshake fail; PyPI chalta hai). Model `paraphrase-multilingual-MiniLM-L12-v2` ek baar khule network/EC2 se download karke `app/rag/models/` me daal diya (gitignored, ~470MB). `app/rag/embed_model.py` local folder detect karke `HF_HUB_OFFLINE=1` set karta hai → sab offline chalta hai. Naya machine pe: `python download_model.py` (khule net par) ya folder copy karo.
- **Windows console cp1252 hai** → `print()` me emoji/unicode (jaise `✅`) `UnicodeEncodeError` deta hai. Plain ASCII use karo (ingest.py se `✅` hata diya).

## 5. Folder structure (scaffolded)
```
app/           main.py, api/, agents/[supervisor, rag_agent, tool_agent, human_loop, graph.py],
               tools/, rag/[ingest.py, retriever.py, embed_model.py, test_rag.py, knowledge_base/, models/(gitignored)],
               guardrails/[pii_filter, prompt_injection_check], memory/, observability/, core/[config, llm_client]
mock_bank/     mock_banking_api.py  (ALAG package — external backend decouple karne ke liye, app/ se bahar)
evaluation/    eval_dataset.jsonl, run_ragas_eval.py
frontend/      streamlit_app.py
docker/ · tests/ · .env.example · requirements.txt · README.md · .gitattributes · download_model.py · setup.sh · setup.ps1 (root)
```
Package dirs mein `__init__.py`, data dirs mein `.gitkeep`.

## 6. Build order (plan)
1. mock_banking_api.py ✅ → 2. RAG (ingest + retriever) ✅ → 2.5 RAG distance threshold ✅ →
**3. LangGraph flow ← ABHI YAHAN** (3.1 llm_client ✅ | 3.2 supervisor node ← NEXT | 3.3 rag_agent | 3.4 tool_agent | 3.5 human-loop | 3.6 graph.py) →
4. guardrails + human-in-loop → 5. observability (Langfuse) → 6. evaluation (RAGAS) + Docker deploy

## 7. DONE tak (git — repo `main` par, GitHub par pushed)
> NOTE: is session me Windows repo + Linux repo merge huye → history re-authored (purane hashes invalid). Commits ab noreply identity par. GitHub: LakshyaChauhanProgramming/pnb_workflow_agent

| Commit | Kya |
|---|---|
| `13f8c3f` | **Initial** — mock banking API + RAG pipeline + offline model support + scaffold |
| `67694d6` | cross-platform setup scripts (setup.sh/ps1, download_model.py, .gitattributes) + docs |
| `5ac0bd0` | CLAUDE.md (Claude Code guidance) |
| _(is commit)_ | **RAG distance threshold** + **embedding_export** + **LangGraph 3.1 (llm_client)** + deps (langgraph/openai/dotenv) + PROJECT_CONTEXT update |

**Mock bank (`mock_bank/mock_banking_api.py`)** — FastAPI, in-memory fake data.
Endpoints: `GET /`, `/health`, `/accounts/{acct}`, `/accounts/{acct}/balance`, `/loans/{id}/status`,
`POST /complaints` (Pydantic `ComplaintIn`, 201), `GET /complaints/{id}`.
Fake data: accounts `1111000011110000` (Amit), `2222000022220000` (Priya); loans `LN1001`, `LN1002`.
Run: `venv/Scripts/python.exe -m uvicorn mock_bank.mock_banking_api:app --port 8001` → docs at `/docs`.

**RAG (`app/rag/`)** —
- `ingest.py`: KB `.md` → chunk (CHUNK_SIZE=500, OVERLAP=100) → embed → ChromaDB collection `pnb_kb`. Run: `venv/Scripts/python.exe -m app.rag.ingest` (3 files → 9 chunks). Model `embed_model.py` se resolve hota hai (offline-friendly).
- `retriever.py`: `retrieve(query, k=3, max_distance=None)` → top-k chunks + source + L2 distance (kam = zyada similar). **Distance threshold ADD ho gaya** (2.5 done): `max_distance` diya to door chunks drop, khaali `[]` = "no relevant context". Measured: in-domain ~12-17, OOD tak ~29 → threshold ~20 (squared-L2). `__main__` demo threshold=20 dikhata hai.
- `test_rag.py`: 7 hands-on examples. Run: `python -m app.rag.test_rag <n|all>`. #6 = known limitation (transliterated formal Hindi "griha rin"), #7 = out-of-domain (credit card KB mein nahi).
- `export_embeddings.py`: Chroma vectors → `embedding_export/{vectors,metadata}.tsv` (gitignored) → TensorFlow Embedding Projector (projector.tensorflow.org) me 2D/3D visualize. Run: `python -m app.rag.export_embeddings`.
- `knowledge_base/`: savings_account.md, loans.md, complaints.md.

**Core (`app/core/llm_client.py`)** — OpenRouter client (OpenAI SDK, `base_url` swap). `chat(messages, model=None, temperature=0.3, max_tokens=1024)` → text. Secrets `.env` se (dotenv). Test: `python -m app.core.llm_client`. **WORKING** (Claude Sonnet 5 ne Hinglish jawab diya). ⚠️ OpenRouter account me credits KAM hain — dev ke waqt dhyaan; khatam huye to Gemini free pe switch (abstraction ki wajah se 2-line kaam).

**LangGraph** — installed (`langgraph==1.2.9`). Hello-world graph (supervisor pattern, keyword-classifier, no LLM) scratchpad me banaya-chalaya (mechanics samajhne ke liye; repo me nahi). Asli agents `app/agents/` me 3.2 se banenge.

## 8. Key learnings (interview-ready)
- **Embeddings semantic hote hain** (meaning, keyword nahi). Eval se pakda: English-only model Hinglish pe fail → multilingual model. Model native Devanagari + casual Hinglish samajhta hai, par *pure transliterated formal Hindi* pe kamzor (mitigation: query ko Devanagari transliterate / bilingual KB).
- **Embeddings ka math intuition** (interview-ready): text → high-dim space me point (yahan 384-dim). Similar meaning = paas-paas points. Similarity naapte hain **cosine similarity** (`A·B/(|A||B|)`, angle-based, -1..+1) ya **L2 distance** (Chroma default; kam = similar). Directions rishte encode karti hain (`king−man+woman≈queen`). Numbers self-supervised training se aate hain (distributional hypothesis: "same context = same meaning"); sentence-transformers isko **contrastive learning** (paraphrase pairs paas, alag door) se refine karta hai. Zaroori: query aur docs **same model** se embed karo warna spaces align nahi honge.
- **Chunking retrieval quality affect karta hai:** naive fixed-size se "home loan interest" ka sahi chunk #2 pe aaya, #1 pe personal/car loan. → `k>1` retrieve karo; heading-aware/semantic chunking = future improvement.
- **Out-of-domain queries** bhi chunk return karte hain (high distance) → real system mein **distance threshold** lagao warna LLM ko galat context milega.
- **Pydantic validation** declarative — galat POST body auto 422, business logic clean.
- **Distance threshold (implemented):** Chroma default = **squared L2** (bounded NAHI, unbounded — humare KB me ~12-30). `max_distance` gate se OOD garbage LLM tak nahi jaata (empty `[]` = honest "pata nahi"). **Trade-off:** strict threshold → sahi jawab bhi block (false negative); loose → garbage pass (false positive) — beech me tune. Squared-L2 se clean separation mushkil (mausam/pizza slip through) → **cosine distance (0-2)** future upgrade.
- **LangGraph mental model (4 cheezein):** State (shared dict jo flow karti), Node (function jo state update kare), Edge (A→B), Conditional edge (state dekh ke route = supervisor). Nodes sirf changed keys return karte, LangGraph merge karta. Interview: supervisor = conditional-edge + routing function.
- **LangChain vs LangGraph:** LangChain = seedhi "chains" (linear). LangGraph = graph (loops/branching/human-in-loop/state) — usi company ka, LangChain ke upar; multi-agent ke liye standard. RAG humne haath se banaya (LangChain shortcuts nahi) taaki internals samajh aayein.
- **LLM API basics:** stateless request-response (har baar poori history bhejo); `messages` roles system/user/assistant; `temperature` low=consistent. **OpenRouter gotcha:** `max_tokens` ke hisaab se credits UPFRONT reserve hote → bina set kiye 402 (humne 1024 set kiya). Provider abstraction (`llm_client.py`) alag rakhne se swap trivial.

## 9. NEXT

### 9.0 ABHI KAR RAHE: Step 3.2 — Supervisor node (LLM se intent classification)
**Kya:** ek LangGraph node jo user query ko `balance` / `complaint` / `faq` (aur baad me `transaction`) me classify kare — **LLM se, keyword se nahi**. Phir conditional edge us intent pe route kare.
**Kyun:** "paise kat gaye galat" jaisi query keyword-match se miss hoti; LLM meaning samajhta. Hello-world graph me keyword `if/else` tha — usko LLM se replace karna.
**Kaise:** (1) `app/agents/supervisor.py` — `chat()` (llm_client) ko ek structured prompt + query do → ek label wapas; (2) State me `route` set; (3) conditional edge se sahi agent node pe. Prompt me labels + "sirf label do" instruction; kam max_tokens (credits bachao).

### Baaki Step 3 (LangGraph — project ka dil)
- 3.1 `app/core/llm_client.py` ✅ DONE (OpenRouter, working)
- 3.2 Supervisor/router — intent classification ← ABHI
- 3.3 RAG agent — retriever.py + LLM → grounded answer with citations (distance threshold use karega)
- 3.4 Tool agent — mock_bank APIs call kare
- 3.5 Human-in-the-loop node — sensitive actions (fund transfer) pe approval
- 3.6 `app/agents/graph.py` — sabko wire karo

**Credits reminder:** OpenRouter balance kam hai — agents test karte waqt chhota `max_tokens`, ya Gemini free pe switch (llm_client me base_url+model swap).

---
*Yeh file repo ke saath travel karti hai (git). Naye system pe (Linux/mac ya Windows): `git clone` →
**one-command setup**: `bash setup.sh` (Linux/mac) ya `.\setup.ps1` (Windows) — ye venv + deps + .env +
model download (~470MB, open internet chahiye) + ingest sab kar deta hai (idempotent) → `.env` me
`OPENROUTER_API_KEY` daalo → yeh file mujhe padhne ko bolo → NEXT se continue. (Detailed steps README.md me.)*
