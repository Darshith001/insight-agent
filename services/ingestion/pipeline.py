"""End-to-end ingestion: parse -> chunk -> embed -> upsert into Qdrant.

Usage:
    python -m services.ingestion.pipeline path/to/doc.pdf [doc_id]
"""
from __future__ import annotations
import sys
import uuid
from pathlib import Path
from qdrant_client import models

from services.common.config import get_settings
from services.common.qdrant import get_client, ensure_collection, to_sparse_vector
from services.common.embeddings import embed
from .parser import parse

BATCH_SIZE = 32   # upsert in small batches to avoid timeouts on large docs


def _batched(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def ingest(path: str, doc_id: str | None = None) -> int:
    s = get_settings()
    ensure_collection()
    chunks = parse(path)
    if not chunks:
        print("  [warn] no chunks extracted — check the file has readable text.")
        return 0

    doc_id = doc_id or Path(path).stem
    print(f"  Embedding {len(chunks)} chunks...")
    vecs = embed([c.text for c in chunks])

    points = []
    for i, ch in enumerate(chunks):
        points.append(
            models.PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{doc_id}-{i}")),
                vector={
                    "dense": vecs["dense"][i],
                    "sparse": to_sparse_vector(vecs["sparse"][i]),
                },
                payload={
                    "doc_id": doc_id,
                    "chunk_idx": i,
                    "page": ch.page,
                    "section": ch.section,
                    "modality": ch.modality,
                    "text": ch.text,
                    "source_uri": str(path),
                },
            )
        )

    qc = get_client()
    total = 0
    for batch in _batched(points, BATCH_SIZE):
        qc.upsert(collection_name=s.qdrant_collection, points=batch, wait=True)
        total += len(batch)
        print(f"  Upserted {total}/{len(points)} chunks", end="\r")
    print()
    return total


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python -m services.ingestion.pipeline <path> [doc_id]")
        sys.exit(1)
    p = sys.argv[1]
    did = sys.argv[2] if len(sys.argv) > 2 else None
    n = ingest(p, did)
    print(f"Ingested {n} chunks from {p}")
