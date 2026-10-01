import hashlib
from pathlib import Path

import pymupdf

from .cleaning import clean_text
from .layout import strip_page_furniture
from .models import PageContent


class IngestionError(Exception):
    """Raised when a document cannot be turned into pages."""


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()[:16]


def ingest_pdf(path: str | Path) -> list[PageContent]:
    """Extract one PageContent per page from a PDF file."""
    path = Path(path)
    if not path.is_file():
        raise IngestionError(f"File not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise IngestionError(f"Not a PDF file: {path.name}")

    try:
        doc = pymupdf.open(str(path))
    except Exception as exc:
        raise IngestionError(f"Cannot open {path.name}: {exc}") from exc

    with doc:
        if doc.needs_pass:
            raise IngestionError(f"{path.name} is password-protected")
        metadata = {k: v for k, v in (doc.metadata or {}).items() if v}
        doc_id = file_hash(path)
        pages = [
            PageContent(
                doc_id=doc_id,
                source=path.name,
                page_number=index + 1,
                text=clean_text(page.get_text("text")),
                metadata=metadata,
            )
            for index, page in enumerate(doc)
        ]
    return strip_page_furniture(pages)
