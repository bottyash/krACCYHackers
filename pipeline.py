import chromadb
from sentence_transformers import SentenceTransformer
from langchain_ollama import OllamaLLM
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from scorer import run_all_scores, scores_to_prompt_text


MODEL_NAME = "qwen3.5:4b"
DB_PATH    = "./chroma_db"
TOP_K      = 3

print("Loading models...")
_embedder = SentenceTransformer("all-MiniLM-L6-v2")
_llm      = OllamaLLM(model=MODEL_NAME, temperature=0.1)
_chroma   = chromadb.PersistentClient(path=DB_PATH)
_col      = _chroma.get_collection("triage_protocol")
print("Models ready\n")

class SharedState(TypedDict):
    patient:             dict
    labs:                list[dict]
    clinical_scores:     dict
    scores_text:         str
    protocol_context:    str
    researcher_summary:  str
    writer_report:       str
    final_output:        Optional[dict]


def clinical_scoring(state):
    scores = run_all_scores(state["patient"], state["labs"])
    state["clinical_scores"] = scores
    state["scores_text"]     = scores_to_prompt_text(scores)
    return state

def retrieve_protocol(state):
    p      = state["patient"]
    scores = state["clinical_scores"]
    fast_hint   = "FAST stroke" if scores["fast"]["positive"] else ""
    sepsis_hint = "septic shock" if scores["sepsis"]["score"] >= 3 else ""
    peds_hint   = "paediatric" if scores["paediatric"].get("applicable") else ""
    critical_labs = " ".join(scores["critical_labs"]["names"])
    query = f"{p['chief_complaint']} SBP {p['vitals']['bp_systolic']} HR {p['vitals']['heart_rate']} SpO2 {p['vitals']['spo2']} GCS {p['vitals']['gcs']} {fast_hint} {sepsis_hint} {peds_hint} {critical_labs}".strip()
    emb    = _embedder.encode([query]).tolist()
    result = _col.query(query_embeddings=emb, n_results=TOP_K)
    parts  = [f"[{m['title']}]\n{d}" for d, m in zip(result["documents"][0], result["metadatas"][0])]
    state["protocol_context"] = "\n\n---\n\n".join(parts)
    return state
    
def researcher_worker(state):
    p, v = state["patient"], state["patient"]["labs"]["clinical_scores"]["scores_text"]["protocol_context"]["researcher_summary"]["writer_report"]["final_output"]
    lab_lines = "\n".join(f"  {l['test']}: {l['value']} {l['unit']} [{l['flag']}]" for l in state["labs"])
    prompt = f"""You are a nurse researcher. Produce a concise clinical summary (max 200 words)."""
    
    return state
    
def writer_worker(state):
    p, v = state["patient"], state["patient"]["vitals"]
    lab_lines = "\n".join(f"  {l['test']}: {l['value']} {l['unit']} [{l['flag']}]" for l in state["labs"])
    
    prompt = f""" You are a senior physician. Assign priority using all data given. Respond in VALID JSON only"""
    return state

def fallback(state):
    
    
    return state

def build_graph():


def