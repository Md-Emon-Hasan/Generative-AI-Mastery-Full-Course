from services.llm import get_llm, get_embeddings

def test_llm_initialization():
    llm = get_llm()
    assert llm.model_name == "gemini-1.5-pro"
    assert llm.temperature == 0.7

def test_embeddings_initialization():
    embeddings = get_embeddings()
    assert embeddings.model == "models/embedding-001"