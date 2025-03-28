def parse_qa(text):
    """Parse generated text into Q&A pairs
    
    Args:
        text (str): Generated text containing Q&A pairs
        
    Returns:
        list: List of dictionaries with 'question' and 'answer' keys
    """
    qa_pairs = []
    current_q = None
    
    for line in text.split('\n'):
        line = line.strip()
        
        # Handle question lines
        if line.startswith('Q'):
            if current_q:  # Save previous question if exists
                qa_pairs.append(current_q)
            
            parts = line.split(':', 1)
            if len(parts) > 1:
                current_q = {
                    'question': parts[1].strip(), 
                    'answer': ''
                }
        
        # Handle answer lines
        elif line.startswith('A') and current_q:
            parts = line.split(':', 1)
            if len(parts) > 1:
                current_q['answer'] = parts[1].strip()
    
    # Add the last question if it exists
    if current_q:
        qa_pairs.append(current_q)
    
    return qa_pairs