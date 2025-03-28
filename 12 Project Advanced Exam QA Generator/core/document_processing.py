import os
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import Docx2txtLoader
from langchain.document_loaders import UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from services.llm import get_embeddings

def load_document(file_path):
    """Load document based on file extension
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        list: List of document pages with metadata
    
    Raises:
        ValueError: If file type is unsupported
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    loader_map = {
        '.pdf': PyPDFLoader,
        '.docx': Docx2txtLoader,
        '.pptx': UnstructuredPowerPointLoader
    }
    
    if file_ext not in loader_map:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    loader = loader_map[file_ext](file_path)
    return loader.load()

def process_document(file_path):
    """Process document into chunks and create vector store
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        tuple: (Chroma vector store, list of text chunks)
    """
    # Load and split document
    pages = load_document(file_path)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        length_function=len,
        add_start_index=True
    )
    
    chunks = text_splitter.split_documents(pages)
    
    # Create persistent storage directory
    doc_name = os.path.splitext(os.path.basename(file_path))[0]
    chroma_dir = os.path.join("data", "chroma_db", doc_name)
    os.makedirs(chroma_dir, exist_ok=True)
    
    # Create and persist vector store
    chroma_db = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=chroma_dir
    )
    chroma_db.persist()
    
    return chroma_db, chunks

def get_document_type(file_path):
    """Get document type from file extension
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        str: Document type (pdf, docx, pptx)
    """
    return os.path.splitext(file_path)[1].lower()[1:]