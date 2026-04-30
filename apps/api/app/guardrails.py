"""Input/output guardrails: PII redaction (Presidio) + prompt-injection heuristics."""
from __future__ import annotations
import re
from functools import lru_cache

_INJECTION_PATTERNS = [
    re.compile(r"ignore (all|previous|the above) (instructions|prompts)", re.I),
    re.compile(r"system prompt", re.I),
    re.compile(r"you are now (a|an) ", re.I),
    re.compile(r"reveal your (system )?prompt", re.I),
]


@lru_cache
def _analyzer():
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        return AnalyzerEngine(), AnonymizerEngine()
    except Exception:
        return None


def is_injection(text: str) -> bool:
    return any(p.search(text) for p in _INJECTION_PATTERNS)


def redact_pii(text: str) -> str:
    pair = _analyzer()
    if pair is None:
        return text
    analyzer, anonymizer = pair
    results = analyzer.analyze(text=text, language="en")
    if not results:
        return text
    return anonymizer.anonymize(text=text, analyzer_results=results).text
