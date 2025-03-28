import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from services.llm import get_llm

def chat_with_document(query):
    """Handle chat with document using retrieval QA"""
    if 'vector_db' not in st.session_state or st.session_state.vector_db is None:
        return "Document not processed yet. Please upload and process a document first."
    
    prompt_template = """
    You are a helpful assistant that answers questions about the provided document.
    Use the following pieces of context to answer the question at the end.
    Always follow these rules:
    - Provide clear, concise answers in bullet points when appropriate
    - Keep explanations brief but informative
    - Reference page numbers if available in the context
    - If you don't know the answer, say you don't know
    
    Context:
    {context}
    
    Question: {question}
    
    Answer in this format:
    - [Main point 1] (Brief explanation)
    - [Main point 2] (Brief explanation)
    [Additional context if needed]
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=get_llm(),
        chain_type="stuff",
        retriever=st.session_state.vector_db.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt}
    )
    
    result = qa_chain({"query": query})
    return result["result"]