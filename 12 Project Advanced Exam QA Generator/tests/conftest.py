import pytest
import os
from pathlib import Path
from core.document_processing import process_document
from services.llm import get_llm, get_embeddings

@pytest.fixture
def sample_pdf_path():
    test_dir = Path(__file__).parent
    return str(test_dir / "test_data/sample.pdf")

@pytest.fixture
def sample_text_chunks():
    return [
        {"page_content": "Machine learning is a subset of AI.", "metadata": {"page": 1}},
        {"page_content": "Deep learning uses neural networks.", "metadata": {"page": 2}}
    ]

@pytest.fixture
def sample_qa_pairs():
    return [
        {"question": "What is machine learning?", "answer": "A subset of AI."},
        {"question": "What does deep learning use?", "answer": "Neural networks."}
    ]

@pytest.fixture(scope="module")
def llm():
    return get_llm()

@pytest.fixture(scope="module")
def embeddings():
    return get_embeddings()