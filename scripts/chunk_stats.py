"""Compare chunking settings on every PDF in data/raw/."""

import random
import statistics
from pathlib import Path

from docops_ai.chunking import Chunk, ChunkingConfig, chunk_pages
from docops_ai.ingestion import IngestionError, ingest_pdf

SIZES = (300, 500, 800, 1200)
OVERLAP_SHARES = (0.0, 0.1, 0.2)
TINY_CHARS = 100  # chunks shorter than this are suspicious
NUMERIC_SHARE = 0.3  # "code listing" if more than 30% of lines are bare numbers
SAMPLE_CONFIG = ChunkingConfig(chunk_size=800, overlap=100)
SAMPLES = 3


def numeric_heavy(text: str) -> bool:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return False
    return sum(line.isdigit() for line in lines) / len(lines) > NUMERIC_SHARE


def describe(chunks: list[Chunk]) -> tuple[int, float, float, int, int, float, float]:
    lengths = [len(c.text) for c in chunks]
    n = len(chunks)
    return (
        n,
        statistics.mean(lengths),
        statistics.median(lengths),
        min(lengths),
        max(lengths),
        100 * sum(x < TINY_CHARS for x in lengths) / n,
        100 * sum(numeric_heavy(c.text) for c in chunks) / n,
    )


def main() -> None:
    random.seed(0)
    for pdf in sorted(Path("data/raw").glob("*.pdf")):
        try:
            pages = ingest_pdf(pdf)
        except IngestionError as exc:
            print(f"\n{pdf.name}: ERROR {exc}")
            continue
        total = sum(len(p.text) for p in pages)
        print(f"\n=== {pdf.name} ({len(pages)} pages, {total} chars)")
        print(
            f"{'size':>5} {'ovl':>4} {'chunks':>6} {'mean':>6} {'med':>5} "
            f"{'min':>4} {'max':>5} {'%tiny':>6} {'%nums':>6}"
        )
        for size in SIZES:
            for share in OVERLAP_SHARES:
                config = ChunkingConfig(chunk_size=size, overlap=int(size * share))
                chunks = chunk_pages(pages, config)
                if not chunks:
                    print(f"{size:>5} {config.overlap:>4}  no chunks")
                    continue
                n, mean, med, lo, hi, tiny, nums = describe(chunks)
                print(
                    f"{size:>5} {config.overlap:>4} {n:>6} {mean:>6.0f} {med:>5.0f} "
                    f"{lo:>4} {hi:>5} {tiny:>6.1f} {nums:>6.1f}"
                )

        chunks = chunk_pages(pages, SAMPLE_CONFIG)
        print(
            f"\n-- {SAMPLES} random chunks at size={SAMPLE_CONFIG.chunk_size}, "
            f"overlap={SAMPLE_CONFIG.overlap}"
        )
        for c in random.sample(chunks, min(SAMPLES, len(chunks))):
            print(f"[p.{c.page_number} c{c.chunk_index}, {len(c.text)} chars]")
            print(c.text)
            print("-" * 60)


if __name__ == "__main__":
    main()
