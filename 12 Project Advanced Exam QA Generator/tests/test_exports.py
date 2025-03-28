import io
import pandas as pd
from core.exports import create_export_files

def test_create_export_files(sample_qa_pairs):
    exports = create_export_files(sample_qa_pairs, "test_doc")
    
    # Test CSV
    df = pd.read_csv(io.StringIO(exports["csv"]))
    assert len(df) == 2
    
    # Test JSON
    assert '"question": "What is machine learning?"' in exports["json"]
    
    # Test PDF
    assert exports["pdf"].startswith(b"%PDF")
    
    # Test ZIP
    assert exports["zip"].getvalue() is not None