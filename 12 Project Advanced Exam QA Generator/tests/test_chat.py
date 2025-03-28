from unittest.mock import MagicMock
from core.chat import chat_with_document

def test_chat_with_document(monkeypatch):
    # Mock the vector_db and retriever
    mock_vector_db = MagicMock()
    mock_retriever = MagicMock()
    mock_vector_db.as_retriever.return_value = mock_retriever
    
    # Mock the LLM chain
    mock_chain = MagicMock()
    mock_chain.return_value = {"result": "Mocked response"}
    
    monkeypatch.setattr("core.chat.RetrievalQA.from_chain_type", mock_chain)
    
    # Create mock session state
    class MockSessionState:
        vector_db = mock_vector_db
    
    response = chat_with_document("test query", MockSessionState())
    assert response == "Mocked response"