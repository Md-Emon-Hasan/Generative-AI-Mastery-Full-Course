import os
import tempfile
import uuid

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary location
    
    Args:
        uploaded_file (UploadedFile): Streamlit uploaded file object
        
    Returns:
        str: Path to the saved temporary file
    """
    temp_dir = os.path.join("data", "temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    
    file_ext = os.path.splitext(uploaded_file.name)[1]
    temp_path = os.path.join(temp_dir, f"temp_{uuid.uuid4().hex}{file_ext}")
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    return temp_path

def cleanup_temp_file(file_path):
    """Clean up temporary file if it exists
    
    Args:
        file_path (str): Path to the temporary file
    """
    if file_path and os.path.exists(file_path):
        try:
            os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting temp file: {e}")

def ensure_data_dirs():
    """Ensure required data directories exist"""
    dirs = [
        os.path.join("data", "chroma_db"),
        os.path.join("data", "temp_uploads")
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)