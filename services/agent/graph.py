"""LangGraph state machine: plan -> retrieve -> synthesize -> critique -> (retry|end)."""
from __future__ import annotations
import json
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, END

from services.common.llm import complete
from services.common.config import get_settings
from .retrieval import search_multi, Hit
from .prompts import PLANNER_SYSTEM, SYNTH_SYSTEM, CRITIC_SYSTEM


class AgentState(TypedDict, total=False):
    question: str
    tier: Literal["fast", "smart"]
    sub_queries: List[str]
    contexts: List[dict]   # serialized Hit
    draft: str
    critique: dict
    retries: int


def _safe_json(text: str, fallback):
    try:
        start = text.find("[") if text.lstrip().startswith("[") else text.find("{")
        end = text.rfind("]") if text.lstrip().startswith("[") else text.rfind("}")
        return json.loads(text[start : end + 1])
    except Exception:
        return fallback


# ---------- nodes ----------
def plan_node(state: AgentState) -> AgentState:
    raw = complete(
        PLANNER_SYSTEM,
        [{"role": "user", "content": state["question"]}],
        tier="fast",
        max_tokens=300,
        temperature=0.1,
    )
    subs = _safe_json(raw, [state["question"]])
    if not isinstance(subs, list) or not subs:
        subs = [state["question"]]
    return {"sub_queries": [str(x) for x in subs[:4]]}


def retrieve_node(state: AgentState) -> AgentState:
    queries = state.get("sub_queries") or [state["question"]]
    refined = (state.get("critique") or {}).get("refined_query")
    if refined:
        queries = [refined] + queries
    hits: list[Hit] = search_multi(queries)
    return {"contexts": [h.__dict__ for h in hits]}


def synth_node(state: AgentState) -> AgentState:
    ctx = state.get("contexts") or []
    block = "\n\n".join(
        f"[{i+1}] (p.{c['page']} - {c['section']})\n{c['text']}" for i, c in enumerate(ctx)
    ) or "NO CONTEXT FOUND"
    user = f"Question: {state['question']}\n\nContext:\n{block}"
    answer = complete(SYNTH_SYSTEM, [{"role": "user", "content": user}],
                      tier=state.get("tier", "smart"), max_tokens=900, temperature=0.2)
    return {"draft": answer}


def critique_node(state: AgentState) -> AgentState:
    ctx = state.get("contexts") or []
    block = "\n\n".join(f"[{i+1}] {c['text']}" for i, c in enumerate(ctx)) or "(none)"
    user = (
        f"Question: {state['question']}\n\nAnswer:\n{state.get('draft','')}\n\n"
        f"Context:\n{block}"
    )
    raw = complete(CRITIC_SYSTEM, [{"role": "user", "content": user}],
                   tier="smart", max_tokens=400, temperature=0.0)
    parsed = _safe_json(raw, {"score": 1.0, "refined_query": None,
                              "faithful": 1.0, "complete": 1.0, "relevant": 1.0,
                              "reason": "judge parse failed - assume pass"})
    return {"critique": parsed, "retries": (state.get("retries") or 0) + 1}


def should_retry(state: AgentState) -> str:
    s = get_settings()
    score = float((state.get("critique") or {}).get("score", 1.0))
    retries = int(state.get("retries") or 0)
    if score < s.critique_threshold and retries < s.max_retries + 1:
        return "retry"
    return "end"


# ---------- graph ----------
def build_agent():
    g = StateGraph(AgentState)
    g.add_node("plan", plan_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("synthesize", synth_node)
    g.add_node("critique", critique_node)
    g.set_entry_point("plan")
    g.add_edge("plan", "retrieve")
    g.add_edge("retrieve", "synthesize")
    g.add_edge("synthesize", "critique")
    g.add_conditional_edges("critique", should_retry, {"retry": "retrieve", "end": END})
    return g.compile()


agent = build_agent()


def run(question: str, tier: str = "smart") -> dict:
    final = agent.invoke({"question": question, "tier": tier, "retries": 0})
    return {
        "answer": final.get("draft", ""),
        "citations": final.get("contexts", []),
        "critique": final.get("critique", {}),
        "sub_queries": final.get("sub_queries", []),
        "retries": final.get("retries", 0),
    }
