"""
Graph — sab agents ko wire karo (project ka dil)
================================================
Ye LangGraph hai jo teeno pieces ko ek flow me jodta hai:

    START -> supervisor -> (conditional edge based on intent)
                             |-- "faq"                -> rag_node  -> END
                             |-- balance/complaint/loan -> tool_node -> END

- State: ek shared dict {query, intent, answer, sources} jo har node ke beech
  flow karti. Har node sirf apni badli hui keys return karta; LangGraph merge karta.
- supervisor decide karta retrieval (rag) chahiye ya live-data (tool).

Zaroori: `tool_node` mock_bank ko HTTP se call karta → wo alag process ON hona chahiye:
    .venv/bin/uvicorn mock_bank.mock_banking_api:app --port 8001

Test:
    .venv/bin/python -m app.agents.graph
"""

from typing import TypedDict

from langgraph.graph import START, END, StateGraph

from app.agents.rag_agent import answer_faq
from app.agents.supervisor import classify_intent
from app.agents.tool_agent import handle_tool


# --- Shared state (poore graph me flow karti) ---
class State(TypedDict):
    query: str            # user input
    intent: str           # supervisor bharega
    answer: str           # rag/tool bharega
    sources: list[str]    # rag bharega (tool ke liye khaali)


# --- Nodes (har ek pehle bana hua function call karta) ---
def supervisor_node(state: State) -> dict:
    return {"intent": classify_intent(state["query"])}


def rag_node(state: State) -> dict:
    res = answer_faq(state["query"])
    return {"answer": res["answer"], "sources": res["sources"]}


def tool_node(state: State) -> dict:
    return {"answer": handle_tool(state["intent"], state["query"]), "sources": []}


# --- Routing function (conditional edge): intent dekh ke agla node ---
def route_after_supervisor(state: State) -> str:
    # faq = knowledge question -> RAG; baaki = live data/action -> tools.
    return "rag" if state["intent"] == "faq" else "tool"


def build_graph():
    b = StateGraph(State)
    b.add_node("supervisor", supervisor_node)
    b.add_node("rag", rag_node)
    b.add_node("tool", tool_node)

    b.add_edge(START, "supervisor")
    b.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {"rag": "rag", "tool": "tool"},   # mapping: routing-fn ka output -> node
    )
    b.add_edge("rag", END)
    b.add_edge("tool", END)
    return b.compile()


# Module load par ek hi baar compile.
graph = build_graph()


def ask(query: str) -> dict:
    """Ek query poore graph se chalao → final state ({query, intent, answer, sources})."""
    return graph.invoke({"query": query})


if __name__ == "__main__":
    queries = [
        "savings account ka minimum balance kitna hai",                  # faq  -> rag
        "mera balance batao account 1111000011110000",                    # balance -> tool
        "loan LN1001 ka status kya hai",                                  # loan_status -> tool
        "account 1111000011110000 se ATM me paisa kat gaya par nikla nahi",  # complaint -> tool
    ]
    for q in queries:
        print(f"\nUSER: {q}")
        final = ask(q)
        print(f"  [intent = {final['intent']}]")
        print(f"  BOT: {final['answer']}")
        if final.get("sources"):
            print(f"  (sources: {final['sources']})")
