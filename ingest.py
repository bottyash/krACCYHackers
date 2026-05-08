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
