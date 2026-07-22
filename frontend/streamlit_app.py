"""
Streamlit Chat UI — PNB Workflow Agent
======================================
Ek simple chat interface jo backend ke `ask(query)` (LangGraph) ko call karta hai
aur jawab + intent + sources dikhata hai. Isse project DEMOABLE ban jata hai.

Run karne ke liye (project root se):
    .venv/bin/streamlit run frontend/streamlit_app.py

NOTE: balance/loan/complaint (tool) queries ke liye mock_bank ALAG process ON hona chahiye:
    .venv/bin/uvicorn mock_bank.mock_banking_api:app --port 8001
"""

import sys
import uuid
from pathlib import Path

# Streamlit script ko frontend/ se run karta hai → project root sys.path me daalo
# taaki `import app...` kaam kare.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.agents.graph import ask  # noqa: E402 (path setup ke baad import)

st.set_page_config(page_title="PNB Workflow Agent", page_icon="🏦")
st.title("🏦 PNB Workflow Agent")
st.caption("Multi-agent banking assistant — balance, loan status, complaints, FAQs. Hinglish me poochho.")

# --- Sidebar: examples + note ---
with st.sidebar:
    st.header("Try karo")
    st.markdown(
        "- `savings account ka minimum balance kitna hai`\n"
        "- `mera balance batao account 1111000011110000`\n"
        "- `loan LN1001 ka status`\n"
        "- `account 1111000011110000 se ATM me paisa cut gaya`"
    )
    st.info("Test accounts: `1111000011110000`, `2222000022220000` · Loans: `LN1001`, `LN1002`")
    st.warning("Tool queries (balance/loan/complaint) ke liye mock_bank port 8001 par ON hona chahiye.")

# --- Chat history session_state me rakho (Streamlit har interaction pe script rerun karta) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Har browser-session ka apna thread_id → us session ki apni memory (slot-filling
# state alag rahe, doosre users se mix na ho). session_state rerun ke paar bacha rehta.
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Purane messages render karo
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("meta"):
            st.caption(m["meta"])

# --- Naya input ---
if query := st.chat_input("Apna sawaal likhein..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Soch raha hoon..."):
            try:
                result = ask(query, thread_id=st.session_state.thread_id)
                answer = result.get("answer") or "(koi jawab nahi mila)"
                meta_bits = [f"intent: `{result.get('intent', '?')}`"]
                if result.get("sources"):
                    meta_bits.append("sources: " + ", ".join(result["sources"]))
                meta = " · ".join(meta_bits)
            except Exception as e:
                answer = f"Kuch gadbad ho gayi: {e}"
                meta = ""
        st.markdown(answer)
        if meta:
            st.caption(meta)

    st.session_state.messages.append({"role": "assistant", "content": answer, "meta": meta})
