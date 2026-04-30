"""Run RAGAS over the golden set and fail CI if metrics drop below thresholds.

Usage:
    python evals/run_ragas.py --golden evals/golden_set.jsonl
"""
from __future__ import annotations
import argparse, json, sys
from datasets import Dataset

from services.agent.graph import run as run_agent

THRESHOLDS = {
    "faithfulness": 0.85,
    "answer_relevancy": 0.80,
    "context_precision": 0.70,
}


def build_dataset(golden_path: str) -> Dataset:
    rows = []
    for line in open(golden_path, encoding="utf-8"):
        if not line.strip():
            continue
        g = json.loads(line)
        out = run_agent(g["question"], tier="smart")
        rows.append({
            "question": g["question"],
            "answer": out["answer"],
            "contexts": [c["text"] for c in out["citations"]] or g.get("contexts", []),
            "ground_truth": g["ground_truth"],
        })
    return Dataset.from_list(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", required=True)
    args = ap.parse_args()

    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision

    ds = build_dataset(args.golden)
    result = evaluate(ds, metrics=[faithfulness, answer_relevancy, context_precision])
    print(result)

    failed = []
    for k, threshold in THRESHOLDS.items():
        score = float(result[k])
        if score < threshold:
            failed.append(f"{k}={score:.3f} < {threshold}")
    if failed:
        print("EVAL GATE FAILED:", "; ".join(failed))
        sys.exit(1)
    print("EVAL GATE PASSED")


if __name__ == "__main__":
    main()
