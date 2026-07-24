"""
Guardrail (b) — PII masking
===========================
PII = Personally Identifiable Information (account number, phone, PAN, card).

Kyun mask karte hain? Humara LLM ek THIRD PARTY hai (OpenRouter -> Anthropic).
Usko sensitive data zaroorat se zyada mat bhejo — agar kahin log/breach ho to
masked data se nuksaan kam (data minimization; GDPR / India DPDP jaisa principle).

TRUST-BOUNDARY DECISION (yaad rakho):
  - MASK karo  -> supervisor + rag_agent ke LLM-input (unko asli number chahiye
                  hi nahi; woh sirf intent-classify / FAQ ke liye hain).
  - MASK MAT karo -> tool_agent RAW query par regex se asli account number nikaalta
                  hai kyunki wo mock_bank API ko bhejni hai. Wahan mask kiya to
                  balance/loan query kaam hi nahi karegi.

Ye NAIVE regex masker hai — pehli line of defense (cheap, deterministic, koi LLM
call nahi). Naye formats miss ho sakte hain -> defense-in-depth ka EK layer.

Design note (16-digit ambiguity): account number aur debit/credit card DONO
16-digit hote hain -> regex inhe distinguish nahi kar sakta. Isliye conservatively
DONO ko ek hi "16-digit" pattern se mask karte hain (last 4 digits visible).

Test:
    python -m app.guardrails.pii
"""

import re


# --- PII patterns (order matters: pehle zyada-specific/lambe match karo) ---
# 16-digit number (account ya card). \b se word-boundary — 16 se lambe digit-run
# me galti se match na ho. Last 4 digits visible rakhenge (masking me).
_ACCOUNT_OR_CARD = re.compile(r"\b(\d{12})(\d{4})\b")

# PAN: 5 letters + 4 digits + 1 letter (e.g. ABCDE1234F). Case-insensitive.
_PAN = re.compile(r"\b([A-Z]{5})[0-9]{4}([A-Z])\b", re.IGNORECASE)

# Indian phone: optional (+91 / 0) prefix + uska apna separator, phir 10 digits
# (6-9 se shuru). Last 4 visible. NOTE: separator `[\s-]?` ko prefix ke ANDAR
# rakha (poora prefix optional) — warna bina-code wale case me `[\s-]?` peeche ka
# space kha jaata tha ("phone 987..." -> "phone987..."). Interview: greedy/optional
# regex adjacent whitespace consume kar sakta — group boundaries dhyaan se.
_PHONE = re.compile(r"\b(?:(?:\+?91|0)[\s-]?)?([6-9]\d{5})(\d{4})\b")


def _mask_account_or_card(m: re.Match) -> str:
    # 12 digits -> '*', last 4 as-is.  e.g. 1111000011110000 -> ************0000
    return "*" * 12 + m.group(2)


def _mask_pan(m: re.Match) -> str:
    # First 5 letters visible, 4 middle digits masked, last letter visible.
    # e.g. ABCDE1234F -> ABCDE****F  (5 letters help detect it's a PAN)
    return f"{m.group(1)}****{m.group(2)}"


def _mask_phone(m: re.Match) -> str:
    # Last 4 digits visible, baaki masked. e.g. 9876543210 -> ******3210
    return "*" * 6 + m.group(2)


def mask_pii(text: str) -> str:
    """Text me se account/card, PAN, phone mask karke naya text lautao.

    Fail-safe: khaali/None input -> waisa hi (ya "") lautao, crash nahi.
    Order: 16-digit pehle (sabse specific length), phir PAN, phir phone —
    taaki chhote patterns lambe numbers ke andar galti se match na karein.
    """
    if not text:
        return text
    text = _ACCOUNT_OR_CARD.sub(_mask_account_or_card, text)
    text = _PAN.sub(_mask_pan, text)
    text = _PHONE.sub(_mask_phone, text)
    return text


if __name__ == "__main__":
    # Hands-on: PII mask ho, baaki text intact rahe.
    samples = [
        "mera account 1111000011110000 hai balance batao",
        "PAN ABCDE1234F aur phone 9876543210 note kar lo",
        "call me on +91 9123456789 ya 09123456789",
        "card 4111111111111111 se payment fail hui",
        "home loan ka interest rate kya hai",          # koi PII nahi -> unchanged
        "loan LN1001 ka status",                       # LN-id PII nahi -> unchanged
    ]
    for s in samples:
        print(f"  IN : {s}")
        print(f"  OUT: {mask_pii(s)}\n")
