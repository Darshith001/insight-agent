"""Use GPT-4o as a teacher to label questions as fast (0) or smart (1).

python scripts/gen_router_data.py --in data/questions.txt --out data/router.jsonl
"""
from __future__ import annotations
import argparse, json
from services.common.llm import complete

SYS = """Classify whether a question requires a small fast model (label 0)
or a powerful reasoning model (label 1). Return only "0" or "1"."""


def label(q: str) -> int:
    out = complete(SYS, [{"role": "user", "content": q}], tier="smart",
                   max_tokens=4, temperature=0.0).strip()
    return 1 if out.startswith("1") else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.src, encoding="utf-8") as f, open(args.out, "w", encoding="utf-8") as g:
        for line in f:
            q = line.strip()
            if not q:
                continue
            g.write(json.dumps({"question": q, "label": label(q)}) + "\n")


if __name__ == "__main__":
    main()
