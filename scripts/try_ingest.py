from pathlib import Path

from docops_ai.ingestion import IngestionError, ingest_pdf

for pdf in sorted(Path("data/raw").glob("*.pdf")):
    try:
        pages = ingest_pdf(pdf)
    except IngestionError as exc:
        print(f"{pdf.name}: ERROR {exc}")
        continue
    empty = sum(p.is_empty for p in pages)
    chars = sum(len(p.text) for p in pages)
    print(f"{pdf.name}: {len(pages)} pages, {empty} empty, {chars} chars")
    first = next((p for p in pages if not p.is_empty), None)
    if first:
        print(f"  p.{first.page_number}: {first.text[:150]!r}")
