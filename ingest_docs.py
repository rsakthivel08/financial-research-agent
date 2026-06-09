# ingest_docs.py — run ONCE before streamlit run app.py
import os
from agent.ingestion import ingest_pdf

DOCUMENTS = [
    # ── Apple ──────────────────────────────────────────────────────
    {"path": "data/uploads/apple_10Q.pdf",        "company": "Apple", "doc_type": "10-Q Filing"},
    {"path": "data/uploads/Apple_10Q(2024).pdf",  "company": "Apple", "doc_type": "10-Q Filing"},
    {"path": "data/uploads/Apple_10Q(2025).pdf",  "company": "Apple", "doc_type": "10-Q Filing"},

    # ── Tesla ──────────────────────────────────────────────────────
    {"path": "data/uploads/Tesla_10K.pdf",        "company": "Tesla", "doc_type": "10-K Filing"},
    {"path": "data/uploads/Tesla_10K(2024).pdf",  "company": "Tesla", "doc_type": "10-K Filing"},
    {"path": "data/uploads/Tesla_10K(2025).pdf",  "company": "Tesla", "doc_type": "10-K Filing"},

    # ── Amazon ─────────────────────────────────────────────────────
    {"path": "data/uploads/Amazon_10K.pdf",       "company": "Amazon", "doc_type": "10-K Filing"},
    {"path": "data/uploads/Amazon_10K(2024).pdf", "company": "Amazon", "doc_type": "10-K Filing"},
    {"path": "data/uploads/Amazon_10K(2025).pdf", "company": "Amazon", "doc_type": "10-K Filing"},

    # ── Microsoft ──────────────────────────────────────────────────
    {"path": "data/uploads/Microsoft_11-K.pdf",       "company": "Microsoft", "doc_type": "11-K Filing"},
    {"path": "data/uploads/Microsoft_10-Q.pdf",       "company": "Microsoft", "doc_type": "10-Q Filing"},
    {"path": "data/uploads/Microsoft_10-Q(2024).pdf", "company": "Microsoft", "doc_type": "10-Q Filing"},
    {"path": "data/uploads/Microsoft_10-Q(2025).pdf", "company": "Microsoft", "doc_type": "10-Q Filing"},

    # ── Nvidia ─────────────────────────────────────────────────────
    {"path": "data/uploads/Nvidia_10Q.pdf",        "company": "Nvidia", "doc_type": "10-Q Filing"},
    {"path": "data/uploads/Nvidia_10Q(2024).pdf",  "company": "Nvidia", "doc_type": "10-Q Filing"},
    {"path": "data/uploads/Nvidia_10Q(2025).pdf",  "company": "Nvidia", "doc_type": "10-Q Filing"},
]

if __name__ == "__main__":
    print("🚀 Starting document ingestion...\n")
    success, skipped, failed = 0, 0, 0

    for doc in DOCUMENTS:
        path = doc["path"]
        if not os.path.exists(path):
            print(f"⚠️  Skipping (not found) : {path}")
            skipped += 1
            continue
        try:
            print(f"📄 Ingesting [{doc['company']} | {doc['doc_type']}]: {os.path.basename(path)}")
            n = ingest_pdf(path, doc["doc_type"], doc["company"])
            print(f"   ✅ {n} chunks stored\n")
            success += 1
        except Exception as e:
            print(f"   ❌ Failed: {e}\n")
            failed += 1

    print("─" * 50)
    print(f"✅ Ingested : {success} files")
    print(f"⚠️  Skipped  : {skipped} files")
    print(f"❌ Failed   : {failed} files")
    print("\n🎉 Done! Now run: streamlit run app.py")