"""
RAG Tool for LangChain Agents
Wraps the knowledge base retriever as a callable tool
"""

from langchain.tools import tool
from src.rag.retriever import get_retriever


@tool
def query_knowledge_base(question: str) -> str:
    """
    Search the dental clinic knowledge base for relevant information.

    This tool searches through comprehensive FAQ documents containing:
    - Business hours and location information
    - Services offered (general dentistry, cosmetics, orthodontics, etc.)
    - Pricing and examination fees
    - Insurance coverage and payment policies
    - Dental procedures and treatment information
    - Contact information and parking details

    Use this tool when the patient asks about:
    - "What are your business hours?"
    - "How much does teeth cleaning cost?"
    - "Do you accept insurance?"
    - "What services do you offer?"
    - "Where is the clinic located?"

    Args:
        question: The patient's question in natural language (Arabic or English)

    Returns:
        A string containing the most relevant information from the knowledge base
    """
    try:
        retriever = get_retriever()

        # Query the knowledge base (k=2 for faster responses)
        docs = retriever.query(question, k=2)

        if not docs:
            return (
                "I couldn't find specific information about that in our knowledge base. "
                "Could you rephrase your question, or I can connect you with our staff for assistance."
            )

        # Combine retrieved documents with separators
        context = "\n\n---\n\n".join(docs)

        return f"Relevant information from our knowledge base:\n\n{context}"

    except Exception as e:
        return f"Error querying knowledge base: {str(e)}"


# Export all tools as a list for easy registration
rag_tools = [query_knowledge_base]
