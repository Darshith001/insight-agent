"""Structure-aware chunking. Respects headings, falls back to token windows."""
from __future__ import annotations
from dataclasses import dataclass
import tiktoken

_enc = tiktoken.get_encoding("cl100k_base")


@dataclass
class Chunk:
    text: str
    page: int
    section: str
    modality: str  # text | table | figure


def _tok_len(s: str) -> int:
    return len(_enc.encode(s))


def split_by_tokens(text: str, max_tokens: int, overlap: int) -> list[str]:
    ids = _enc.encode(text)
    out, start = [], 0
    step = max(1, max_tokens - overlap)
    while start < len(ids):
        end = min(start + max_tokens, len(ids))
        out.append(_enc.decode(ids[start:end]))
        if end == len(ids):
            break
        start += step
    return out


def chunk_sections(sections: list[dict], max_tokens: int = 500, overlap: int = 80) -> list[Chunk]:
    """sections: [{title, page, modality, text}, ...]."""
    chunks: list[Chunk] = []
    for sec in sections:
        if _tok_len(sec["text"]) <= max_tokens:
            chunks.append(Chunk(sec["text"], sec["page"], sec["title"], sec["modality"]))
        else:
            for piece in split_by_tokens(sec["text"], max_tokens, overlap):
                chunks.append(Chunk(piece, sec["page"], sec["title"], sec["modality"]))
    return chunks
