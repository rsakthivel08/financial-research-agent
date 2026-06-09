import fitz  # PyMuPDF
import uuid
from agent.retriever import add_documents

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split long text into overlapping chunks.
    Overlap ensures context isn't lost at chunk boundaries.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def ingest_pdf(file_path: str, doc_type: str, company: str):
    """
    Extract text from a PDF (annual report, earnings call transcript),
    chunk it, and store in ChromaDB with metadata tags.
    """
    doc = fitz.open(file_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    chunks = chunk_text(full_text)
    metadatas = [
        {"source": file_path, "type": doc_type, "company": company, "chunk_index": i}
        for i, _ in enumerate(chunks)
    ]
    # Generate unique IDs for each chunk so ChromaDB can deduplicate
    ids = [str(uuid.uuid4()) for _ in chunks]
    add_documents(chunks, metadatas, ids)
    return len(chunks)