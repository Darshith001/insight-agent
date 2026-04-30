"""Multi-modal document parser using Docling. Falls back to plain text for .txt/.md."""
from __future__ import annotations
import warnings
from pathlib import Path
from .chunking import chunk_sections, Chunk


def _page_no(item) -> int:
    """Extract page number from a Docling item's prov field (handles both object and dict forms)."""
    prov = getattr(item, "prov", None)
    if not prov:
        return 0
    first = prov[0] if isinstance(prov, (list, tuple)) else prov
    if hasattr(first, "page_no"):
        return int(first.page_no)
    if isinstance(first, dict):
        return int(first.get("page_no", 0))
    return 0


def _table_to_markdown(item, doc) -> str:
    """Export table to markdown, passing doc to avoid deprecation warning."""
    if not hasattr(item, "export_to_markdown"):
        return str(item)
    try:
        # newer Docling requires the parent doc to be passed
        import inspect
        sig = inspect.signature(item.export_to_markdown)
        if "doc" in sig.parameters:
            return item.export_to_markdown(doc=doc)
        return item.export_to_markdown()
    except Exception:
        return str(item)


def _parse_with_docling(path: Path) -> list[dict]:
    from docling.document_converter import DocumentConverter

    abs_path = path.resolve().as_posix()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = DocumentConverter().convert(abs_path)

    doc = result.document
    sections: list[dict] = []
    current_title = "intro"
    page = 0

    for item, _level in doc.iterate_items():
        try:
            kind = item.label.lower() if hasattr(item, "label") else "text"
            page = _page_no(item)

            if "header" in kind or "title" in kind:
                current_title = (getattr(item, "text", "") or "").strip() or current_title
                continue
            if "table" in kind:
                md = _table_to_markdown(item, doc)
                sections.append({"title": current_title, "page": page, "modality": "table", "text": md})
            elif "figure" in kind or "picture" in kind:
                caption = (getattr(item, "caption_text", "") or "").strip()
                if caption:
                    sections.append({"title": current_title, "page": page, "modality": "figure", "text": caption})
            else:
                text = (getattr(item, "text", "") or "").strip()
                if text:
                    sections.append({"title": current_title, "page": page, "modality": "text", "text": text})
        except Exception as e:
            print(f"  [warn] skipping item on page {page}: {e}")
            continue

    return sections


def _parse_plain(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [{"title": path.stem, "page": 0, "modality": "text", "text": text}]


def parse(path: str | Path) -> list[Chunk]:
    p = Path(path).resolve()

    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {p}")
    if p.is_dir():
        raise IsADirectoryError(
            f"'{p}' is a folder, not a file.\n"
            f"Please pass a file path, e.g.:\n"
            f"  python -m services.ingestion.pipeline \"E:\\folder\\report.pdf\""
        )

    if p.suffix.lower() in {".txt", ".md"}:
        sections = _parse_plain(p)
    else:
        sections = _parse_with_docling(p)

    return chunk_sections(sections)
