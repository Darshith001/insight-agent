"""Smoke tests that don't require external services."""
from services.ingestion.chunking import split_by_tokens, chunk_sections


def test_split_by_tokens_basic():
    text = "hello world. " * 200
    chunks = split_by_tokens(text, max_tokens=50, overlap=10)
    assert len(chunks) > 1
    assert all(len(c) > 0 for c in chunks)


def test_chunk_sections_passthrough_short():
    secs = [{"title": "intro", "page": 0, "modality": "text", "text": "tiny doc"}]
    out = chunk_sections(secs, max_tokens=500, overlap=80)
    assert len(out) == 1
    assert out[0].text == "tiny doc"
    assert out[0].section == "intro"


def test_chunk_sections_splits_long():
    secs = [{"title": "long", "page": 1, "modality": "text", "text": "alpha " * 1000}]
    out = chunk_sections(secs, max_tokens=200, overlap=20)
    assert len(out) > 1
    assert all(c.section == "long" and c.page == 1 for c in out)
