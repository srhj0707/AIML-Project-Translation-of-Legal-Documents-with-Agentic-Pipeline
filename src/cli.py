import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from .pipeline.legal_agent_orchestrator import LegalAgentOrchestrator
from .reporting.reporter import LegalTranslationReporter
from .translation.fine_tuning import LegalModelTrainer
from .glossary.manager import LegalGlossaryManager
from .dataset.loader import LegalDatasetLoader

def handle_translate(args):
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.")
        sys.exit(1)

    print(f"\n[1/4] Ingesting legal document from: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        doc_text = f.read()

    print("[2/4] Initializing Agentic AI + NLP Pipeline...")
    orchestrator = LegalAgentOrchestrator()

    print("[3/4] Executing Stage 1 Detection -> Stage 2 Translation & Agent Review -> Stage 3 Validation...")
    result = orchestrator.process_document(doc_text)

    summary = result["document_summary"]
    status = result["overall_status"]
    print(f"\n=======================================================")
    print(f"PIPELINE AUDIT COMPLETE: {status}")
    print(f"=======================================================")
    print(f"Total Clauses Processed:          {summary['total_clauses']}")
    print(f"Verified & Approved:             {summary['verified_clauses_count']}")
    print(f"Flagged for Human Legal Review:  {summary['flagged_clauses_count']}")
    print(f"Average Legal Fidelity Score:     {summary['avg_legal_fidelity_score']}%")
    print(f"Entity Exact Match Ratio:        {summary['avg_entity_preservation_pct']}%")
    print(f"Round-Trip Back-Translation chrF:{summary['avg_back_trans_chrf']}")
    # Set utf-8 output encoding if supported
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("[4/4] Generating audit logs and interactive reports...")
    reporter = LegalTranslationReporter()
    output_prefix = args.prefix or input_path.stem + "_audit"
    saved = reporter.save_reports(result, output_prefix=output_prefix, output_dir=args.output_dir)

    print(f"[OK] JSON Audit Log:     {saved['json_path']}")
    print(f"[OK] Markdown Summary:   {saved['markdown_path']}")
    print(f"[OK] HTML Dashboard:     {saved['html_path']}")
    print("\nTranslation complete successfully!")

def handle_evaluate_corpus(args):
    dataset_name = getattr(args, "dataset", "milpac")
    print(f"\n[+] Loading English-Hindi Parallel Legal Corpus [{dataset_name.upper()}]...")
    loader = LegalDatasetLoader(dataset_name=dataset_name)
    
    if getattr(args, "split", "test") == "test":
        splits = loader.get_splits(train_ratio=0.7, val_ratio=0.15)
        pairs = splits["test"]
        print(f"Selected Test Split: {len(pairs)} pairs from total {len(loader.get_all_pairs())} pairs.")
    else:
        pairs = loader.get_all_pairs()
        print(f"Total pairs available: {len(pairs)}")

    limit = getattr(args, "limit", None)
    if limit and limit > 0 and limit < len(pairs):
        pairs = pairs[:limit]
        print(f"Evaluating top {limit} test samples...")

    orchestrator = LegalAgentOrchestrator()
    metrics_list = []

    print("\n[+] Evaluating pipeline performance across test cases...")
    print(f"{'ID':<25} | {'Domain':<16} | {'BLEU':<6} | {'chrF':<6} | {'EMR':<6} | {'Fidelity':<8} | {'Status'}")
    print("-" * 85)

    for p in pairs:
        doc_res = orchestrator.process_document(p["en_text"])
        c = doc_res["clauses"][0]
        m = c["metrics"]
        j = c["judge_evaluation"]

        emr_pct = f"{int(m['entity_exact_match_ratio']*100)}%"
        status = "PASSED" if not c["requires_human_review"] else "FLAGGED"
        pid = p["id"][:24]

        print(f"{pid:<25} | {p['domain']:<16} | {m['bleu']:<6} | {m['chrf']:<6} | {emr_pct:<6} | {j['overall_fidelity_score']:<8} | {status}")
        metrics_list.append({
            "bleu": m["bleu"],
            "chrf": m["chrf"],
            "emr": m["entity_exact_match_ratio"],
            "fidelity": j["overall_fidelity_score"]
        })

    n = len(metrics_list)
    avg_bleu = sum(x["bleu"] for x in metrics_list) / n if n else 0
    avg_chrf = sum(x["chrf"] for x in metrics_list) / n if n else 0
    avg_emr = (sum(x["emr"] for x in metrics_list) / n * 100) if n else 0
    avg_fid = sum(x["fidelity"] for x in metrics_list) / n if n else 0

    print("-" * 85)
    print(f"AVERAGE BENCHMARKS -> BLEU: {avg_bleu:.2f} | chrF: {avg_chrf:.2f} | Entity Match: {avg_emr:.1f}% | Legal Fidelity: {avg_fid:.1f}%\n")

def handle_train(args):
    dataset_name = getattr(args, "dataset", "milpac")
    print(f"\n[+] Initializing Domain Adaptation / Fine-Tuning for: {args.base_model}")
    print(f"[+] Using Dataset: {dataset_name.upper()} (MILPaC Benchmark from Law-AI IIT KGP)")
    trainer = LegalModelTrainer(
        base_model_name=args.base_model,
        dataset_name=dataset_name,
        output_dir=args.output_dir
    )

    print("[+] Partitioning dataset into training (70%), validation (15%), and test (15%) splits...")
    result = trainer.train_or_simulate(epochs=args.epochs, learning_rate=args.lr)

    print("\n=== Training & Domain Adaptation Summary ===")
    print(f"Base Model:         {result['base_model']}")
    print(f"Dataset:            {dataset_name.upper()} ({result['dataset_info']['train_samples']} train, {result['dataset_info']['validation_samples']} val, {result['dataset_info']['test_samples']} test)")
    print(f"Epochs:             {result['hyperparameters']['epochs']}")
    print(f"Best Val Loss:      {result['best_val_loss']}")
    print("\nEpoch Progress:")
    for h in result["training_history"]:
        print(f"  Epoch {h['epoch']}: Train Loss = {h['train_loss']}, Val Loss = {h['val_loss']}, Val Legal BLEU = {h['val_legal_bleu']}")
    print(f"\nModel checkpoint and metadata saved to: {result['final_checkpoint']}")

def handle_glossary(args):
    manager = LegalGlossaryManager()
    if args.search:
        query = args.search.lower()
        print(f"\nSearching legal glossary for: '{query}'")
        found = False
        for en, hi in manager.en_to_hi.items():
            if query in en or query in hi:
                print(f"  {en.title():<35} -> {hi}")
                found = True
        if not found:
            print("  No matching legal terms found.")
    else:
        print(f"\nTotal legal terms loaded: {len(manager.en_to_hi)}")
        print("\nSample Terms:")
        for en, hi in list(manager.en_to_hi.items())[:15]:
            print(f"  {en.title():<35} -> {hi}")

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Legal Translation Agent: Agentic AI + NLP English to Hindi Translation & Validation"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # translate command
    p_trans = subparsers.add_parser("translate", help="Translate and validate a legal document")
    p_trans.add_argument("input_file", help="Path to legal document (txt)")
    p_trans.add_argument("--output-dir", default="./reports", help="Directory to save audit reports")
    p_trans.add_argument("--prefix", default=None, help="Prefix for report file names")

    # evaluate-corpus command
    p_eval = subparsers.add_parser("evaluate-corpus", help="Run benchmark evaluation over legal parallel dataset")
    p_eval.add_argument("--dataset", default="milpac", choices=["milpac", "curated", "combined"], help="Dataset to evaluate")
    p_eval.add_argument("--limit", type=int, default=15, help="Number of pairs to evaluate (0 for all)")
    p_eval.add_argument("--split", default="test", choices=["test", "all"], help="Dataset split to evaluate")

    # train command
    p_train = subparsers.add_parser("train", help="Run domain adaptation / fine-tuning on legal pairs")
    p_train.add_argument("--base-model", default="law-ai/InLegalTrans-En2Indic-1B", help="Base MT model (e.g. InLegalTrans-En2Indic-1B or IndicTrans2)")
    p_train.add_argument("--dataset", default="milpac", choices=["milpac", "curated", "combined"], help="Dataset for training")
    p_train.add_argument("--epochs", type=int, default=4, help="Number of training epochs")
    p_train.add_argument("--lr", type=float, default=3e-5, help="Learning rate")
    p_train.add_argument("--output-dir", default="./checkpoints/legal_nllb_adapted", help="Output directory")

    # glossary command
    p_gloss = subparsers.add_parser("glossary", help="Inspect or search bilingual legal terms")
    p_gloss.add_argument("--search", default=None, help="Search query")

    args = parser.parse_args()

    if args.command == "translate":
        handle_translate(args)
    elif args.command == "evaluate-corpus":
        handle_evaluate_corpus(args)
    elif args.command == "train":
        handle_train(args)
    elif args.command == "glossary":
        handle_glossary(args)

if __name__ == "__main__":
    main()
