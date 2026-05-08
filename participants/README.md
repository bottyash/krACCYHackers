# MediRoute — Participant Data Pack

## What's in this pack

```
participants/
├── README.md                  ← you are here
├── labs.csv                   ← lab results for all 10 patients
├── patients/
│   ├── P001.json              ← Arjun Mehta
│   ├── P002.json              ← Priya Nair
│   ├── P003.json              ← Ramesh Kulkarni
│   ├── P004.json              ← Sunita Desai
│   ├── P005.json              ← Kavya Reddy
│   ├── P006.json              ← Mohan Iyer
│   ├── P007.json              ← Fatima Sheikh
│   ├── P008.json              ← Vikram Joshi
│   ├── P009.json              ← Deepa Varma
│   └── P010.json              ← Suresh Pillai
└── protocols/
    └── triage_protocol.md     ← MediRoute Emergency Triage Protocol v2.1
```

## Your task

Build a multi-agent system that:
1. Accepts a patient JSON + their lab rows from labs.csv as input
2. Retrieves relevant triage protocol context (RAG from triage_protocol.md → ChromaDB)
3. Uses a researcher worker to consolidate patient history and lab signals
4. Uses a writer worker to produce a structured triage report
5. Assigns a final priority: **P1 (Immediate)**, **P2 (Urgent)**, **P3 (Less Urgent)**, or **P4 (Non-Urgent)**
6. Outputs a confidence score (0.0–1.0) alongside the priority

## Expected output format (per patient)

```json
{
  "patient_id": "P001",
  "priority": "P1",
  "confidence": 0.95,
  "key_signals": ["troponin_CRITICAL", "ST_elevation_ECG", "SBP_92"],
  "reasoning": "...",
  "retrieved_protocol_context": "...",
  "worker_trace": { "researcher": "...", "writer": "..." }
}
```

## Offline constraints

- No internet access during the hackathon
- Use Ollama (llama3 or mistral) for LLM calls
- Use ChromaDB local mode for vector storage
- Use `all-MiniLM-L6-v2` (pre-downloaded) for embeddings
- All packages are pre-installed in your Python environment

## Notes

- Ground-truth labels are NOT in this pack. They will be revealed at judging time.
- All patient names and records are synthetic.
- The triage_protocol.md should be chunked and ingested into ChromaDB at the start of your run.
