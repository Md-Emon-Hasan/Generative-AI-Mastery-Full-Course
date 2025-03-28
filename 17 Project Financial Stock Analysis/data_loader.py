import os
from langchain_community.document_loaders import DirectoryLoader, UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import config

def load_documents():
    """Load and preprocess HTML documents from the articles directory."""
    if not os.listdir(config.ARTICLES_DIR):
        return None, "❌ No files found in articles directory."

    loader = DirectoryLoader(
        config.ARTICLES_DIR, 
        glob="*.html", 
        loader_cls=UnstructuredHTMLLoader
    )
    documents = loader.load()

    # Split large documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)

    return chunks, f"✅ Loaded {len(chunks)} document chunks successfully."

if __name__ == "__main__":
    chunks, message = load_documents()
    print(message)
