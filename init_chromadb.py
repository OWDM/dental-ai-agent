"""
Initialize ChromaDB with Jina Embeddings
This script loads documents from rag-doc/ and creates vector embeddings
"""

import os
import chromadb
from langchain_community.embeddings import JinaEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from src.config.settings import settings

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"


def initialize_chroma():
    """Initialize ChromaDB with documents from rag-doc/"""

    print("=" * 60)
    print("🔄 Initializing ChromaDB with Jina Embeddings")
    print("=" * 60)

    # 1. Load documents
    print("\n📂 Loading documents from rag-doc/...")
    loader = TextLoader("rag-doc/mock-data.txt", encoding="utf-8")
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} document(s)")

    # 2. Split into chunks
    print("\n✂️  Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # Characters per chunk
        chunk_overlap=50,  # Overlap to maintain context
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} chunks")

    # 3. Initialize Jina embeddings
    print("\n🧬 Initializing Jina embeddings...")
    if not settings.jina_api_key:
        print("❌ Error: JINA_API_KEY not found in .env file")
        return False

    embeddings = JinaEmbeddings(
        jina_api_key=settings.jina_api_key,
        model_name=settings.jina_embedding_model
    )
    print(f"✅ Using model: {settings.jina_embedding_model}")

    # 4. Delete old collection if it exists
    print("\n🗑️  Removing old ChromaDB collection...")
    client = chromadb.PersistentClient(path=settings.chroma_db_path)
    try:
        client.delete_collection(name=settings.chroma_collection_name)
        print("✅ Deleted old collection")
    except Exception:
        print("ℹ️  No existing collection found (this is fine)")

    # 5. Create new vector store
    print("\n💾 Creating new ChromaDB collection...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=settings.chroma_collection_name,
        persist_directory=settings.chroma_db_path,
    )
    print(f"✅ Created collection: {settings.chroma_collection_name}")

    # 6. Test retrieval
    print("\n🧪 Testing retrieval...")
    test_query = "What are the business hours?"
    results = vectorstore.similarity_search(test_query, k=2)
    print(f"✅ Retrieved {len(results)} results for test query")
    print("\nSample result:")
    print("-" * 60)
    print(results[0].page_content[:200] + "...")
    print("-" * 60)

    print("\n" + "=" * 60)
    print("✅ ChromaDB Initialization Complete!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   • Collection: {settings.chroma_collection_name}")
    print(f"   • Chunks: {len(chunks)}")
    print(f"   • Embedding Model: {settings.jina_embedding_model}")
    print(f"   • Path: {settings.chroma_db_path}")
    print("\n🚀 You can now run: python main.py")

    return True


if __name__ == "__main__":
    try:
        initialize_chroma()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Check that JINA_API_KEY is set in .env")
        print("   2. Verify rag-doc/mock-data.txt exists")
        print("   3. Ensure you have internet connection for Jina API")
