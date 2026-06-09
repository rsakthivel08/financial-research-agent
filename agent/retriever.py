import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List

# Load embedding model once at module level (cached in memory)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize persistent ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="financial_docs",
    metadata={"hnsw:space": "cosine"}  # cosine similarity for semantic search
)

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Convert text chunks into vector embeddings."""
    return embedding_model.encode(texts, show_progress_bar=False).tolist()

def add_documents(chunks: List[str], metadata: List[dict], ids: List[str]):
    """
    Add document chunks to ChromaDB.
    Each chunk gets: its text, its embedding vector, metadata (source, page, type).
    """
    embeddings = embed_texts(chunks)
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadata,
        ids=ids
    )

def vector_search(query: str, n_results: int = 3) -> List[dict]:
    """
    Semantic retrieval: embed the query, find top-K similar chunks.
    This is the 'Vector search / semantic retrieval' tool in your diagram.
    """
    query_embedding = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    # Zip documents + metadata into clean dicts
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]