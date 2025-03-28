import streamlit as st
import config
from vector_store import index_documents, get_collection
from query_engine import query_documents

# Streamlit Page Configuration
st.set_page_config(page_title="📊 Financial Chatbot", layout="wide")
st.title("📊 Financial Document Analyzer")
st.caption("Ask questions about your financial documents")

# Sidebar: Document Management
with st.sidebar:
    st.header("📂 Document Management")
    
    if st.button("🔄 Rebuild Document Index", help="Process all HTML files in /articles"):
        with st.spinner("Indexing documents..."):
            success, message = index_documents()
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)

    st.markdown("### 📌 How to Use")
    st.markdown("""
    1️⃣ Place HTML files in `/articles` folder  
    2️⃣ Click 'Rebuild Index' above  
    3️⃣ Ask questions in the main interface  
    """)

    # Collection Status
    if get_collection():
        st.success("✅ Documents are indexed")
    else:
        st.warning("⚠️ No indexed documents found")

# Main Interface
question = st.text_area("🔎 Enter your question:", placeholder="e.g. What are the key risks for Tesla?", height=150)

if st.button("Analyze Documents", type="primary") and question.strip():
    with st.spinner("Searching documents..."):
        answer = query_documents(question)

    st.subheader("📖 Analysis Results")
    st.markdown(answer)

    with st.expander("📌 Document References"):
        st.info("Document numbers above correspond to the most relevant sources.")

