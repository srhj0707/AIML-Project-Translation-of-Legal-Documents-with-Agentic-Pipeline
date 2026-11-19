"""
Comprehensive Multi-Language Pipeline Verification Script
Validates all 5 supported Indian Languages:
  1. Hindi (hi) - Indo-Aryan (Devanagari)
  2. Telugu (te) - Dravidian (Telugu Script)
  3. Malayalam (ml) - Dravidian (Malayalam Script)
  4. Tamil (ta) - Dravidian (Tamil Script)
  5. Kannada (kn) - Dravidian (Kannada Script)
"""

import sys
import time
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from src.pipeline.legal_agent_orchestrator import LegalAgentOrchestrator

TEST_DOCUMENT = (
    "IN THE HIGH COURT OF JUDICATURE\n"
    "CRIMINAL MISCELLANEOUS BAIL APPLICATION NO. 412 OF 2024\n\n"
    "1. Parties and Representation.\n"
    "The Petitioner has approached this Court under Section 439 of the Code of Criminal Procedure, 1973, "
    "seeking regular bail in connection with Crime No. 88 of 2023.\n\n"
    "2. Submissions and Financial Bond.\n"
    "The Learned Counsel for the Petitioner submits that the Applicant is ready to furnish a personal bond "
    "of Rs. 1,00,000/- with two solvent sureties of the like amount to the satisfaction of the Trial Court.\n\n"
    "3. Mandatory Negative Covenant and Restraint.\n"
    "The Applicant shall not tamper with the prosecution evidence or contact any witness directly or indirectly.\n\n"
    "4. Final Order and Disposition.\n"
    "In view of the above facts, the Bail Application is accordingly allowed on the aforesaid conditions."
)

SCRIPT_RANGES = {
    "hi": ("Devanagari", "\u0900", "\u097F"),
    "te": ("Telugu", "\u0C00", "\u0C7F"),
    "ml": ("Malayalam", "\u0D00", "\u0D7F"),
    "ta": ("Tamil", "\u0B80", "\u0BFF"),
    "kn": ("Kannada", "\u0C80", "\u0CFF")
}

def verify_script_presence(text: str, start_char: str, end_char: str) -> bool:
    return any(start_char <= char <= end_char for char in text)

def run_verification():
    print("=" * 80)
    print("NYAYATRANS AI - 5-LANGUAGE PIPELINE REVERIFICATION SUITE")
    print("=" * 80)
    print(f"Test Document: 4 Clauses, Multi-entity (Rs. 1,00,000 / Sec 439 / CrPC 1973 / Shall Not)")
    print("-" * 80)

    orchestrator = LegalAgentOrchestrator()
    results_summary = []

    languages = [
        ("hi", "Hindi (हिंदी - Devanagari)"),
        ("te", "Telugu (తెలుగు - Dravidian)"),
        ("ml", "Malayalam (മലയാളം - Dravidian)"),
        ("ta", "Tamil (தமிழ் - Dravidian)"),
        ("kn", "Kannada (ಕನ್ನಡ - Dravidian)")
    ]

    for lang_code, lang_name in languages:
        t0 = time.time()
        print(f"\n[TESTING] {lang_name} (Code: '{lang_code}')...")
        
        result = orchestrator.process_document(TEST_DOCUMENT, target_lang=lang_code)
        elapsed = round(time.time() - t0, 3)

        summary = result["document_summary"]
        translated_doc = result["translated_document"]
        script_info = SCRIPT_RANGES[lang_code]
        has_script = verify_script_presence(translated_doc, script_info[1], script_info[2])

        # Verify key entities preserved
        has_amount = "1,00,000" in translated_doc or "₹" in translated_doc
        has_section = "439" in translated_doc

        # Verify backward-compatible field
        field_name = f"translated_document_{'hindi' if lang_code == 'hi' else 'telugu' if lang_code == 'te' else 'malayalam' if lang_code == 'ml' else 'tamil' if lang_code == 'ta' else 'kannada'}"
        has_lang_field = field_name in result

        status_flag = "PASS" if (
            has_script and
            has_amount and
            has_section and
            has_lang_field and
            summary["avg_legal_fidelity_score"] >= 75.0
        ) else "FAIL"

        print(f"  -> Execution Time: {elapsed}s")
        print(f"  -> Script Verified ({script_info[0]}): {has_script}")
        print(f"  -> Key Entities Preserved (Rs 1,00,000 & Sec 439): {has_amount and has_section}")
        print(f"  -> Legal Fidelity Score: {summary['avg_legal_fidelity_score']}%")
        print(f"  -> Entity Exact Match: {summary['avg_entity_preservation_pct']}%")
        print(f"  -> Back-Trans BLEU: {summary['avg_back_trans_bleu']} | chrF: {summary['avg_back_trans_chrf']}")
        print(f"  -> Overall Status: {result['overall_status']} | Target Display: {result['target_language']}")
        print(f"  -> Result: [{status_flag}]")

        first_clause_trans = result["clauses"][0]["verified_translation"].strip()
        print(f"  -> Sample Clause Translation: \"{first_clause_trans[:70]}...\"")

        results_summary.append({
            "lang_code": lang_code,
            "lang_name": lang_name.split(" ")[0],
            "family": "Indo-Aryan" if lang_code == "hi" else "Dravidian",
            "time_s": elapsed,
            "fidelity": summary["avg_legal_fidelity_score"],
            "emr": summary["avg_entity_preservation_pct"],
            "bleu": summary["avg_back_trans_bleu"],
            "chrf": summary["avg_back_trans_chrf"],
            "status": status_flag
        })

    print("\n" + "=" * 80)
    print("FINAL 5-LANGUAGE PIPELINE PERFORMANCE MATRIX")
    print("=" * 80)
    print(f"{'Language':<12} | {'Family':<12} | {'Time (s)':<10} | {'Fidelity':<10} | {'EMR (%)':<10} | {'BLEU':<8} | {'Status':<8}")
    print("-" * 80)
    for r in results_summary:
        print(f"{r['lang_name']:<12} | {r['family']:<12} | {r['time_s']:<10.2f} | {r['fidelity']:<10.1f} | {r['emr']:<10.1f} | {r['bleu']:<8.1f} | {r['status']:<8}")
    print("=" * 80)

    all_passed = all(r["status"] == "PASS" for r in results_summary)
    if all_passed:
        print("\nALL 5 LANGUAGES VERIFIED FLAWLESSLY. PIPELINE 100% OPERATIONAL.\n")
    else:
        print("\nSOME LANGUAGES FAILED VERIFICATION.\n")
        sys.exit(1)

if __name__ == "__main__":
    run_verification()
