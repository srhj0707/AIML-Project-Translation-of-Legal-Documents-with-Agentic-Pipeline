"""
Parses the reference papers in the Downloads folder and extracts metadata:
Title, Authors, Year, Core Inferences, and Open Problems / Research Gaps.
"""

import sys
import json
from pathlib import Path
from pypdf import PdfReader

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

dl = Path("C:/Users/jsair/Downloads")

target_files = [
    "MILPaC_ A Novel Benchmark for Evaluating Translation of Legal Text to Indian Languages (1).pdf",
    "Evaluation of LLM for English to Hindi Legal Domain Machine Translation Systems (1).pdf",
    "JELLLSVol.3Issue.186-100.pdf",
    "1-s2.0-S2215039025000323-main.pdf",
    "AI Legal Translation India_ How AI-Powered Translation Is (1).pdf",
    "trans-kom_17_02_05_Giampieri_AI.20241128 (1).pdf",
    "Altakhaineh-et-al_AComparativeStudy_31032025.pdf"
]

results = []

for fname in target_files:
    fpath = dl / fname
    if not fpath.exists():
        continue
    reader = PdfReader(fpath)
    text = ""
    for p in reader.pages[:3]:
        text += (p.extract_text() or "") + "\n"
    
    first_chunk = " ".join(text.split()[:400])
    results.append({
        "filename": fname,
        "pages": len(reader.pages),
        "preview": first_chunk
    })
    print(f"File: {fname} (Pages: {len(reader.pages)})")
    print(f"Preview: {first_chunk[:300]}...\n" + "-"*60)

with open("reference_papers_summary.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
