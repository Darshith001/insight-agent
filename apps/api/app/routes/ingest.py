"""/ingest endpoint: upload a doc, push it through the ingestion pipeline."""
from __future__ import annotations
import shutil
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, Depends
from services.ingestion.pipeline import ingest as ingest_doc
from ..auth import current_user

router = APIRouter()


@router.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    doc_id: str | None = Form(None),
    user: str = Depends(current_user),
):
    suffix = Path(file.filename or "doc").suffix or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    n = ingest_doc(tmp_path, doc_id or Path(file.filename or "doc").stem)
    return {"ok": True, "chunks": n, "doc_id": doc_id, "user": user}
