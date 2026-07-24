"""
Supervisor / Router Agent
=========================
Multi-agent flow ka pehla dimaag: user ki query dekho aur decide karo ise
kaunsa specialist agent handle karega. Ye "intent classification" hai.

Keyword-matching kyun NAHI: "mere paise kat gaye but transaction fail" me
'complaint' shabd nahi hai, par matlab complaint ka hai. LLM MEANING samajhta
hai, isliye classify LLM se karwate hain.

Baad me (graph.py) is intent ko ek conditional-edge padhega aur sahi node par
bhej dega. Abhi ye standalone testable hai.

Test:
    .venv/bin/python -m app.agents.supervisor
"""

from app.core.llm_client import chat
from app.guardrails.pii import mask_pii

# Jitne intents hum handle kar sakte hain (state me isi me se ek jayega).
INTENTS = {
    "balance": "account balance ya account details dekhna",
    "complaint": "koi shikayat/dispute (paise kat gaye, fraud, galat charge, service issue)",
    "loan_status": "loan application ya uska status/eligibility",
    "faq": "general sawaal (policies, charges, interest rate, kaise karein) — baaki sab",
}

# LLM ko diya jaane wala instruction. Note: 'sirf ek label' + 'kuch aur mat likho'
# taaki output parse-karna aasan rahe (cheap structured-output trick).
_SYSTEM_PROMPT = (
    "Tum ek bank assistant ka router ho. User ki query padho aur usse THIK EK "
    "category me daalo. Sirf category ka naam (lowercase) likho — aur kuch nahi, "
    "koi explanation nahi.\n\n"
    "Categories:\n"
    + "\n".join(f"- {name}: {desc}" for name, desc in INTENTS.items())
    + "\n\nAgar saaf na ho, to 'faq' do."
)


def classify_intent(query: str) -> str:
    """Query ka intent laao — INTENTS me se ek label.

    LLM kabhi extra text ya galat label de sakta hai → normalize + validate
    karte hain, aur match na ho to safe fallback 'faq'.

    PII: classifier ko sirf MEANING chahiye (asli account/phone number nahi) →
    LLM ko masked query bhejte hain (data minimization). Masked number ka intent
    same rehta hai (e.g. "************0000 ka balance" → abhi bhi 'balance').
    """
    raw = chat(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": mask_pii(query)},
        ],
        temperature=0,      # classification = deterministic chahiye, creative nahi
        max_tokens=32,      # label chhota hai, par itni headroom chahiye — 10 pe
                            # model kabhi khaali output de deta tha (budget starve).
    )

    # Normalize: lowercase + spaces/punctuation trim.
    label = raw.strip().lower().strip(".!\"'")

    # Validate: agar LLM ne kuch aur bol diya, to guess karo ya faq fallback.
    if label in INTENTS:
        return label
    # kabhi-kabhi LLM "intent: complaint" jaisa de → andar se dhoondo
    for name in INTENTS:
        if name in label:
            return name
    return "faq"


if __name__ == "__main__":
    # Alag-alag tarah ki queries — dekho routing sahi ho raha ya nahi.
    tests = [
        "mera account balance kitna hai",           # balance
        "mere paise kat gaye par transaction fail",  # complaint (koi keyword nahi!)
        "home loan ka status batao",                 # loan_status
        "savings account ka interest rate kya hai",  # faq
        "ATM se paisa nikla nahi par account se cut gaya",  # complaint
        "account 1111000011110000 ka balance batao",  # balance — PII masked, phir bhi sahi
    ]
    for q in tests:
        print(f"{classify_intent(q):12}  <-  {q}")
