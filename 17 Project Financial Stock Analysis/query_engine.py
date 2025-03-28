import google.generativeai as genai
import config
from vector_store import get_collection

# Initialize Gemini API
genai.configure(api_key=config.GOOGLE_API_KEY)

def query_documents(question):
    """Retrieve answers from indexed documents using Gemini."""
    try:
        collection = get_collection()
        if collection is None:
            return "⚠️ No document collection found. Please index documents first."

        # Retrieve top 3 most relevant documents
        results = collection.query(query_texts=[question], n_results=3)

        if not results["documents"]:
            return "❌ No relevant information found in documents."

        # Prepare context from retrieved documents
        context = "\n\n---\n\n".join(
            f"📄 Document {i+1}:\n{doc}" for i, doc in enumerate(results["documents"][0])
        )

        # Generate response using Gemini
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(
            f"""You are a financial analyst providing insights from the documents:
            
            {context}
            
            Question: {question}
            
            Guidelines:
            - Answer based on the provided context
            - Reference document numbers where applicable
            - If unsure, state: "This information isn't available in the documents"
            """
        )
        return response.text

    except Exception as e:
        return f"❌ Query error: {str(e)}"

if __name__ == "__main__":
    question = "What are the key risks for Nvidia?"
    print(query_documents(question))
