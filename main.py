import os, sys, json, csv
from pathlib import Path

os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

from agent import triage_patient

PATIENTS_DIR = "../participants/patients"
LABS_CSV     = "../participants/labs.csv"
OUTPUT_FILE  = "./results.json"

PRIORITY_EMOJI = {"P1": "🔴", "P2": "🟠", "P3": "🟡", "P4": "🟢"}


def load_labs() -> dict[str, list[dict]]:
    """Load labs.csv and group by patient_id."""
    labs = {}
    with open(LABS_CSV, newline="") as f:
        for row in csv.DictReader(f):
            pid = row["patient_id"]
            labs.setdefault(pid, []).append(row)
    return labs


