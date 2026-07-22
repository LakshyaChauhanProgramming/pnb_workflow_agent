"""
Tool Agent
==========
`balance` / `loan_status` / `complaint` intents — ye documents (RAG) se nahi,
LIVE data/action se handle hote hain. Ye agent mock_bank ke HTTP APIs call karta hai.

Classic "agent calls tools" pattern: router decide karta kaunsa tool, tool =
external system (yahan mock_bank) ka ek patla wrapper. mock_bank ALAG process hai.

Pehle mock_bank chalao (alag terminal me):
    .venv/bin/uvicorn mock_bank.mock_banking_api:app --port 8001

Phir test:
    .venv/bin/python -m app.agents.tool_agent
"""

import os
import re

import httpx

# mock_bank kahan chal raha (env se override ho sakta).
BASE_URL = os.getenv("MOCK_BANK_URL", "http://127.0.0.1:8001")
_TIMEOUT = 10.0


# --- ID extraction (regex — deterministic + free, LLM se sasta) ---
def _extract_account(text: str) -> str | None:
    """16-digit account number dhoondo."""
    m = re.search(r"\b\d{16}\b", text)
    return m.group(0) if m else None


def _extract_loan_id(text: str) -> str | None:
    """LN se shuru hone wala loan id dhoondo (case-insensitive)."""
    m = re.search(r"\bLN\d+\b", text, re.IGNORECASE)
    return m.group(0).upper() if m else None


def _get(path: str) -> tuple[bool, object]:
    """GET helper → (ok, data|error_msg). Connection/404 gracefully handle."""
    try:
        r = httpx.get(f"{BASE_URL}{path}", timeout=_TIMEOUT)
    except httpx.RequestError:
        return False, "Bank service abhi available nahi hai (mock_bank chal raha hai kya?)."
    if r.status_code == 404:
        return False, r.json().get("detail", "Not found")
    r.raise_for_status()
    return True, r.json()


# --- Handlers (ek intent = ek tool) ---
def handle_balance(query: str) -> str:
    acc = _extract_account(query)
    if not acc:
        return "Balance dekhne ke liye apna 16-digit account number bataiye."
    ok, data = _get(f"/accounts/{acc}/balance")
    if not ok:
        return f"Balance nahi mil paya: {data}"
    return (f"{data['name']} ji, account {acc} me balance "
            f"Rs. {data['balance']:,.2f} {data['currency']} hai.")


def handle_loan_status(query: str) -> str:
    lid = _extract_loan_id(query)
    if not lid:
        return "Loan status ke liye apna loan ID bataiye (jaise LN1001)."
    ok, data = _get(f"/loans/{lid}/status")
    if not ok:
        return f"Loan info nahi mili: {data}"
    due = data.get("next_due") or "—"
    return (f"Loan {lid} ({data['type']}): status = {data['status']}, "
            f"EMI Rs. {data['emi']:,}, agli due date {due}.")


def handle_complaint(query: str) -> str:
    acc = _extract_account(query)
    if not acc:
        return "Complaint darj karne ke liye apna 16-digit account number bataiye."
    # MVP: category = 'general', description = poora query. (Aage LLM se structured
    # extraction kar sakte — abhi keep simple.)
    payload = {"account_number": acc, "category": "general", "description": query}
    try:
        r = httpx.post(f"{BASE_URL}/complaints", json=payload, timeout=_TIMEOUT)
    except httpx.RequestError:
        return "Bank service abhi available nahi hai (mock_bank chal raha hai kya?)."
    if r.status_code == 404:
        return "Complaint darj nahi hui: ye account nahi mila."
    r.raise_for_status()
    d = r.json()
    return f"{d['message']} Aapki complaint ID: {d['complaint_id']}."


_HANDLERS = {
    "balance": handle_balance,
    "loan_status": handle_loan_status,
    "complaint": handle_complaint,
}


def handle_tool(intent: str, query: str) -> str:
    """Intent → sahi tool chalao. Unknown intent = guard."""
    handler = _HANDLERS.get(intent)
    if handler is None:
        return f"'{intent}' ke liye koi tool nahi hai."
    return handler(query)


if __name__ == "__main__":
    tests = [
        ("balance", "mera balance batao account 1111000011110000"),
        ("loan_status", "loan LN1001 ka status kya hai"),
        ("complaint", "account 1111000011110000 se ATM me paisa cut gaya par nikla nahi"),
        ("balance", "mera balance kitna hai"),      # no account → poochega
        ("loan_status", "LN9999 ka status"),         # not found → friendly
    ]
    for intent, q in tests:
        print(f"\n[{intent}] {q}")
        print("  ->", handle_tool(intent, q))
