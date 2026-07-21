"""
RAG Practical Test / Playground
===============================
Yeh file SEEKHNE ke liye hai — retriever ko alag-alag tarah ke sawaalon par
chala ke dekho ki kaunse chunks aate hain aur kitne similar (distance) hain.

Pehle ingest chal chuki honi chahiye (collection 'pnb_kb' bani ho):
    python -m app.rag.ingest

Chalane ke tareeke:
    python -m app.rag.test_rag            # saare examples ki list dikhao (usage)
    python -m app.rag.test_rag 1          # sirf example #1 chalao
    python -m app.rag.test_rag 3          # sirf example #3 chalao
    python -m app.rag.test_rag all        # saare examples ek ke baad ek chalao

Har example ke saath ek "OBSERVE" note hai — wahi seekhne ka point hai.
DISTANCE: jitni KAM, utna zyada relevant (ChromaDB default L2 distance).
"""

import sys

from app.rag.retriever import retrieve

# Har example: sawaal + kitne chunks (k) + kya observe karna hai.
EXAMPLES = [
    {
        "query": "home loan ka interest rate kya hai?",
        "k": 2,
        "observe": "Seedha English/Hinglish sawaal. loans.md ka chunk top par aana chahiye, "
                   "distance kam. Yeh 'happy path' hai.",
    },
    {
        "query": "savings account pe kitna byaaj milta hai?",
        "k": 2,
        "observe": "Hinglish ('byaaj' = interest). Dekho model ko 'byaaj' samajh aaya kya — "
                   "savings_account.md aana chahiye, loans.md nahi.",
    },
    {
        "query": "complaint kaise register karun?",
        "k": 2,
        "observe": "Intent-based query. complaints.md ka 'kaise darj karein' chunk aana chahiye.",
    },
    {
        "query": "मिनिमम बैलेंस कितना रखना पड़ता है?",
        "k": 2,
        "observe": "Devanagari (Hindi script) query. Multilingual model ise achhe se samajhta hai — "
                   "savings_account.md ka minimum balance chunk aana chahiye.",
    },
    {
        "query": "ATM se paise nahi mile par account debit ho gaya, kya karun?",
        "k": 3,
        "observe": "Real-life scenario. failed_transaction / charge-back wale chunks aane chahiye "
                   "(complaints.md). Note karo top-3 mein kaun-kaun aaye.",
    },
    {
        "query": "griha rin par byaaj kitna hai",
        "k": 2,
        "observe": "KNOWN LIMITATION: pure transliterated formal Hindi. Model shayad galat/kamzor "
                   "match de (distance zyada). Yahi wo case hai jise eval ne pakda tha — "
                   "interview mein bolne layak. Mitigation: query ko Devanagari mein transliterate karna.",
    },
    {
        "query": "credit card ke reward points kaise redeem karein?",
        "k": 2,
        "observe": "OUT-OF-DOMAIN: KB mein credit card ke reward points hai hi nahi. "
                   "RAG phir bhi 'sabse paas ka' chunk laayega (distance ZYADA hogi). "
                   "Sabak: real system mein distance threshold lagate hain — warna irrelevant "
                   "context LLM ko galat jawab dilwa sakta hai.",
    },
]


def run_example(i: int) -> None:
    """1-based index se ek example chalao."""
    ex = EXAMPLES[i - 1]
    print("=" * 70)
    print(f"EXAMPLE {i}")
    print(f"QUERY   : {ex['query']}")
    print(f"OBSERVE : {ex['observe']}")
    print("-" * 70)
    hits = retrieve(ex["query"], k=ex["k"])
    for rank, hit in enumerate(hits, 1):
        # Chunk lamba ho sakta hai — pehle 120 chars dikha do.
        preview = hit["text"].replace("\n", " ")[:120]
        print(f"  #{rank}  distance={hit['distance']:<7} [{hit['source']}]")
        print(f"       {preview}...")
    print("=" * 70)
    print()


def usage() -> None:
    print(__doc__.strip())
    print("\nAvailable examples:")
    for i, ex in enumerate(EXAMPLES, 1):
        print(f"  {i}. {ex['query']}")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        usage()
        return

    arg = args[0].lower()
    if arg == "all":
        for i in range(1, len(EXAMPLES) + 1):
            run_example(i)
        return

    if arg.isdigit() and 1 <= int(arg) <= len(EXAMPLES):
        run_example(int(arg))
        return

    print(f"Galat argument: {arg!r}")
    print(f"Use: ek number 1-{len(EXAMPLES)}, ya 'all', ya khaali (usage ke liye).")


if __name__ == "__main__":
    main()
