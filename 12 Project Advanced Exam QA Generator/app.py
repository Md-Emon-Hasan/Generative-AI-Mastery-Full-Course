import streamlit as st
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from core.document_processing import process_document
from core.qa_generation import generate_qa_pairs
from core.chat import chat_with_document
from core.exports import create_export_files
from utils.parsing import parse_qa
from utils.file_handling import save_uploaded_file
from utils.file_handling import cleanup_temp_file

# Load environment variables
load_dotenv()

# Custom CSS
st.markdown("""
<style>
    .header {
        font-size: 2.5rem;
        color: #2c3e50;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #7f8c8d;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 5px solid #2ecc71;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    .question-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .generate-btn {
        background-color: #3498db !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.5rem !important;
        margin: 1rem 0 !important;
    }
    .sidebar-section {
        margin-bottom: 2rem;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        margin-bottom: 20px;
        border: 1px solid #eee;
        border-radius: 10px;
        padding: 15px;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 10px 15px;
        border-radius: 18px;
        margin-bottom: 10px;
        max-width: 80%;
        margin-left: auto;
    }
    .bot-message {
        background-color: #f1f1f1;
        padding: 10px 15px;
        border-radius: 18px;
        margin-bottom: 10px;
        max-width: 80%;
        margin-right: auto;
    }
    .bot-message ul {
        margin: 0;
        padding-left: 20px;
    }
    .bot-message li {
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []
if 'current_document' not in st.session_state:
    st.session_state.current_document = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'text_chunks' not in st.session_state:
    st.session_state.text_chunks = None

def main():
    st.markdown('<div class="header">Advanced Exam QA Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Generate customized questions from documents</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown('<div class="sidebar-section"><h3>⚙️ Configuration</h3></div>', unsafe_allow_html=True)
        
        num_questions = st.slider(
            "Number of Questions",
            5, 30, 10
        )
        
        complexity = st.selectbox(
            "Question Complexity",
            ["Basic", "Intermediate", "Advanced"],
            index=1
        )
        
        domain = st.selectbox(
            "Domain Focus",
            ["Technical", "Business", "Legal", "Medical", "General"],
            index=0
        )
        
        custom_prompt = st.text_area(
            "Custom Instructions",
            placeholder="E.g., '5 questions about airplanes and 5 about engines' or 'How many topics in this document?'",
            height=100
        )
        
        st.markdown("---")
        st.markdown("**Supported Formats:** PDF, DOCX, PPTX")
    
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "docx", "pptx"]
    )
    
    if uploaded_file and not st.session_state.get('processing_started', False):
        if st.button(
            "✨ Process Document",
            key="process_doc",
            type="primary",
            use_container_width=True
        ):
            st.session_state.processing_started = True
            st.session_state.current_document = uploaded_file.name
            st.rerun()
    
    if uploaded_file and st.session_state.get('processing_started', False):
        with st.spinner("Processing document..."):
            start_time = time.time()
            tmp_path = save_uploaded_file(uploaded_file)
            
            try:
                # Process document
                chroma_db, text_chunks = process_document(tmp_path)
                st.session_state.vector_db = chroma_db
                st.session_state.text_chunks = text_chunks
                
                # Display chat interface
                st.markdown("---")
                st.subheader("💬 Chat with Your Document")
                
                if len(st.session_state.chat_messages) == 0:
                    st.session_state.chat_messages = [{
                        "role": "assistant", 
                        "content": "I've processed your document. Ask me anything about it!\n- You can ask about specific topics\n- Request summaries of sections\n- Clarify any concepts"
                    }]
                
                # Display chat messages
                chat_container = st.container()
                with chat_container:
                    for message in st.session_state.chat_messages:
                        if message["role"] == "user":
                            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                        else:
                            formatted_content = message["content"].replace('\n', '<br>')
                            st.markdown(f'<div class="bot-message">{formatted_content}</div>', unsafe_allow_html=True)
                
                # Chat input
                chat_input = st.chat_input("Ask a question about the document...")
                if chat_input:
                    st.session_state.chat_messages.append({"role": "user", "content": chat_input})
                    with st.spinner("Thinking..."):
                        response = chat_with_document(chat_input)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    st.rerun()
                
                # Q&A Generation
                st.markdown("---")
                if st.button(
                    "✨ Generate Questions & Answers",
                    key="generate_qa",
                    type="primary",
                    use_container_width=True
                ):
                    qa_text = generate_qa_pairs(
                        st.session_state.text_chunks, 
                        num_questions, 
                        complexity, 
                        domain, 
                        custom_prompt
                    )
                    
                    if "Main Topics:" in qa_text:
                        st.subheader("Document Analysis")
                        st.markdown(f"```\n{qa_text}\n```")
                    else:
                        qa_pairs = parse_qa(qa_text)
                        
                        if not qa_pairs:
                            st.error("Failed to generate valid questions. Try different parameters.")
                            return
                        
                        st.session_state.current_qa_pairs = qa_pairs
                        history_entry = {
                            "timestamp": datetime.now().isoformat(),
                            "document": uploaded_file.name,
                            "questions": qa_pairs,
                            "config": {
                                "num_questions": num_questions,
                                "complexity": complexity,
                                "domain": domain,
                                "custom_prompt": custom_prompt
                            }
                        }
                        st.session_state.qa_history.append(history_entry)
                        
                        st.markdown(f"""
                        <div class="success-box">
                            ✅ Generated {len(qa_pairs)} questions in {time.time()-start_time:.1f}s
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                        
                        # Create exports
                        export_data = create_export_files(
                            qa_pairs, 
                            os.path.splitext(uploaded_file.name)[0]
                        )
                        st.session_state.export_data = export_data
            
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
            finally:
                cleanup_temp_file(tmp_path)
    
    # Display current Q&A if exists
    if 'current_qa_pairs' in st.session_state:
        st.subheader("Generated Questions & Answers")
        for i, pair in enumerate(st.session_state.current_qa_pairs, 1):
            with st.container():
                st.markdown(f"""
                <div class="question-card">
                    <h4>Q{i}: {pair['question']}</h4>
                    <p><strong>Answer:</strong> {pair['answer']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Display export options if exists
        if 'export_data' in st.session_state:
            st.subheader("Export Options")
            cols = st.columns(4)
            formats = [
                ("CSV", st.session_state.export_data["csv"], "text/csv"),
                ("JSON", st.session_state.export_data["json"], "application/json"),
                ("PDF", st.session_state.export_data["pdf"], "application/pdf"),
                ("ZIP", st.session_state.export_data["zip"], "application/zip")
            ]
            
            for col, (fmt, data, mime) in zip(cols, formats):
                with col:
                    st.download_button(
                        label=f"Download {fmt}",
                        data=data,
                        file_name=f"Interview_QA_{st.session_state.current_document.split('.')[0]}.{fmt.lower()}",
                        mime=mime,
                        use_container_width=True,
                        key=f"download_{fmt}"
                    )
    
    # History section
    if st.session_state.qa_history:
        with st.expander("📚 Generation History"):
            for idx, entry in enumerate(reversed(st.session_state.qa_history)):
                with st.container():
                    st.markdown(f"""
                    <div style="margin-bottom: 1rem; padding: 1rem; background: #f0f2f6; border-radius: 0.5rem;">
                        <strong>{entry['document']}</strong> ({entry['timestamp'][:10]})
                        <div style="font-size: 0.8rem; color: #666;">
                            {entry['config']['num_questions']} {entry['config']['complexity']} questions ({entry['config']['domain']})
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"View {idx+1}", key=f"view_{idx}"):
                        st.session_state.viewing_history_idx = len(st.session_state.qa_history) - 1 - idx
                        st.rerun()
    
    if 'viewing_history_idx' in st.session_state:
        history_item = st.session_state.qa_history[st.session_state.viewing_history_idx]
        
        st.subheader(f"History: {history_item['document']}")
        st.caption(f"Generated on {history_item['timestamp'][:10]}")
        
        for i, pair in enumerate(history_item['questions'], 1):
            with st.container():
                st.markdown(f"""
                <div class="question-card">
                    <h4>Q{i}: {pair['question']}</h4>
                    <p><strong>Answer:</strong> {pair['answer']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        if st.button("Back to History"):
            del st.session_state.viewing_history_idx
            st.rerun()

if __name__ == "__main__":
    os.makedirs("chroma_db", exist_ok=True)
    os.makedirs("temp_uploads", exist_ok=True)
    main()