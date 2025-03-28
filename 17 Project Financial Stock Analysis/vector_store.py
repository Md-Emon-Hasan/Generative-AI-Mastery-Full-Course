import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_community.vectorstores import Chroma as LangchainChroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import config
from data_loader import load_documents

def index_documents():
    """Index financial documents into ChromaDB."""
    try:
        chunks, message = load_documents()
        if chunks is None:
            return False, message

        # Define embedding function
        embedding_function = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=config.GOOGLE_API_KEY
        )

        # Create or update ChromaDB collection
        vector_db = LangchainChroma.from_documents(
            documents=chunks,
            embedding=embedding_function,
            persist_directory=config.CHROMA_DIR,
            collection_name=config.COLLECTION_NAME
        )
        vector_db.persist()

        return True, f"✅ Indexed {len(chunks)} document chunks successfully."

    except Exception as e:
        return False, f"❌ Indexing error: {str(e)}"

def get_collection():
    """Retrieve ChromaDB collection."""
    try:
        client = chromadb.PersistentClient(path=config.CHROMA_DIR)
        return client.get_collection(
            name=config.COLLECTION_NAME,
            embedding_function=embedding_functions.GoogleGenerativeAiEmbeddingFunction(
                api_key=config.GOOGLE_API_KEY,
                model_name="models/embedding-001"
            )
        )
    except ValueError:
        return None

if __name__ == "__main__":
    success, message = index_documents()
    print(message)
