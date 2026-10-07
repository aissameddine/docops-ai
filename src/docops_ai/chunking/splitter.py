from docops_ai.ingestion.models import PageContent

from .models import Chunk, ChunkingConfig

# Preferred places to cut, best first. A cut after a paragraph break beats a cut
# after a sentence, which beats a cut between two words.
SEPARATORS = ("\n\n", "\n", ". ", " ")
MIN_FILL = 0.5  # a cut must keep at least this share of the window


def _find_end(text: str, start: int, config: ChunkingConfig, limit: int) -> int:
    """End (exclusive) of the chunk that begins at `start`."""
    hard_end = min(start + config.chunk_size, limit)
    if hard_end == limit:
        return limit
    window = text[start:hard_end]
    min_len = max(1, int(config.chunk_size * MIN_FILL))
    for sep in SEPARATORS:
        idx = window.rfind(sep)
        if idx != -1 and idx + len(sep) >= min_len:
            return start + idx + len(sep)
    return hard_end  # no good cut: a very long word, a URL, ...


def _next_start(text: str, start: int, end: int, overlap: int) -> int:
    """Where the next chunk begins: `overlap` characters back, on a word start."""
    if overlap == 0:
        return end
    candidate = end - overlap
    if candidate <= start:
        return end  # chunk too short to overlap: guarantee progress
    for i in range(candidate, end):
        if text[i - 1].isspace() and not text[i].isspace():
            return i
    return candidate


def split_text(text: str, config: ChunkingConfig) -> list[tuple[int, int]]:
    """Return (start, end) offsets of the stripped chunks of `text`."""
    limit = len(text.rstrip())
    spans = []
    start = 0
    while start < limit:
        end = _find_end(text, start, config, limit)
        raw = text[start:end]
        lead = len(raw) - len(raw.lstrip())
        trail = len(raw) - len(raw.rstrip())
        if end - trail > start + lead:
            spans.append((start + lead, end - trail))
        if end >= limit:
            break
        start = _next_start(text, start, end, config.overlap)
    return spans


def chunk_pages(pages: list[PageContent], config: ChunkingConfig | None = None) -> list[Chunk]:
    """Cut every page into chunks. A chunk never spans two pages."""
    config = config or ChunkingConfig()
    chunks = []
    for page in pages:
        for index, (s, e) in enumerate(split_text(page.text, config)):
            chunks.append(
                Chunk(
                    chunk_id=f"{page.doc_id}-p{page.page_number}-c{index}",
                    doc_id=page.doc_id,
                    source=page.source,
                    page_number=page.page_number,
                    chunk_index=index,
                    text=page.text[s:e],
                    char_start=s,
                    char_end=e,
                    metadata=dict(page.metadata),
                )
            )
    return chunks
