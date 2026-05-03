"""/ingest, /documents endpoints for PDF upload and document management."""
from __future__ import annotations
import asyncio
import shutil
import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from services.ingestion.pipeline import ingest as ingest_doc
from services.common.qdrant import list_documents, delete_document
from ..auth import current_user

router = APIRouter()

ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt", ".md", ".html"}
MAX_UPLOAD_MB = 50


@router.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    doc_id: str | None = Form(None),
    user: str = Depends(current_user),
):
    suffix = Path(file.filename or "doc").suffix.lower() or ".pdf"
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(400, f"Unsupported file type: {suffix}. Allowed: {', '.join(ALLOWED_SUFFIXES)}")

    content = await file.read()
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File too large (max {MAX_UPLOAD_MB} MB)")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    resolved_doc_id = doc_id or Path(file.filename or "doc").stem
    try:
        n = await asyncio.to_thread(ingest_doc, tmp_path, resolved_doc_id)
    except Exception as e:
        raise HTTPException(500, f"Ingestion failed: {e}") from e
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return {"ok": True, "chunks": n, "doc_id": resolved_doc_id, "filename": file.filename}


@router.get("/documents")
async def get_documents(user: str = Depends(current_user)):
    try:
        docs = await asyncio.to_thread(list_documents)
    except Exception as e:
        raise HTTPException(500, f"Could not list documents: {e}") from e
    return {"documents": docs}


@router.delete("/documents/{doc_id}")
async def remove_document(doc_id: str, user: str = Depends(current_user)):
    try:
        await asyncio.to_thread(delete_document, doc_id)
    except Exception as e:
        raise HTTPException(500, f"Could not delete document: {e}") from e
    return {"ok": True, "doc_id": doc_id}
