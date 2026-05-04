# -*- coding: utf-8 -*-
"""InsightAgent -- Accuracy & Cost Benchmark.

Usage:
    cd "E:/NEW PROJ/insight-agent"
    python evals/benchmark.py
"""
from __future__ import annotations
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

# OpenAI pricing per 1M tokens (May 2026)
PRICING = {
    "gpt-4o":      {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini": {"input": 0.15,  "output": 0.60},
}

# Test questions: easy -> medium -> hard
QUESTIONS = [
    {"q": "What is InsightAgent?",                          "tier_expect": "fast"},
    {"q": "What port does the API run on?",                 "tier_expect": "fast"},
    {"q": "What embedding model does the system use?",      "tier_expect": "fast"},
    {"q": "What vector database is used?",                  "tier_expect": "fast"},
    {"q": "How does hybrid retrieval work in this system?", "tier_expect": "smart"},
    {"q": "What is the self-correction mechanism?",         "tier_expect": "smart"},
    {"q": "How are documents ingested and indexed?",        "tier_expect": "smart"},
    {"q": "Compare the fast and smart tiers -- when does each activate and what are the cost trade-offs?",
                                                            "tier_expect": "smart"},
    {"q": "Walk me through what happens end-to-end when a user uploads a PDF and asks a question.",
                                                            "tier_expect": "smart"},
    {"q": "What security measures protect the API and what happens if Redis is unavailable?",
                                                            "tier_expect": "smart"},
]

# Patch LLM to capture token usage per call
import services.common.llm as llm_module
from openai import OpenAI

_token_log: list[dict] = []

def _patched_complete(system, messages, tier="smart", max_tokens=1024,
                      temperature=0.2, cache_system=True) -> str:
    from services.common.config import get_settings
    s = get_settings()
    model = s.opus_model if tier == "smart" else s.haiku_model
    client = OpenAI(api_key=s.openai_api_key or os.getenv("OPENAI_API_KEY", ""))
    full_messages = [{"role": "system", "content": system}] + messages
    resp = client.chat.completions.create(
        model=model, messages=full_messages,
        max_tokens=max_tokens, temperature=temperature,
    )
    usage = resp.usage
    _token_log.append({
        "model": model,
        "input_tok": usage.prompt_tokens,
        "output_tok": usage.completion_tokens,
        "tier": tier,
    })
    return resp.choices[0].message.content or ""

llm_module.complete = _patched_complete

from services.agent.graph import run as run_agent

results = []
print("\n" + "="*70)
print("  InsightAgent -- Accuracy & Cost Benchmark")
print("="*70)

for i, item in enumerate(QUESTIONS, 1):
    q = item["q"]
    print(f"\n[{i}/{len(QUESTIONS)}] {q[:65]}...")
    _token_log.clear()
    t0 = time.perf_counter()
    try:
        tier = "smart" if len(q.split()) > 12 else "fast"
        out = run_agent(q, tier=tier)
        latency = time.perf_counter() - t0

        critique = out.get("critique") or {}
        score    = float(critique.get("score",    0))
        faithful = float(critique.get("faithful", 0))
        complete = float(critique.get("complete", 0))
        relevant = float(critique.get("relevant", 0))
        retries  = int(out.get("retries", 0))
        cites    = len(out.get("citations", []))
        tier_used = "smart" if any(t["model"] == "gpt-4o" for t in _token_log) else "fast"

        total_cost = total_in = total_out = 0
        for t in _token_log:
            p = PRICING.get(t["model"], PRICING["gpt-4o"])
            total_cost += (t["input_tok"] / 1e6) * p["input"] + \
                          (t["output_tok"] / 1e6) * p["output"]
            total_in  += t["input_tok"]
            total_out += t["output_tok"]

        results.append({
            "question":    q,
            "tier_used":   tier_used,
            "tier_expect": item["tier_expect"],
            "score":       round(score,    3),
            "faithful":    round(faithful, 3),
            "complete":    round(complete, 3),
            "relevant":    round(relevant, 3),
            "retries":     retries,
            "citations":   cites,
            "latency_s":   round(latency, 2),
            "input_tok":   total_in,
            "output_tok":  total_out,
            "cost_usd":    round(total_cost, 6),
            "answer_preview": (out.get("answer") or "")[:120],
        })

        grade = "PASS" if score >= 0.75 else "FAIL"
        print(f"  [{grade}] score={score:.2f}  faithful={faithful:.2f}  "
              f"complete={complete:.2f}  relevant={relevant:.2f}")
        print(f"         tier={tier_used}  retries={retries}  cites={cites}  "
              f"latency={latency:.1f}s  cost=${total_cost:.4f}  "
              f"tokens={total_in}/{total_out}")

    except Exception as e:
        import traceback; traceback.print_exc()
        results.append({"question": q, "error": str(e), "cost_usd": 0})
        print(f"  [ERR] {e}")

# Summary
ok = [r for r in results if "score" in r]
if not ok:
    print("No results -- all queries failed.")
    sys.exit(1)

total_cost  = sum(r.get("cost_usd",   0) for r in results)
total_in    = sum(r.get("input_tok",  0) for r in ok)
total_out   = sum(r.get("output_tok", 0) for r in ok)
avg_score   = sum(r["score"]    for r in ok) / len(ok)
avg_faith   = sum(r["faithful"] for r in ok) / len(ok)
avg_comp    = sum(r["complete"] for r in ok) / len(ok)
avg_rel     = sum(r["relevant"] for r in ok) / len(ok)
avg_lat     = sum(r["latency_s"] for r in ok) / len(ok)
avg_cost    = total_cost / len(ok)
pass_rate   = sum(1 for r in ok if r["score"] >= 0.75) / len(ok) * 100
retry_rate  = sum(r["retries"] for r in ok) / len(ok)
fast_n      = sum(1 for r in ok if r["tier_used"] == "fast")
smart_n     = len(ok) - fast_n

# Cost if everything ran on gpt-4o
all_smart_cost = (total_in  / 1e6) * PRICING["gpt-4o"]["input"] + \
                 (total_out / 1e6) * PRICING["gpt-4o"]["output"]
savings = (1 - total_cost / all_smart_cost) * 100 if all_smart_cost > 0 else 0

sep = "="*70
print(f"\n{sep}")
print("  RESULTS SUMMARY")
print(sep)
print(f"  Queries run        : {len(ok)}/{len(QUESTIONS)}")
print(f"  Pass rate (>=0.75) : {pass_rate:.0f}%")
print()
print("  -- Accuracy ------------------------------------------")
print(f"  Avg critic score   : {avg_score:.3f}  {'[GOOD]' if avg_score>=0.75 else '[NEEDS WORK]'}")
print(f"  Avg faithfulness   : {avg_faith:.3f}  {'[GOOD]' if avg_faith>=0.75 else '[LOW]'}")
print(f"  Avg completeness   : {avg_comp:.3f}  {'[GOOD]' if avg_comp>=0.75 else '[LOW]'}")
print(f"  Avg relevance      : {avg_rel:.3f}  {'[GOOD]' if avg_rel>=0.75 else '[LOW]'}")
print(f"  Avg retry rate     : {retry_rate:.2f} per query")
print()
print("  -- Performance ---------------------------------------")
print(f"  Avg latency        : {avg_lat:.1f}s per query")
print(f"  Fast tier (mini)   : {fast_n} queries ({fast_n/len(ok)*100:.0f}%)")
print(f"  Smart tier (4o)    : {smart_n} queries ({smart_n/len(ok)*100:.0f}%)")
print()
print("  -- Cost ----------------------------------------------")
print(f"  Total tokens       : {total_in:,} input + {total_out:,} output")
print(f"  Total for {len(ok)} queries : ${total_cost:.4f}")
print(f"  Avg cost/query     : ${avg_cost:.4f}")
print(f"  Est. 1,000 queries : ${avg_cost * 1000:.2f}")
print(f"  Est. 10,000 queries: ${avg_cost * 10000:.2f}")
print()
print("  -- Cost Efficiency -----------------------------------")
print(f"  All-GPT-4o cost    : ${all_smart_cost:.4f}")
print(f"  With routing       : ${total_cost:.4f}")
print(f"  Routing saves      : {savings:.0f}% cost reduction")
print(sep)
print()
print("  Per-Query Breakdown:")
print(f"  {'#':<3} {'Result':<6} {'Score':>6} {'Tier':<6} {'Lat':>6} {'Cost':>8} {'Ret':>4}  Question")
print("  " + "-"*78)
for i, r in enumerate(results, 1):
    if "score" in r:
        g = "PASS" if r["score"] >= 0.75 else "FAIL"
        q_s = r["question"][:44] + ("..." if len(r["question"]) > 44 else "")
        print(f"  {i:<3} {g:<6} {r['score']:>5.2f}  {r['tier_used']:<6} "
              f"{r['latency_s']:>5.1f}s  ${r['cost_usd']:.4f}  {r['retries']:>3}  {q_s}")
    else:
        print(f"  {i:<3} ERROR  -      -      -      -         -  {r['question'][:44]}")

# Save JSON
out_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump({
        "summary": {
            "queries_run":       len(ok),
            "pass_rate_pct":     round(pass_rate, 1),
            "avg_score":         round(avg_score, 3),
            "avg_faithfulness":  round(avg_faith, 3),
            "avg_completeness":  round(avg_comp,  3),
            "avg_relevance":     round(avg_rel,   3),
            "avg_latency_s":     round(avg_lat,   2),
            "avg_cost_usd":      round(avg_cost,  6),
            "total_cost_usd":    round(total_cost, 4),
            "routing_saves_pct": round(savings,   1),
            "fast_queries_pct":  round(fast_n / len(ok) * 100, 1),
            "retry_rate":        round(retry_rate, 2),
        },
        "results": results,
    }, f, indent=2)
print(f"\n  Full results saved: {out_path}")
print(sep)
