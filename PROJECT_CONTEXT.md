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
3. **LangGraph flow ✅ COMPLETE** (3.1 llm_client ✅ | 3.2 supervisor ✅ | 3.3 rag_agent ✅ | 3.4 tool_agent ✅ | 3.6 graph.py ✅ | 3.5 human-loop = DEFERRED) →
**Frontend (Streamlit) ← ABHI YAHAN** (ask() ke upar chat UI, demoable) →
4. guardrails + human-in-loop → 5. observability (Langfuse) → 6. evaluation (RAGAS) + Docker deploy

> ⚠️ **3.5 human-in-the-loop SKIP nahi kiya — DEFER kiya** (learning ke liye koi step chhoote na). Iska asli matlab tab banta hai jab koi sensitive/irreversible action ho (jaise fund transfer). Abhi tools read + low-risk (balance/loan/complaint) hain. Jab transfer-tool add karenge (Step 4 guardrails ke saath), approval-gate wahan lagega.

## 7. DONE tak (git — repo `main` par, GitHub par pushed)
> NOTE: is session me (a) Windows+Linux repo merge → re-authored, (b) `Co-Authored-By: Claude` trailer SAB commits se strip kiya (user request) → history force-push hui, hashes badalte rahe. Commits noreply identity par. GitHub: LakshyaChauhanProgramming/pnb_workflow_agent

| Commit | Kya |
|---|---|
| `c78e30d` | **Initial** — mock banking API + RAG pipeline + offline model + scaffold |
| `a419bbd` | cross-platform setup (setup.sh/ps1, download_model.py, .gitattributes) |
| `dcd5fe1` | CLAUDE.md |
| `74a23d4` | RAG distance threshold + embedding_export + LangGraph 3.1 (llm_client) + deps |
| `9a96b5f` | **Supervisor** (3.2) — LLM intent classify + ChromaDB telemetry fix + llm_client None-guard |
| `faf8508` | **RAG agent** (3.3) — grounded FAQ answer + citations |
| `d6f4d2a` | **Tool agent** (3.4) — mock_bank HTTP calls (balance/loan/complaint) + httpx pin |
| _(is commit)_ | **graph.py** (3.6) — full multi-agent wiring (Step 3 COMPLETE) + PROJECT_CONTEXT update |

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

**LangGraph** — installed (`langgraph==1.2.9`). Hello-world graph (supervisor pattern, keyword-classifier, no LLM) scratchpad me banaya-chalaya (mechanics samajhne ke liye; repo me nahi). Asli agents `app/agents/` me abhi as standalone functions bane hain; graph.py (3.6) me wire honge.

**Agents (`app/agents/`)** —
- `supervisor.py` ✅ (3.2): `classify_intent(query)` → LLM se ek label (`balance`/`complaint`/`loan_status`/`faq`). **Guardrail:** normalize + validate (allowlist `INTENTS`) + safe fallback `faq`. `temperature=0, max_tokens=32` (10 pe empty output = starvation bug). Test 5/5 sahi ("paise kat gaye" bina keyword → complaint). Router = **retrieval-vs-tool** decide karta.
- `rag_agent.py` ✅ (3.3): `answer_faq(query)` → `retrieve(threshold)` → khaali to LLM bulao mat (fallback, no-hallucination) → warna numbered context+source LLM ko (grounding prompt) → answer. Returns `{answer, sources, grounded}`. Live proof mila: OOD query threshold (layer1) se nikli par prompt-grounding (layer2) ne "pata nahi" bolwaya → **defense-in-depth**.
- `tool_agent.py` ✅ (3.4): `handle_tool(intent, query)` → `balance`/`loan_status`/`complaint` ke liye mock_bank HTTP APIs call (`httpx`). Regex se id extract (16-digit acct, `LN\d+`). Guards: id missing→maango, 404→friendly, service-down (`RequestError`)→graceful. Test 5/5 sahi. (mock_bank alag process ON hona chahiye.)
- `graph.py` ✅ (3.6): `build_graph()` → State `{query,intent,answer,sources}`; nodes supervisor/rag/tool; conditional edge (faq→rag, baaki→tool). **`ask(query)` = single entry point** (UI isi ko call karega). End-to-end test 4/4 sahi. **Step 3 COMPLETE — project ka dil ready.**

## 8. Key learnings (interview-ready)
- **Embeddings semantic hote hain** (meaning, keyword nahi). Eval se pakda: English-only model Hinglish pe fail → multilingual model. Model native Devanagari + casual Hinglish samajhta hai, par *pure transliterated formal Hindi* pe kamzor (mitigation: query ko Devanagari transliterate / bilingual KB).
- **Embeddings ka math intuition** (interview-ready): text → high-dim space me point (yahan 384-dim). Similar meaning = paas-paas points. Similarity naapte hain **cosine similarity** (`A·B/(|A||B|)`, angle-based, -1..+1) ya **L2 distance** (Chroma default; kam = similar). Directions rishte encode karti hain (`king−man+woman≈queen`). Numbers self-supervised training se aate hain (distributional hypothesis: "same context = same meaning"); sentence-transformers isko **contrastive learning** (paraphrase pairs paas, alag door) se refine karta hai. Zaroori: query aur docs **same model** se embed karo warna spaces align nahi honge.
- **Chunking retrieval quality affect karta hai:** naive fixed-size se "home loan interest" ka sahi chunk #2 pe aaya, #1 pe personal/car loan. → `k>1` retrieve karo; heading-aware/semantic chunking = future improvement.
- **Out-of-domain queries** bhi chunk return karte hain (high distance) → real system mein **distance threshold** lagao warna LLM ko galat context milega.
- **Pydantic validation** declarative — galat POST body auto 422, business logic clean.
- **Distance threshold (implemented):** Chroma default = **squared L2** (bounded NAHI, unbounded — humare KB me ~12-30). `max_distance` gate se OOD garbage LLM tak nahi jaata (empty `[]` = honest "pata nahi"). **Trade-off:** strict threshold → sahi jawab bhi block (false negative); loose → garbage pass (false positive) — beech me tune. Squared-L2 se clean separation mushkil (mausam/pizza slip through) → **cosine distance (0-2)** future upgrade.
- **LangGraph mental model (4 cheezein):** State (shared dict jo flow karti), Node (function jo state update kare), Edge (A→B), Conditional edge (state dekh ke route = supervisor). Nodes sirf changed keys return karte, LangGraph merge karta. Interview: supervisor = conditional-edge + routing function.
- **LangChain vs LangGraph:** LangChain = seedhi "chains" (linear). LangGraph = graph (loops/branching/human-in-loop/state) — usi company ka, LangChain ke upar; multi-agent ke liye standard. RAG humne haath se banaya (LangChain shortcuts nahi) taaki internals samajh aayein.
- **LLM API basics:** stateless request-response (har baar poori history bhejo); `messages` roles system/user/assistant; `temperature` low=consistent. **OpenRouter gotcha:** `max_tokens` ke hisaab se credits UPFRONT reserve hote → bina set kiye 402 (humne set kiya). Provider abstraction (`llm_client.py`) alag rakhne se swap trivial.
- **Guardrail = validation + fallback (supervisor):** LLM output UNTRUSTED maano → normalize (caps/space/punctuation) → validate against allowlist → safe fallback. Guarantee: hamesha ek valid intent, downstream crash/misroute nahi. `faq` safe default kyun: RAG general handler, koi khatarnak side-effect nahi (complaint/transaction galti se trigger nahi hoti).
- **Grounding + defense-in-depth (rag_agent):** LLM ko SIRF retrieved context se jawab dene ka prompt → hallucination kam + citation. **Live:** ek OOD query threshold (layer1) se nikal gayi par prompt-grounding (layer2) ne "pata nahi" bolwaya → multiple guardrails = no single point of failure.
- **max_tokens starvation bug:** classifier me `max_tokens=10` → model label emit karne se pehle ruk gaya → empty output → galat fallback. Output ko headroom do; over-optimize mat karo.
- **ChromaDB 0.5.23 telemetry warning:** `Settings(anonymized_telemetry=False)` + env-var dono ignore → asli fix `logging.getLogger("chromadb.telemetry.product.posthog").setLevel(CRITICAL)` (message `logging.error` se aata). Lesson: source pe fix na ho to logging layer pe suppress.
- **Agent-calls-tools pattern (tool_agent):** router → intent → tool (external system ka wrapper). RAG (docs) vs Tool (live APIs) — dono ek hi graph me = hybrid knowledge + action agent. mock_bank alag process = separation of concerns (real backend swap trivial).
- **Graph wiring (3.6):** standalone-tested nodes ko LangGraph ne conditional-edge se connect kiya — supervisor route karta, State har node me travel karti (partial-update merge). Composition + loose coupling: har piece pehle alag test hua, phir graph ne bas join kar diya. `ask()` = single entry point → backend UI-ready.

## 9. NEXT

### 9.0 ABHI KAR RAHE: Frontend — Streamlit chat UI
**Kya:** `frontend/streamlit_app.py` — ek simple chat interface jo `app.agents.graph.ask(query)` call kare aur jawab (+ intent + sources) dikhaye.
**Kyun:** ab tak sab CLI se test hua. Streamlit se project DEMOABLE ban jata — resume/interview me live dikha sakte. Streamlit = pure Python, UI banane ka fastest tarika (React baad me).
**Kaise:** (1) `pip install streamlit`; (2) `st.chat_input` + `st.chat_message` se chat loop; (3) har user msg pe `ask()` call, `st.session_state` me history rakho; (4) intent + sources bhi dikhao (transparency). NOTE: tool queries ke liye mock_bank alag process ON hona chahiye. Run: `streamlit run frontend/streamlit_app.py`.

### Deferred / baaki
- **3.5 Human-in-the-loop** — DEFER (build order me note dekho): fund-transfer jaisa sensitive action add karte waqt approval-gate lagega (Step 4 ke saath).
- Step 4 guardrails (PII + prompt-injection) → 5 observability (Langfuse) → 6 eval (RAGAS) + Docker deploy.

**Credits reminder:** OpenRouter balance kam hai — test karte waqt chhota `max_tokens`, ya Gemini free pe switch (llm_client me base_url+model swap).

---
*Yeh file repo ke saath travel karti hai (git). Naye system pe (Linux/mac ya Windows): `git clone` →
**one-command setup**: `bash setup.sh` (Linux/mac) ya `.\setup.ps1` (Windows) — ye venv + deps + .env +
model download (~470MB, open internet chahiye) + ingest sab kar deta hai (idempotent) → `.env` me
`OPENROUTER_API_KEY` daalo → yeh file mujhe padhne ko bolo → NEXT se continue. (Detailed steps README.md me.)*
