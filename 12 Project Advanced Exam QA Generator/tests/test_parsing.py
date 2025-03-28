from utils.parsing import parse_qa, validate_qa_pairs

def test_parse_qa():
    text = """
    Q1: What is Python?
    A1: A programming language.
    Q2: What is GPT?
    A2: An AI model.
    """
    result = parse_qa(text)
    assert len(result) == 2
    assert result[0]["question"] == "What is Python?"
    assert result[1]["answer"] == "An AI model."

def test_validate_qa_pairs(sample_qa_pairs):
    assert validate_qa_pairs(sample_qa_pairs) is True
    assert validate_qa_pairs([{"question": "Only question"}]) is False