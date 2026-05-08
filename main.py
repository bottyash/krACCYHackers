import os, sys, json, csv
from pathlib import Path

os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

from agent import triage_patient

PATIENTS_DIR = "../participants/patients"
LABS_CSV     = "../participants/labs.csv"
OUTPUT_FILE  = "./results.json"

PRIORITY_EMOJI = {"P1": "🔴", "P2": "🟠", "P3": "🟡", "P4": "🟢"}
