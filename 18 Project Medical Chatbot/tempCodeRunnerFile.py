from src.helper import load_pdf_file, text_split, download_hugging_face_embeddings
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define ChromaDB storage directory
CHROMADB_PERSIST_DIR = "./chroma_db"

# Ensure the 'Data/' directory exists
DATA_DIR = "data/"  # Adjust if your folder is named differently
if not os.path.exists(DATA_DIR):
    raise FileNotFoundError(f"Directory not found: '{DATA_DIR}'")

# Load and process PDF data
extracted_data = load_pdf_file(data=DATA_DIR)
text_chunks = text_split(extracted_data)

# Load embeddings model
embeddings = download_hugging_face_embeddings()

# Create or load ChromaDB vector store
vector_store = Chroma(
    persist_directory=CHROMADB_PERSIST_DIR,
    embedding_function=embeddings
)

# Add documents to ChromaDB
vector_store.add_documents(text_chunks)

print("ChromaDB setup complete. Embeddings stored successfully.")
