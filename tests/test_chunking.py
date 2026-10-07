import pytest
from pydantic import ValidationError

from docops_ai.chunking import ChunkingConfig, chunk_pages
from docops_ai.ingestion import PageContent


def page(text, number=1, **meta):
    return PageContent(doc_id="doc1", source="a.pdf", page_number=number, text=text, metadata=meta)


def words(n):
    return " ".join(f"word{i}" for i in range(n))


def test_config_rejects_overlap_not_smaller_than_size():
    with pytest.raises(ValidationError):
        ChunkingConfig(chunk_size=100, overlap=100)


def test_short_text_gives_one_chunk():
    chunks = chunk_pages([page("Hello world.")], ChunkingConfig(chunk_size=100, overlap=10))
    assert len(chunks) == 1
    assert chunks[0].text == "Hello world."


def test_blank_page_gives_no_chunks():
    assert chunk_pages([page("   \n\n  ")]) == []


def test_chunks_never_exceed_chunk_size():
    config = ChunkingConfig(chunk_size=120, overlap=20)
    chunks = chunk_pages([page(words(200))], config)
    assert len(chunks) > 1
    assert all(len(c.text) <= 120 for c in chunks)


def test_offsets_match_text():
    p = page(words(150))
    for c in chunk_pages([p], ChunkingConfig(chunk_size=100, overlap=20)):
        assert p.text[c.char_start : c.char_end] == c.text


def test_consecutive_chunks_overlap():
    config = ChunkingConfig(chunk_size=100, overlap=30)
    chunks = chunk_pages([page(words(150))], config)
    for prev, nxt in zip(chunks, chunks[1:], strict=False):
        shared = prev.char_end - nxt.char_start
        assert 0 < shared <= config.overlap


def test_zero_overlap_chunks_do_not_overlap():
    chunks = chunk_pages([page(words(150))], ChunkingConfig(chunk_size=100, overlap=0))
    for prev, nxt in zip(chunks, chunks[1:], strict=False):
        assert nxt.char_start >= prev.char_end


def test_no_content_is_lost():
    p = page(words(300))
    covered = set()
    for c in chunk_pages([p], ChunkingConfig(chunk_size=90, overlap=15)):
        covered.update(range(c.char_start, c.char_end))
    missing = [i for i, ch in enumerate(p.text) if not ch.isspace() and i not in covered]
    assert missing == []


def test_prefers_paragraph_breaks():
    para1 = "A" * 60
    para2 = "B" * 60
    chunks = chunk_pages([page(f"{para1}\n\n{para2}")], ChunkingConfig(chunk_size=100, overlap=0))
    assert [c.text for c in chunks] == [para1, para2]


def test_long_unbroken_string_still_splits():
    chunks = chunk_pages([page("x" * 1000)], ChunkingConfig(chunk_size=100, overlap=10))
    assert len(chunks) >= 10
    assert all(len(c.text) <= 100 for c in chunks)


def test_page_and_source_carry_through():
    chunks = chunk_pages([page("Hello there.", number=7, title="T")])
    assert chunks[0].page_number == 7
    assert chunks[0].source == "a.pdf"
    assert chunks[0].metadata == {"title": "T"}


def test_ids_are_unique_and_deterministic():
    pages = [page(words(120), number=1), page(words(120), number=2)]
    config = ChunkingConfig(chunk_size=100, overlap=20)
    first = [c.chunk_id for c in chunk_pages(pages, config)]
    second = [c.chunk_id for c in chunk_pages(pages, config)]
    assert first == second
    assert len(set(first)) == len(first)


def test_chunk_never_spans_two_pages():
    pages = [page("first page text", number=1), page("second page text", number=2)]
    chunks = chunk_pages(pages)
    assert [c.page_number for c in chunks] == [1, 2]


def test_progress_with_large_overlap():
    config = ChunkingConfig(chunk_size=50, overlap=49)
    chunks = chunk_pages([page(words(100))], config)
    assert len(chunks) < 500
