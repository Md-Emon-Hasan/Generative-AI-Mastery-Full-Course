from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize models only once
_llm = None
_embeddings = None

def get_llm():
    """Get the LLM model instance (singleton pattern)"""
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro", 
            temperature=0.7
        )
    return _llm

def get_embeddings():
    """Get the embeddings model instance (singleton pattern)"""
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001"
        )
    return _embeddings