from langchain.prompts import PromptTemplate
from services.llm import get_llm
from utils.parsing import parse_qa

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
    
    result = get_llm().invoke(prompt_template.format(context=context))
    return result.content