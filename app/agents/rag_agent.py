"""
RAG Agent
=========
`faq`-type query ka GROUNDED jawab: retriever se relevant chunks laao, phir LLM ko
SIRF usi context se jawab dene ko bolo (+ source citation).

Kyun grounding: LLM apni training-memory se jawab de to purana/galat ho sakta
(hallucination). Retrieved docs = official, fresh context → LLM usi pe jawab de →
bharosa + citation (user dekh sakta jawab kahan se aaya).

Do safety layers:
  1. Distance threshold (retriever) — irrelevant chunk aaye hi na.
  2. "Context me na ho to bolo pata nahi" (prompt) — LLM banaye na.

Test:
    .venv/bin/python -m app.agents.rag_agent
"""

from app.core.llm_client import chat
from app.rag.retriever import retrieve

MAX_DISTANCE = 20.0   # 2.5 me measure kiya: in-domain ~12-17, OOD ~29 → beech me 20
TOP_K = 3

_SYSTEM_PROMPT = (
    "Tum PNB (Punjab National Bank) ke helpful assistant ho. Neeche CONTEXT diya "
    "hai jo bank ke official documents se aaya hai. SIRF is context ke aadhaar par "
    "Hinglish me jawab do. Agar jawab context me nahi hai to saaf bolo: "
    "'Mujhe iski jaankari nahi hai' — apni taraf se kuch mat banao."
)


def answer_faq(query: str) -> dict:
    """Grounded FAQ answer + sources laao.

    Return: {"answer": str, "sources": list[str], "grounded": bool}
      grounded=False → koi relevant context nahi mila (LLM call bhi nahi kiya).
    """
    hits = retrieve(query, k=TOP_K, max_distance=MAX_DISTANCE)

    # RAG fallback: threshold ke baad kuch nahi bacha → LLM ko bulao hi mat.
    # (credits bachte hain + hallucination ka mauka hi nahi milta)
    if not hits:
        return {
            "answer": "Mujhe iski jaankari nahi hai. Kripya PNB helpline ya branch se sampark karein.",
            "sources": [],
            "grounded": False,
        }

    # Context = numbered chunks with source (LLM aur user dono ke liye citation).
    context = "\n\n".join(
        f"[{i + 1}] (source: {h['source']})\n{h['text']}" for i, h in enumerate(hits)
    )
    answer = chat(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nSAWAAL: {query}"},
        ],
        temperature=0.2,   # thoda natural, par mostly context-bound
        max_tokens=300,    # ek FAQ jawab ke liye kaafi
    )

    # Unique source files (order preserve) — citation dikhane ke liye.
    sources = list(dict.fromkeys(h["source"] for h in hits))
    return {"answer": answer, "sources": sources, "grounded": True}


if __name__ == "__main__":
    tests = [
        "savings account ka minimum balance kitna hai",   # in-domain → grounded
        "credit card ke reward points kaise milte hain",  # OOD → fallback (no LLM)
    ]
    for q in tests:
        print(f"\nSAWAAL: {q}")
        res = answer_faq(q)
        print(f"  grounded={res['grounded']} | sources={res['sources']}")
        print(f"  JAWAB: {res['answer']}")
