"""
RAG Retriever for Dental Clinic FAQ
Connects to existing ChromaDB vector store
"""

import os
import chromadb
from langchain_chroma import Chroma
from langchain_community.embeddings import JinaEmbeddings
from src.config.settings import settings

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"


class KnowledgeBaseRetriever:
    """
    Retriever for the dental clinic FAQ knowledge base.

    Uses ChromaDB for semantic search over clinic information:
    - Business hours, location, contact info
    - Services offered and pricing
    - Insurance and payment policies
    - Common dental procedures and FAQs
    """

    def __init__(self):
        """Initialize connection to existing ChromaDB"""

        # Initialize Jina AI embeddings
        if not settings.jina_api_key:
            raise ValueError("JINA_API_KEY is required in .env file")

        self.embeddings = JinaEmbeddings(
            jina_api_key=settings.jina_api_key,
            model_name=settings.jina_embedding_model
        )

        # Connect to existing ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=settings.chroma_db_path)

        # Load existing collection
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=settings.chroma_collection_name,
            embedding_function=self.embeddings,
        )

        # Create retriever with optimized parameters
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 2}  # Retrieve top 2 chunks (reduced from 3 for speed)
        )

    def query(self, question: str, k: int = 2) -> list[str]:
        """
        Query the knowledge base and return relevant documents.

        Args:
            question: User's question in natural language
            k: Number of documents to retrieve (default: 2)

        Returns:
            List of relevant document texts
        """
        # Update retriever with custom k if needed
        if k != 2:
            self.retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )

        # Retrieve documents
        docs = self.retriever.invoke(question)

        # Extract text content from documents
        return [doc.page_content for doc in docs]

    def query_with_scores(self, question: str, k: int = 3) -> list[tuple[str, float]]:
        """
        Query the knowledge base and return documents with relevance scores.

        Args:
            question: User's question in natural language
            k: Number of documents to retrieve (default: 3)

        Returns:
            List of tuples (document_text, similarity_score)
        """
        results = self.vectorstore.similarity_search_with_score(question, k=k)
        return [(doc.page_content, score) for doc, score in results]


# Singleton instance
_retriever_instance = None


def get_retriever() -> KnowledgeBaseRetriever:
    """Get or create a singleton retriever instance"""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = KnowledgeBaseRetriever()
    return _retriever_instance
