from collections import Counter

from .cleaning import clean_text
from .models import PageContent

EDGE_LINES = 3  # how many lines at the top/bottom of a page count as "edge"
MIN_PAGES = 3  # below this we cannot tell furniture from content
MIN_SHARE = 0.5  # fraction of pages an edge line must appear on
MIN_LINE_LEN = 5  # ignore very short lines such as "}" in code


def _threshold(n_pages: int) -> float:
    return max(MIN_PAGES, n_pages * MIN_SHARE)


def _repeated_edge_lines(pages: list[PageContent]) -> list[str]:
    """Edge lines shared by enough pages, in order of first appearance."""
    counts: Counter[str] = Counter()
    for page in pages:
        lines = [line.strip() for line in page.text.split("\n")]
        edge = dict.fromkeys(lines[:EDGE_LINES] + lines[-EDGE_LINES:])
        counts.update(line for line in edge if len(line) >= MIN_LINE_LEN and not line.isdigit())
    limit = _threshold(len(pages))
    return [line for line, count in counts.items() if count >= limit]


def _page_number_offset(pages: list[PageContent]) -> int | None:
    """If footers are bare numbers following page_number - k, return k."""
    offsets: Counter[int] = Counter()
    for page in pages:
        last = page.text.rsplit("\n", 1)[-1].strip()
        if last.isdigit():
            offsets[page.page_number - int(last)] += 1
    if not offsets:
        return None
    offset, count = offsets.most_common(1)[0]
    return offset if count >= _threshold(len(pages)) else None


def strip_page_furniture(pages: list[PageContent]) -> list[PageContent]:
    """Remove repeated headers/footers and bare page numbers from every page.

    The removed header/footer lines are not lost: they are stored in
    metadata["stripped_edge_lines"], joined with " | ".
    """
    if len(pages) < MIN_PAGES:
        return pages

    repeated = _repeated_edge_lines(pages)
    repeated_set = set(repeated)
    offset = _page_number_offset(pages)
    extra = {"stripped_edge_lines": " | ".join(repeated)} if repeated else {}

    result = []
    for page in pages:
        lines = page.text.split("\n")
        last = lines[-1].strip() if lines else ""
        if offset is not None and last.isdigit() and page.page_number - int(last) == offset:
            lines = lines[:-1]
        n = len(lines)
        kept = [
            line
            for i, line in enumerate(lines)
            if not (line.strip() in repeated_set and (i < EDGE_LINES or i >= n - EDGE_LINES))
        ]
        result.append(
            page.model_copy(
                update={
                    "text": clean_text("\n".join(kept)),
                    "metadata": {**page.metadata, **extra},
                }
            )
        )
    return result
