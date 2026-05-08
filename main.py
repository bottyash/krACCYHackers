import os, sys, json, csv
from pathlib import Path

os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

from agent import triage_patient

PATIENTS_DIR = "../participants/patients"
LABS_CSV     = "../participants/labs.csv"
OUTPUT_FILE  = "./results.json"

def load_labs() -> dict[str, list[dict]]:
    """Load labs.csv and group by patient_id."""
    labs = {}
    with open(LABS_CSV, newline="") as f:
        for row in csv.DictReader(f):
            pid = row["patient_id"]
            labs.setdefault(pid, []).append(row)
    return labs

def load_patients(patient_filter=None) -> list[dict]:
    patients = []
    for path in sorted(Path(PATIENTS_DIR).glob("*.json")):
        p = json.loads(path.read_text())
        if patient_filter and p["patient_id"] != patient_filter:
            continue
        patients.append(p)
    return patients

def print_result(r: dict):
    print(f"\n{'─'*60}")
    print(f" {r['patient_id']} → {r.get('priority','?')}  (confidence: {r.get('confidence', 0):.0%})")
    print(f"   Signals : {', '.join(r.get('key_signals', []))}")
    print(f"   Reason  : {r.get('reasoning','')[:120]}...")
    print(f"{'─'*40}")
