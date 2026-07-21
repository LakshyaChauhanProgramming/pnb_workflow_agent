"""
Mock PNB Banking API
====================
Yeh REAL Punjab National Bank ka backend NAHI hai — yeh usko *simulate* karta hai.
Humara AI agent iske endpoints ko HTTP se call karega (balance, complaint, loan...).

Chalane ke liye (project root se):
    .venv/bin/uvicorn mock_bank.mock_banking_api:app --reload --port 8001

Phir browser mein kholo:  http://127.0.0.1:8001/docs   (auto Swagger UI)
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Mock PNB Banking API",
    version="0.2.0",
    description="Punjab National Bank backend ka mock — testing/learning ke liye.",
)

# ===========================================================================
# FAKE DATABASE (in-memory dicts — asli DB baad mein).
# ===========================================================================
ACCOUNTS = {
    "1111000011110000": {
        "name": "Amit Kumar",
        "account_type": "savings",
        "balance": 25340.75,
        "currency": "INR",
        "branch": "Connaught Place, New Delhi",
        "ifsc": "PUNB0111100",
    },
    "2222000022220000": {
        "name": "Priya Sharma",
        "account_type": "current",
        "balance": 187500.00,
        "currency": "INR",
        "branch": "MG Road, Bengaluru",
        "ifsc": "PUNB0222200",
    },
}

LOANS = {
    "LN1001": {"account_number": "1111000011110000", "type": "home",
               "amount": 3500000, "emi": 28500, "status": "active", "next_due": "2026-08-05"},
    "LN1002": {"account_number": "2222000022220000", "type": "personal",
               "amount": 500000, "emi": 12200, "status": "under_review", "next_due": None},
}

# Complaints yahan store honge. Counter naya ID banane ke liye.
COMPLAINTS: dict[str, dict] = {}
_complaint_counter = 1000


# ===========================================================================
# Pydantic MODELS — POST request ka "body" (data) ka shape define karte hain.
# Kyun: FastAPI in models se automatic VALIDATION karta hai. Galat/missing
# field aaye toh khud 422 error bhej deta hai — humein manually check nahi karna.
# ===========================================================================
class ComplaintIn(BaseModel):
    account_number: str = Field(..., description="Jis account ki complaint hai")
    category: str = Field(..., description="e.g. 'failed_transaction', 'card_block', 'dispute'")
    description: str = Field(..., min_length=5, description="Kya problem hai")


# ===========================================================================
# ENDPOINTS
# ===========================================================================
@app.get("/")
def root():
    return {"service": "Mock PNB Banking API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# --- Account: full details ---
@app.get("/accounts/{account_number}")
def get_account(account_number: str):
    if account_number not in ACCOUNTS:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_number": account_number, **ACCOUNTS[account_number]}


# --- Account: balance only ---
@app.get("/accounts/{account_number}/balance")
def get_balance(account_number: str):
    if account_number not in ACCOUNTS:
        raise HTTPException(status_code=404, detail="Account not found")
    acc = ACCOUNTS[account_number]
    return {
        "account_number": account_number,
        "name": acc["name"],
        "balance": acc["balance"],
        "currency": acc["currency"],
    }


# --- Loan: status check ---
@app.get("/loans/{loan_id}/status")
def get_loan_status(loan_id: str):
    if loan_id not in LOANS:
        raise HTTPException(status_code=404, detail="Loan not found")
    return {"loan_id": loan_id, **LOANS[loan_id]}


# --- Complaint: register (POST) ---
# 'payload: ComplaintIn' => FastAPI request body ko is model mein parse + validate karega.
# status_code=201 => "Created" (naya resource bana), REST convention.
@app.post("/complaints", status_code=201)
def create_complaint(payload: ComplaintIn):
    # Account valid hai kya? Warna complaint banane ka matlab nahi.
    if payload.account_number not in ACCOUNTS:
        raise HTTPException(status_code=404, detail="Account not found")

    global _complaint_counter
    _complaint_counter += 1
    complaint_id = f"CMP{_complaint_counter}"

    COMPLAINTS[complaint_id] = {
        "account_number": payload.account_number,
        "category": payload.category,
        "description": payload.description,
        "status": "registered",
    }
    return {"complaint_id": complaint_id, "status": "registered",
            "message": "Aapki complaint darj ho gayi hai."}


# --- Complaint: status check ---
@app.get("/complaints/{complaint_id}")
def get_complaint(complaint_id: str):
    if complaint_id not in COMPLAINTS:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {"complaint_id": complaint_id, **COMPLAINTS[complaint_id]}
