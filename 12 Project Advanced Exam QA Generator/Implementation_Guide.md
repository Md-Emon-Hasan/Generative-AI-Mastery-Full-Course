### **1. File Creation Order & Implementation Flow**
**(Follow this sequence exactly)**

#### **Step 1: Project Setup**
1. Create base folder:  
   ```bash
   mkdir exam_qa_generator
   cd exam_qa_generator
   ```

2. Initialize these files first:  
   ```bash
   touch app.py requirements.txt .env
   mkdir core services utils data
   ```

#### **Step 2: Core Infrastructure**
1. **Services Layer** (Create first - foundational):  
   ```bash
   touch services/__init__.py services/llm_service.py
   ```
   - Implement `llm_service.py` first (Gemini setup)

2. **Utils Layer**:  
   ```bash
   touch utils/__init__.py utils/file_utils.py utils/text_parser.py
   ```
   - Add file handling (`file_utils.py`)  
   - Add text parsing (`text_parser.py`)

#### **Step 3: Core Functionality**
1. **Document Processing**:  
   ```bash
   touch core/__init__.py core/document_processor.py
   ```
   - Implement file loading and chunking

2. **Q&A Engine**:  
   ```bash
   touch core/qa_engine.py
   ```
   - Add Gemini prompt templates

3. **Chat System**:  
   ```bash
   touch core/chat_interface.py
   ```
   - Build RetrievalQA chain

4. **Exports**:  
   ```bash
   touch core/export_manager.py
   ```
   - Add CSV/PDF export logic

#### **Step 4: UI & Final Integration**
1. **Main App**:  
   - Complete `app.py` last (ties everything together)

---

### **2. What Goes Where?**  
*(File-by-File Implementation Guide)*

#### **A. First: `services/llm_service.py**
```python
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

# Singleton pattern implementation here
def get_llm():
    # Returns configured Gemini LLM
    pass

def get_embeddings():
    # Returns embedding model
    pass
```

#### **B. Next: `utils/file_utils.py**
```python
import os
import uuid

def save_uploaded_file(uploaded_file):
    # Saves file to temp_uploads with UUID
    pass

def cleanup_temp_file(path):
    # Deletes temporary files
    pass
```

#### **C. Then: `core/document_processor.py**
```python
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader
from services.llm_service import get_embeddings

def load_document(file_path):
    # Uses appropriate loader based on file extension
    pass

def process_document(file_path):
    # Splits text and creates ChromaDB vectorstore
    pass
```

#### **D. Now: `core/qa_engine.py**
```python
from langchain.prompts import PromptTemplate
from services.llm_service import get_llm

def generate_qa_pairs(text_chunks, num_questions, complexity, domain):
    # Prompt engineering for Gemini
    pass
```

#### **E. Then: `core/chat_interface.py**
```python
from langchain.chains import RetrievalQA
from services.llm_service import get_llm

def chat_with_document(query, session_state):
    # RetrievalQA with session_state.vector_db
    pass
```

#### **F. Finally: `app.py**
```python
# Import ALL modules here
from core.document_processor import process_document
from core.qa_engine import generate_qa_pairs
# ... all other imports

# Streamlit UI implementation
def main():
    # 1. File upload handling
    # 2. Process document button
    # 3. Chat interface
    # 4. Q&A generation
    pass
```

---

### **3. Critical Path Checklist**
1. **Environment Setup**  
   - Complete `.env` with `GOOGLE_API_KEY`  
   - Install dependencies via `requirements.txt`

2. **Execution Order**  
   ```python
   # app.py workflow:
   uploaded_file → save_uploaded_file() → process_document() → 
   generate_qa_pairs() → create_export_files()
   ```

3. **Data Flow**  
   ```
   User Upload → Temp Storage → ChromaDB → 
   Gemini → Q&A Pairs → Export Files
   ```

---

### **4. Pro Tips**
1. **Debugging Sequence**:  
   - Test `llm_service.py` first with simple prompts  
   - Validate document loading before adding embeddings  
   - Check ChromaDB persistence in `data/chroma_db/`

2. **Validation Points**:  
   - After implementing each module, run:  
     ```python
     python3 -c "from services.llm_service import get_llm; print(get_llm().invoke('Test prompt'))"
     ```

3. **Industry Shortcut**:  
   Use this shell command to verify imports:  
   ```bash
   python3 -c "from core.document_processor import process_document; print('All imports work!')"
   ```

---

This guide ensures you:  
✅ **Avoid circular imports**  
✅ **Maintain proper dependency order**  
✅ **Follow industry-standard layering**  
✅ **Test components incrementally**  

For each file, implement the functions shown in the previous code templates, following this exact sequence.