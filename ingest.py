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
