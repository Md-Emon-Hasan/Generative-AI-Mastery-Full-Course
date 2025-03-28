import pandas as pd
from fpdf import FPDF
import json
import zipfile
import io
import os

def create_export_files(qa_pairs, document_name):
    """Create multiple export formats (CSV, JSON, PDF, ZIP) from Q&A pairs
    
    Args:
        qa_pairs (list): List of dictionaries with 'question' and 'answer' keys
        document_name (str): Base name of the source document
    
    Returns:
        dict: Dictionary containing export data in different formats
            {
                "csv": CSV string,
                "json": JSON string,
                "pdf": PDF bytes,
                "zip": ZIP file buffer
            }
    """
    # Create DataFrame from Q&A pairs
    df = pd.DataFrame(qa_pairs)
    
    # Generate CSV
    csv = df.to_csv(index=False)
    
    # Generate JSON
    json_data = df.to_json(orient="records", indent=2)
    
    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # PDF Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Interview Questions & Answers", ln=1, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Generated from: {document_name}", ln=1, align='C')
    pdf.ln(15)
    
    # Add Q&A content
    for i, pair in enumerate(qa_pairs, 1):
        pdf.set_font("Arial", 'B', 12)
        pdf.multi_cell(0, 8, txt=f"Q{i}: {pair['question']}")
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 6, txt=f"{pair['answer']}")
        pdf.ln(8)
    
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    
    # Create ZIP archive containing all formats
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr(f"Interview_QA_{document_name}.csv", csv)
        zip_file.writestr(f"Interview_QA_{document_name}.json", json_data)
        zip_file.writestr(f"Interview_QA_{document_name}.pdf", pdf_bytes)
    
    zip_buffer.seek(0)
    
    return {
        "csv": csv,
        "json": json_data,
        "pdf": pdf_bytes,
        "zip": zip_buffer
    }