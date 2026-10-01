import pymupdf
import pytest

from docops_ai.ingestion import IngestionError, ingest_pdf


@pytest.fixture
def sample_pdf(tmp_path):
    path = tmp_path / "sample.pdf"
    doc = pymupdf.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((72, 72), f"Hello from page {i + 1}")
    doc.set_metadata({"title": "Sample", "author": "Tester"})
    doc.save(str(path))
    doc.close()
    return path


def test_one_record_per_page(sample_pdf):
    pages = ingest_pdf(sample_pdf)
    assert [p.page_number for p in pages] == [1, 2, 3]
    assert "Hello from page 2" in pages[1].text
    assert pages[0].source == "sample.pdf"


def test_metadata_extracted(sample_pdf):
    pages = ingest_pdf(sample_pdf)
    assert pages[0].metadata["title"] == "Sample"
    assert pages[0].metadata["author"] == "Tester"


def test_doc_id_is_stable(sample_pdf):
    first = ingest_pdf(sample_pdf)[0].doc_id
    second = ingest_pdf(sample_pdf)[0].doc_id
    assert first == second
    assert len(first) == 16


def test_blank_page_is_flagged_empty(tmp_path):
    path = tmp_path / "blank.pdf"
    doc = pymupdf.open()
    doc.new_page()
    doc.save(str(path))
    doc.close()
    assert ingest_pdf(path)[0].is_empty


def test_missing_file_raises(tmp_path):
    with pytest.raises(IngestionError):
        ingest_pdf(tmp_path / "nope.pdf")


def test_non_pdf_raises(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("hello")
    with pytest.raises(IngestionError):
        ingest_pdf(path)


def test_corrupt_pdf_raises(tmp_path):
    path = tmp_path / "broken.pdf"
    path.write_bytes(b"this is not a pdf")
    with pytest.raises(IngestionError):
        ingest_pdf(path)


def test_encrypted_pdf_raises(tmp_path):
    path = tmp_path / "locked.pdf"
    doc = pymupdf.open()
    doc.new_page()
    doc.save(
        str(path),
        encryption=pymupdf.PDF_ENCRYPT_AES_256,
        user_pw="secret",
        owner_pw="owner",
    )
    doc.close()
    with pytest.raises(IngestionError):
        ingest_pdf(path)
