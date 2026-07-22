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
**Frontend (Streamlit) ✅ (ask() ke upar chat UI, demoable) →
**4. memory + slot-filling ✅ → guardrails ← ABHI YAHAN → human-in-loop** → 5. observability (Langfuse) → 6. evaluation (RAGAS) + Docker deploy

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
| `1e40c53` | **graph.py** (3.6) — full multi-agent wiring (Step 3 COMPLETE) |
| `ee5f5d6` | **Streamlit frontend** — chat UI over `ask()` + streamlit dep |
| _(is commit)_ | **Memory + slot-filling (4.0)** — MemorySaver checkpointer + `ask(query, thread_id)` + slot-filling; per-session thread_id in Streamlit; guardrails/human-loop plan doc |

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
- `graph.py` ✅ (3.6 + 4.0): `build_graph()` → State `{query,intent,answer,sources,pending_intent,pending_query}`; nodes supervisor/rag/tool; conditional edge (faq→rag, baaki→tool). **`ask(query, thread_id="default")` = single entry point.** **Step 3 COMPLETE.**
  - ✅ **4.0 MEMORY + SLOT-FILLING (KNOWN GAP FIXED):** ab `graph.compile(checkpointer=MemorySaver())` → State per `thread_id` PERSIST. supervisor: `pending_intent` set ho to re-classify SKIP (naya message = pending flow ka jawab). tool_node: slot (`REQUIRED_SLOT` se) missing → prompt + `pending_intent`/`pending_query` yaad; mile (prior+ab wala text jod ke) → tool chalao + pending clear. **Verified:** bot ne "account number bataiye" maanga → user ne AKELA `1111000011110000` bheja → balance mil gaya (pehle `faq` misroute hota tha). Thread isolation bhi pass. Streamlit: per-session `thread_id` (uuid) → sessions ki memory alag.

**Frontend (`frontend/streamlit_app.py`)** ✅ — Streamlit chat UI over `ask()`. `st.chat_input`/`st.chat_message`, history `st.session_state` me (Streamlit har interaction pe script RERUN karta). Har jawab ke saath intent + sources caption (transparency). Top pe project-root `sys.path` me daala (script frontend/ se run hota). Run: `.venv/bin/streamlit run frontend/streamlit_app.py --server.port 8501`. Verified: server boots, health `ok`. Tool queries ke liye mock_bank (8001) ON chahiye.

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
- **Backend/frontend separation:** Streamlit UI sirf `ask()` call karti — poora agent logic backend me. Kal React laga do, `ask()` same rahega. Streamlit script har interaction pe top-se-neeche RERUN hota → mutable state `st.session_state` me rakhni padti (warna chat history reset ho jaati).
- **Conversational memory + slot-filling (4.0):** stateless agent multi-turn me tootta (bot ne account no. maanga, akela number aaya → intent-signal nahi → misroute). Fix = LangGraph **checkpointer** (`MemorySaver`) + **`thread_id`** → State turns ke beech persist. **Slot-filling** = explicit state machine: `pending_intent` set karke "kis field ka intezaar" yaad rakho, agle turn re-classify skip karke flow resume. Interview: (a) checkpointer hi human-in-the-loop `interrupt()` ke liye bhi neev hai; (b) `thread_id` = per-conversation isolation (multi-user safe); (c) MemorySaver in-memory (prod: SqliteSaver/DB).

## 9. NEXT

### Step 4 — Memory/slot-filling ✅ → Guardrails ← ABHI YAHAN → Human-in-the-loop
(Detailed plan: `.claude/plans/resilient-knitting-sun.md`. Step-by-step, confirm karke aage.)

**4.0 Conversational memory + slot-filling ✅ DONE** — MemorySaver checkpointer + `ask(query, thread_id)` + slot-filling (`pending_intent`/`pending_query`). Detail + verification §7 graph.py me. Learning §8 me.

**4.1 Guardrails (`app/guardrails/`) ← ABHI YEH**
- **(a) Prompt-injection** — `prompt_injection.py`: `check_injection(query)->bool` (regex/keyword: "ignore previous instructions", "you are now", "reveal system prompt", etc.). Graph me naya `guardrail_node` (START ke baad, supervisor se pehle); flag → `blocked=True` + refusal → seedha END (LLM/tool skip).
- **(b) PII filter** — `pii.py`: `mask_pii(text)` (16-digit account, phone, PAN, card → masked). **Decision:** PII sirf LLM-input + (Step 5) logs me mask; tool_agent RAW query par regex extract karta rahe (asli number API ke liye chahiye). Supervisor + rag_agent ke LLM calls me `mask_pii()` lagao.
- **Kyun:** defense-in-depth — input sanitization at trust boundary + PII minimization (LLM/3rd-party ko zaroorat se zyada mat do).

**4.2 Human-in-the-loop (3.5 defer kiya tha) — fund transfer + approval gate**
- mock_bank: `TransferIn` + `POST /transfer` (accounts valid? balance kaafi? → debit/credit → `{transfer_id,status,new_balance}`; 404/400 errors).
- supervisor: `INTENTS` me `transfer` add. tool_agent: `handle_transfer(query)` (from/to account + amount extract; multi-slot).
- graph: transfer + slots ready → LangGraph `interrupt()` se ruko → human "haan/nahi" (`Command(resume=...)`) → execute/cancel. (4.0 ka checkpointer isi ke liye tha.)
- streamlit: interrupt aane par confirmation UI + resume.
- **Kyun:** irreversible action pe human-in-the-loop = agentic safety core pattern; `interrupt()` = durable pause (state save → human input → resume).

### Break ke baad — quick restart checklist
- Background servers band ho gaye honge → dobara chalao (alag terminals):
  - `.venv/bin/uvicorn mock_bank.mock_banking_api:app --port 8001`
  - `.venv/bin/streamlit run frontend/streamlit_app.py --server.port 8501`
- Windows machine pe kaam kiya ho to pehle `git pull` (is Linux repo se sync).

### Baaki
- Step 5 observability (Langfuse) → 6 eval (RAGAS) + Docker deploy.

**Credits reminder:** OpenRouter balance kam hai — test karte waqt chhota `max_tokens`, ya Gemini free pe switch (llm_client me base_url+model swap).

---
*Yeh file repo ke saath travel karti hai (git). Naye system pe (Linux/mac ya Windows): `git clone` →
**one-command setup**: `bash setup.sh` (Linux/mac) ya `.\setup.ps1` (Windows) — ye venv + deps + .env +
model download (~470MB, open internet chahiye) + ingest sab kar deta hai (idempotent) → `.env` me
`OPENROUTER_API_KEY` daalo → yeh file mujhe padhne ko bolo → NEXT se continue. (Detailed steps README.md me.)*
