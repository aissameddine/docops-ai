import re
from typing import NamedTuple

# PDF listings (LaTeX "lstlisting" and friends) come out of the extractor with the
# line numbers as separate lines: "1\nvoid f()\n2 {\n3\nint x;". They are noise for
# retrieval, so a run of consecutive numbers is removed, but only with strong evidence.
MIN_RUN = 4  # consecutive line numbers needed to call it a listing
MAX_GAP = 8  # max lines between two consecutive numbers (long code lines wrap)
MIN_ALONE = 0.5  # share of numbers that must sit alone on their line
MIN_CONTENT = 0.5  # share of number pairs that must have code between them

_NUMBERED = re.compile(r"^(\d{1,4})(?:\s+(\S.*))?$")


class _Numbered(NamedTuple):
    line: int  # index of the line in the page
    number: int
    rest: str  # code that follows the number on the same line ("" if alone)


def _runs(candidates: list[_Numbered]) -> list[list[_Numbered]]:
    """Group candidates into runs of consecutive numbers that are close together."""
    runs: list[list[_Numbered]] = []
    for cand in candidates:
        last = runs[-1][-1] if runs else None
        if last and cand.number == last.number + 1 and cand.line - last.line <= MAX_GAP:
            runs[-1].append(cand)
        else:
            runs.append([cand])
    return runs


def _is_listing(run: list[_Numbered]) -> bool:
    if len(run) < MIN_RUN:
        return False
    alone = sum(not c.rest for c in run) / len(run)
    pairs = list(zip(run, run[1:], strict=False))
    with_content = sum(b.line - a.line >= 2 or bool(a.rest) for a, b in pairs) / len(pairs)
    return alone >= MIN_ALONE and with_content >= MIN_CONTENT


def strip_listing_numbers(text: str) -> str:
    """Remove source-code line numbers from a page's text; leave everything else."""
    lines = text.split("\n")
    candidates = []
    for i, line in enumerate(lines):
        match = _NUMBERED.match(line.strip())
        if match:
            candidates.append(_Numbered(i, int(match.group(1)), match.group(2) or ""))

    replacement: dict[int, str] = {}
    for run in _runs(candidates):
        if _is_listing(run):
            replacement.update({c.line: c.rest for c in run})

    kept = []
    for i, line in enumerate(lines):
        if i not in replacement:
            kept.append(line)
        elif replacement[i]:
            kept.append(replacement[i])
    return "\n".join(kept)
