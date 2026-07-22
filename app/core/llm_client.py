"""
LLM Client (OpenRouter)
=======================
Ek jagah se LLM ko call karne ka helper. Baaki poore project (supervisor,
rag_agent, tool_agent) yahin se LLM baat karenge — taaki config ek jagah rahe.

"API call" kya hai (basics):
  Hum ek HTTP request bhejte hain OpenRouter ke server ko: "ye messages hain,
  is model se jawab do". Server LLM chala ke text wapas bhejta hai. Bas.

OpenRouter kyun / kaise:
  OpenRouter ek OpenAI-COMPATIBLE gateway hai. Matlab hum OpenAI ka official
  `openai` SDK use karte hain, bas `base_url` OpenRouter ka de dete hain. Ek hi
  key se model badal sakte hain (anthropic/claude-... ya openai/gpt-... etc).

Secrets .env se aate hain (git-ignored):
  OPENROUTER_API_KEY  -> tumhari key (KABHI code me hardcode mat karna)
  OPENROUTER_BASE_URL -> https://openrouter.ai/api/v1
  LLM_MODEL           -> anthropic/claude-sonnet-5

Test karne ke liye (project root se, .env me key daalne ke baad):
    .venv/bin/python -m app.core.llm_client
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Project root ka .env explicitly load karo (fresh shell me cwd bharosa nahi).
_ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.getenv("LLM_MODEL", "anthropic/claude-sonnet-5")

# Client ek hi baar banao (module load par). Baar-baar banane ki zaroorat nahi.
_client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def chat(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    """LLM ko messages bhejo, text jawab wapas lo.

    Args:
        messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
            - system  = LLM ko instructions/persona (optional, pehla message)
            - user    = insaan ka input
            - assistant = LLM ke pichhle jawab (multi-turn ke liye)
        model: override; default LLM_MODEL (.env se).
        temperature: 0 = predictable/consistent, 1+ = creative/random.
            Humare use (routing, grounded answers) ke liye kam behtar (0.3).
        max_tokens: jawab ki max lambai (tokens). Zaroori kyun: OpenRouter
            upfront credits RESERVE karta hai max_tokens ke hisaab se — bina set
            kiye SDK bada default (65536) maangta hai aur 402 (credits) aata hai.
            Routing/short answers ke liye 1024 kaafi hai.

    Return: sirf jawab ka text (string).
    """
    if not API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY nahi mili. Project root ke .env me apni key daalo:\n"
            "  OPENROUTER_API_KEY=sk-or-...\n"
            "(.env.example dekho; .env git-ignored hai.)"
        )

    response = _client.chat.completions.create(
        model=model or MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    # OpenAI-compatible response: choices[0].message.content me text hota hai.
    return response.choices[0].message.content


if __name__ == "__main__":
    # Quick smoke test — LLM tak request-response chal raha hai?
    print(f"Model: {MODEL}")
    reply = chat([
        {"role": "system", "content": "Tum PNB ke helpful assistant ho. Hinglish me jawab do."},
        {"role": "user", "content": "Ek line me batao: savings account kya hota hai?"},
    ])
    print("LLM:", reply)
