import pytest
from core.document_processing import load_document, process_document
from langchain.schema import Document

def test_load_pdf(sample_pdf_path):
    docs = load_document(sample_pdf_path)
    assert len(docs) > 0
    assert isinstance(docs[0], Document)

def test_process_document(sample_pdf_path):
    chroma_db, chunks = process_document(sample_pdf_path)
    assert chroma_db is not None
    assert len(chunks) > 0
    assert "page_content" in chunks[0].dict()

def test_unsupported_file_type(tmp_path):
    invalid_file = tmp_path / "test.xyz"
    invalid_file.write_text("dummy content")
    with pytest.raises(ValueError):
        load_document(str(invalid_file))