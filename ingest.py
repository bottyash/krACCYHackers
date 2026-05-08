"""
ingest.py — chunk triage_protocol.md and load into ChromaDB
Run this ONCE before main.py
"""
import os, re, chromadb
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer

PROTOCOL_PATH = "../participants/protocols/triage_protocol.md"
DB_PATH       = "./chroma_db"

def chunk_protocol(path: str) -> list[dict]:
    """Split protocol by ## headings into chunks with metadata."""
    text = open(path).read()
    sections = re.split(r'\n(?=## )', text)
    chunks = []
    for i, sec in enumerate(sections):
        sec = sec.strip()
        if not sec:
            continue
        title_match = re.match(r'##\s+(.+)', sec.splitlines()[0])
        title = title_match.group(1) if title_match else f"Section {i}"
        chunks.append({
            "id":    f"chunk_{i:03d}",
            "text":  sec,
            "title": title
        })
    return chunks

def main():
    print("Loading embedder...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    print("Chunking protocol...")
    chunks = chunk_protocol(PROTOCOL_PATH)
    print(f"   → {len(chunks)} chunks")
    for c in chunks:
        print(f"      [{c['id']}] {c['title'][:60]}")

    print("Ingesting into ChromaDB...")
    client = chromadb.PersistentClient(path=DB_PATH)

    # Drop and recreate so re-runs are idempotent
    try:
        client.delete_collection("triage_protocol")
    except Exception:
        pass
    col = client.create_collection("triage_protocol")

    texts      = [c["text"]  for c in chunks]
    ids        = [c["id"]    for c in chunks]
    metadatas  = [{"title": c["title"]} for c in chunks]
    embeddings = embedder.encode(texts, show_progress_bar=True).tolist()

    col.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas)
    print(f"Ingested {len(chunks)} chunks into ChromaDB at '{DB_PATH}'")

    # Sanity check
    result = col.query(
        query_embeddings=embedder.encode(["septic shock lactate"]).tolist(),
        n_results=2
    )
    print("\nSanity query: 'septic shock lactate'")
    for doc, meta in zip(result["documents"][0], result["metadatas"][0]):
        print(f"   ✓ {meta['title']}: {doc[:80]}...")

if __name__ == "__main__":
    main()

