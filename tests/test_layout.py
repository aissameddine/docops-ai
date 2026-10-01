from docops_ai.ingestion.layout import strip_page_furniture
from docops_ai.ingestion.models import PageContent


def make_pages(n, header="Course X - Report", offset=1):
    return [
        PageContent(
            doc_id="d",
            source="s.pdf",
            page_number=i,
            text=f"{header}\nBody of page {i}\nmore content here\n{i - offset}",
        )
        for i in range(1, n + 1)
    ]


def test_header_and_page_number_removed():
    pages = strip_page_furniture(make_pages(6))
    for page in pages:
        assert "Course X" not in page.text
        assert page.text.startswith(f"Body of page {page.page_number}")
        assert not page.text.endswith(str(page.page_number - 1))


def test_short_documents_untouched():
    pages = make_pages(2)
    assert strip_page_furniture(pages) == pages


def test_unique_edge_lines_are_kept():
    pages = make_pages(6)
    pages[2] = pages[2].model_copy(update={"text": "Unique title\nBody\nend 2"})
    out = strip_page_furniture(pages)
    assert out[2].text.startswith("Unique title")


def test_inconsistent_trailing_numbers_are_kept():
    pages = [
        PageContent(doc_id="d", source="s", page_number=i, text=f"Body {i}\n{n}")
        for i, n in enumerate([42, 7, 99, 3, 55], start=1)
    ]
    out = strip_page_furniture(pages)
    assert all(p.text.endswith(str(n)) for p, n in zip(out, [42, 7, 99, 3, 55], strict=True))


def test_removed_lines_are_kept_in_metadata():
    pages = strip_page_furniture(make_pages(6))
    assert "Course X - Report" in pages[0].metadata["stripped_edge_lines"]
