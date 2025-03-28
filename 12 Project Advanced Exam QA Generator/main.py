import streamlit as st
import os
import tempfile
import pandas as pd
import time
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from fpdf import FPDF
import json
import zipfile
import io
from chromadb.config import Settings

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize models
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

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

def parse_qa(text):
    """Parse generated text into Q&A pairs"""
    qa_pairs = []
    current_q = None
    
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('Q'):
            if current_q:
                qa_pairs.append(current_q)
            parts = line.split(':', 1)
            if len(parts) > 1:
                current_q = {'question': parts[1].strip(), 'answer': ''}
        elif line.startswith('A') and current_q:
            parts = line.split(':', 1)
            if len(parts) > 1:
                current_q['answer'] = parts[1].strip()
    
    if current_q:
        qa_pairs.append(current_q)
    
    return qa_pairs

def load_document(file_path, file_type):
    """Load different document types"""
    if file_type == "pdf":
        loader = PyPDFLoader(file_path)
    elif file_type == "docx":
        loader = Docx2txtLoader(file_path)
    elif file_type == "pptx":
        loader = UnstructuredPowerPointLoader(file_path)
    else:
        raise ValueError("Unsupported file type")
    return loader.load()

def process_document(file_path, file_type):
    """Process document and create chunks with persistent storage"""
    pages = load_document(file_path, file_type)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        length_function=len,
        add_start_index=True
    )
    
    # Create persistent ChromaDB directory
    chroma_dir = os.path.join("chroma_db", os.path.splitext(os.path.basename(file_path))[0])
    os.makedirs(chroma_dir, exist_ok=True)
    
    # Process documents with persistent storage
    chroma_db = Chroma.from_documents(
        documents=text_splitter.split_documents(pages),
        embedding=embeddings,
        persist_directory=chroma_dir
    )
    chroma_db.persist()
    
    return chroma_db, text_splitter.split_documents(pages)

def generate_qa_pairs(text_chunks, num_questions, complexity, domain, custom_prompt=None):
    """Generate Q&A pairs with custom options"""
    context = "\n\n".join([f"Page {doc.metadata.get('page', '?')}: {doc.page_content}" 
                          for doc in text_chunks])
    
    # Default prompt template
    base_prompt = """
    As a {domain} domain expert, create {num_questions} interview questions with answers.
    Difficulty: {complexity}
    {custom_instructions}
    
    Requirements:
    1. Questions must be specific to this content
    2. Answers should be 3-5 sentences with references
    3. Include technical details for technical domains
    4. Format:
    Q1: [question]
    A1: [answer with page reference if available]
    Q2: [question]
    A2: [answer with page reference if available]
    
    Content:
    {context}
    """
    
    # Handle custom prompt scenarios
    custom_instructions = ""
    if custom_prompt:
        if "topic" in custom_prompt.lower():
            custom_instructions = f"Focus specifically on: {custom_prompt}"
        elif "how many" in custom_prompt.lower():
            base_prompt = """
            Analyze this document and provide:
            1. The main topics covered
            2. Count of questions that could be generated for each topic
            3. Estimated total questions possible
            
            Format your response as:
            Main Topics:
            - Topic 1: [count] questions
            - Topic 2: [count] questions
            
            Estimated Total: [number] questions
            
            Content:
            {context}
            """
        else:
            custom_instructions = f"Additional requirements: {custom_prompt}"
    
    prompt_template = PromptTemplate(
        input_variables=["context"],
        template=base_prompt.format(
            domain=domain,
            num_questions=num_questions,
            complexity=complexity,
            custom_instructions=custom_instructions,
            context="{context}"
        )
    )
    
    result = llm.invoke(prompt_template.format(context=context))
    return result.content

def create_export_files(qa_pairs, document_name):
    """Create multiple export formats"""
    df = pd.DataFrame(qa_pairs)
    csv = df.to_csv(index=False)
    json_data = df.to_json(orient="records", indent=2)
    
    # PDF Generation
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Interview Questions & Answers", ln=1, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Generated from: {document_name}", ln=1, align='C')
    pdf.ln(15)
    
    for i, pair in enumerate(qa_pairs, 1):
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 8, txt=f"Q{i}: {pair['question']}")
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, txt=f"{pair['answer']}")
        pdf.ln(8)
    
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    
    # ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr(f"Interview_QA_{document_name}.csv", csv)
        zip_file.writestr(f"Interview_QA_{document_name}.json", json_data)
        zip_file.writestr(f"Interview_QA_{document_name}.pdf", pdf_bytes)
    
    zip_buffer.seek(0)
    return csv, json_data, pdf_bytes, zip_buffer

def chat_with_document(query):
    """Handle chat with document using retrieval QA"""
    if 'vector_db' not in st.session_state or st.session_state.vector_db is None:
        st.error("Document not processed yet. Please upload and process a document first.")
        return "I couldn't access the document information."
    
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
        llm=llm,
        chain_type="stuff",
        retriever=st.session_state.vector_db.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt}
    )
    
    result = qa_chain({"query": query})
    return result["result"]

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
            tmp_path = None
            
            try:
                file_type = uploaded_file.name.split('.')[-1].lower()
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                # Process document and get Chroma DB
                chroma_db, text_chunks = process_document(tmp_path, file_type)
                st.session_state.vector_db = chroma_db
                st.session_state.text_chunks = text_chunks
                
                # Display chat interface immediately after processing
                st.markdown("---")
                st.subheader("💬 Chat with Your Document")
                
                # Initialize chat history if not exists
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
                            # Format assistant messages with proper line breaks
                            formatted_content = message["content"].replace('\n', '<br>')
                            st.markdown(f'<div class="bot-message">{formatted_content}</div>', unsafe_allow_html=True)
                
                # Chat input
                chat_input = st.chat_input("Ask a question about the document...")
                
                if chat_input:
                    # Add user message to chat history
                    st.session_state.chat_messages.append({"role": "user", "content": chat_input})
                    
                    # Get response from document
                    with st.spinner("Thinking..."):
                        response = chat_with_document(chat_input)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    
                    # Rerun to update the chat display
                    st.rerun()
                
                # Continue with Q&A generation only if user clicks the button
                st.markdown("---")
                if st.button(
                    "✨ Generate Questions & Answers",
                    key="generate_qa",
                    type="primary",
                    use_container_width=True
                ):
                    qa_text = generate_qa_pairs(st.session_state.text_chunks, num_questions, complexity, domain, custom_prompt)
                    
                    # Handle different response types
                    if "Main Topics:" in qa_text:  # Topic analysis response
                        st.subheader("Document Analysis")
                        st.markdown(f"```\n{qa_text}\n```")
                    else:  # Normal Q&A response
                        qa_pairs = parse_qa(qa_text)
                        
                        if not qa_pairs:
                            st.error("Failed to generate valid questions. Try different parameters.")
                            return
                        
                        # Store Q&A pairs in session state
                        st.session_state.current_qa_pairs = qa_pairs
                        
                        # Add to history
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
                        
                        # Display results
                        st.markdown(f"""
                        <div class="success-box">
                            ✅ Generated {len(qa_pairs)} questions in {time.time()-start_time:.1f}s
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add celebration balloons
                        st.balloons()    
                            
                        # Create exports
                        csv, json_data, pdf_bytes, zip_buffer = create_export_files(
                            qa_pairs, 
                            os.path.splitext(uploaded_file.name)[0]
                        )
                        
                        # Store export data in session state
                        st.session_state.export_data = {
                            "csv": csv,
                            "json": json_data,
                            "pdf": pdf_bytes,
                            "zip": zip_buffer
                        }
                    
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
    
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