import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# File Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_DIR = os.path.join(SCRIPT_DIR, "articles")
CHROMA_DIR = os.path.join(SCRIPT_DIR, "chroma_storage")

# ChromaDB Config
COLLECTION_NAME = "financial_articles"

# Text Splitting Parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200