# **Documentation Exam QA Generator**

## **1. Project Overview**
**Exam QA Generator** is an AI-powered application that automatically generates exam questions and answers from uploaded documents (PDF, DOCX, PPTX). It includes:
- **Document Processing**: Extracts text and creates embeddings.
- **Q&A Generation**: Uses Google Gemini to generate structured questions and answers.
- **Chat Interface**: Allows users to ask questions about the document.
- **Export Options**: Supports CSV, JSON, PDF, and ZIP exports.

---

## **2. System Architecture**
### **High-Level Architecture**
```
┌───────────────────────┐       ┌───────────────────────┐
│      Streamlit UI     │──────▶│    Document Processor  │
└───────────────────────┘       └───────────┬───────────┘
                                            │
┌───────────────────────┐       ┌───────────▼───────────┐
│       Chat Engine     │◀──────│   Vector DB (Chroma)  │
└───────────────────────┘       └───────────┬───────────┘
                                            │
┌───────────────────────┐       ┌───────────▼───────────┐
│   Q&A Generator (LLM) │◀──────│   Text Chunks (LangChain)  │
└───────────────────────┘       └───────────────────────┘
```

### **Tech Stack**
| Component           | Technology |
|---------------------|------------|
| **Frontend**        | Streamlit  |
| **Backend**         | Python     |
| **LLM**            | Google Gemini (via LangChain) |
| **Vector DB**      | ChromaDB   |
| **Document Parsing**| PyPDF, Docx2txt, UnstructuredPPT |
| **Export Formats**  | CSV, JSON, PDF (FPDF), ZIP |

---

## **3. Setup & Installation**
### **Prerequisites**
- Python 3.9+
- Google API Key (for Gemini)
- `pip` package manager

### **Installation**
```bash
# Clone the repository
git clone https://github.com/your-repo/exam-qa-generator.git
cd exam-qa-generator

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### **Run the Application**
```bash
streamlit run app.py
```

---

## **4. Configuration**
### **Environment Variables**
| Variable          | Description |
|-------------------|-------------|
| `GOOGLE_API_KEY`  | Google Gemini API Key |
| `CHROMA_DB_PATH`  | (Optional) Custom ChromaDB storage path |

### **File Structure**
```
exam_qa_generator/
├── app.py               # Main Streamlit app
├── core/                # Core logic
│   ├── document_processing.py  # Doc parsing & chunking
│   ├── qa_generation.py        # LLM-based Q&A generation
│   ├── chat.py                 # Document Q&A chat
│   └── exports.py              # Export handlers (CSV, PDF, etc.)
├── utils/               # Helper functions
│   ├── file_handling.py # Temp file management
│   └── parsing.py       # Text parsing
├── services/            # External services
│   └── llm.py          # LLM & embeddings setup
└── data/                # Persistent storage
    ├── chroma_db/      # Vector embeddings
    └── temp_uploads/   # Temporary files
```

---

## **5. Core Modules**
### **1. Document Processing (`core/document_processing.py`)**
- **Functionality**:
  - Loads PDF, DOCX, PPTX files.
  - Splits text into chunks.
  - Generates embeddings and stores in ChromaDB.
- **Key Methods**:
  - `load_document(file_path)` → Extracts text.
  - `process_document(file_path)` → Creates embeddings.

### **2. Q&A Generation (`core/qa_generation.py`)**
- **Functionality**:
  - Uses Google Gemini to generate structured Q&A pairs.
  - Supports custom prompts and complexity levels.
- **Key Methods**:
  - `generate_qa_pairs(text_chunks, num_questions, complexity, domain)` → Returns Q&A list.

### **3. Chat Engine (`core/chat.py`)**
- **Functionality**:
  - Allows users to ask questions about the document.
  - Uses RetrievalQA for context-aware answers.
- **Key Methods**:
  - `chat_with_document(query)` → Returns AI response.

### **4. Export Manager (`core/exports.py`)**
- **Functionality**:
  - Generates CSV, JSON, PDF, and ZIP exports.
- **Key Methods**:
  - `create_export_files(qa_pairs, document_name)` → Returns export files.

---

## **6. API Reference**
### **LLM Service (`services/llm.py`)**
```python
def get_llm() -> ChatGoogleGenerativeAI:
    """Returns Google Gemini LLM instance."""
    
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Returns text embeddings model."""
```

### **Parsing Utilities (`utils/parsing.py`)**
```python
def parse_qa(text: str) -> List[Dict[str, str]]:
    """Converts raw LLM output into structured Q&A pairs."""
```

### **File Handling (`utils/file_handling.py`)**
```python
def save_uploaded_file(uploaded_file) -> str:
    """Saves uploaded file to temp storage."""
    
def cleanup_temp_file(file_path: str) -> None:
    """Deletes temporary files."""
```

---

## **7. Deployment**
### **Option 1: Local Deployment**
```bash
streamlit run app.py
```

### **Option 2: Docker**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```
```bash
docker build -t exam-qa-generator .
docker run -p 8501:8501 exam-qa-generator
```

### **Option 3: Cloud (AWS/GCP)**
- Use **Streamlit Cloud**, **AWS App Runner**, or **Google Cloud Run**.
- Ensure `GOOGLE_API_KEY` is set in environment variables.

---

## **8. Testing**
### **Unit Tests**
```bash
pytest tests/
```
Example test cases:
- Document loading (`test_document_processing.py`)
- Q&A parsing (`test_parsing.py`)
- Export generation (`test_exports.py`)

---

## **9. Future Improvements**
- **Multi-document support** (merge multiple files).
- **Batch processing** (generate Q&A for multiple files at once).
- **User authentication** (save history per user).
- **Enhanced exports** (LaTeX, Markdown).

---

## **10. Contact Information:**
- **Email:** [iconicemon01@gmail.com](mailto:iconicemon01@gmail.com)
- **GitHub:** [Md-Emon-Hasan](https://github.com/Md-Emon-Hasan)
- **LinkedIn:** [Md Emon Hasan](https://www.linkedin.com/in/md-emon-hasan)
- **Facebook:** [Md Emon Hasan](https://www.facebook.com/mdemon.hasan2001/)

---

## **11. License**
MIT License. See `LICENSE` for details.

---