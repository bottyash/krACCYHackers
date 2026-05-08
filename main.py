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

def load_patients(patient_filter=None) -> list[dict]:
    patients = []
    for path in sorted(Path(PATIENTS_DIR).glob("*.json")):
        p = json.loads(path.read_text())
        if patient_filter and p["patient_id"] != patient_filter:
            continue
        patients.append(p)
    return patients

def print_result(r: dict):
    emoji = PRIORITY_EMOJI.get(r.get("priority", "?"), "⚪")
    print(f"\n{'─'*60}")
    print(f"{emoji}  {r['patient_id']} → {r.get('priority','?')}  (confidence: {r.get('confidence', 0):.0%})")
    print(f"   Signals : {', '.join(r.get('key_signals', []))}")
    print(f"   Reason  : {r.get('reasoning','')[:120]}...")
    print(f"{'─'*60}")

def main():
    patient_filter = sys.argv[1].upper() if len(sys.argv) > 1 else None

    print("=" * 60)
    print("    MediRoute — AI Triage System")
    print("=" * 60)

    labs     = load_labs()
    patients = load_patients(patient_filter)

    if not patients:
        print(f" No patient found for filter: {patient_filter}")
        sys.exit(1)

    print(f"\n Processing {len(patients)} patient(s)...\n")
    results = []

    for i, patient in enumerate(patients, 1):
        pid = patient["patient_id"]
        patient_labs = labs.get(pid, [])
        print(f"[{i}/{len(patients)}] Triaging {pid} — {patient['name']} ...")

        try:
            result = triage_patient(patient, patient_labs)
            results.append(result)
            print_result(result)
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append({
                "patient_id": pid,
                "priority": "ERROR",
                "confidence": 0.0,
                "key_signals": ["pipeline_error"],
                "reasoning": str(e),
                "retrieved_protocol_context": "",
                "worker_trace": {"researcher": "", "writer": ""}
            })

    # Save all results
    output_path = Path(OUTPUT_FILE)
    output_path.write_text(json.dumps(results, indent=2))
    print(f"\n All results saved to {OUTPUT_FILE}")

    # Summary table
    print("\n SUMMARY INFO")
    print(f"{'ID':<8} {'Name':<20} {'Priority':<10} {'Confidence'}")
    print("─" * 55)
    name_map = {p["patient_id"]: p["name"] for p in patients}
    for r in results:
        emoji = PRIORITY_EMOJI.get(r.get("priority","?"), "⚪")
        name  = name_map.get(r["patient_id"], "")
        print(f"{r['patient_id']:<8} {name:<20} {emoji} {r.get('priority','?'):<7}  {r.get('confidence',0):.0%}")

if __name__ == "__main__":
    main()


