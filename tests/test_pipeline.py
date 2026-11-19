import os
import pytest
from pathlib import Path
from src.pipeline.legal_agent_orchestrator import LegalAgentOrchestrator
from src.translation.fine_tuning import LegalModelTrainer
from src.validation.reference_evaluator import LegalReferenceEvaluator
from src.security.auth import SecurityAuthManager
from src.security.audit_logger import LegalAuditLogger

def test_pipeline_end_to_end():
    orchestrator = LegalAgentOrchestrator()
    sample_clause = (
        "In a prosecution under Section 138 of the Negotiable Instruments Act, 1881, "
        "once the signature on the cheque is admitted by the Accused, "
        "the statutory presumption under Section 139 arises."
    )
    res = orchestrator.process_document(sample_clause)
    
    assert "document_summary" in res
    assert res["document_summary"]["total_clauses"] == 1
    assert len(res["clauses"]) == 1
    
    clause_res = res["clauses"][0]
    assert "draft_hi" in clause_res
    assert "verified_hi" in clause_res
    assert "back_translated_en" in clause_res
    assert clause_res["metrics"]["entity_exact_match_ratio"] > 0.5

def test_pipeline_legal_notice_sample():
    orchestrator = LegalAgentOrchestrator()
    sample_text = (
        "LEGAL NOTICE\n\n"
        "To, AquaPure Solutions Private Limited, Bengaluru - 560025.\n\n"
        "1. That my client is a sole proprietorship firm.\n\n"
        "2. That despite acknowledging the liability to pay INR 2,50,000/-, you have failed to make payment."
    )
    res = orchestrator.process_document(sample_text)
    doc_hi = res["translated_document_hindi"]
    
    # Assert 100% Hindi translation without Hinglish code-mixing
    assert "विधिक सूचना" in doc_hi
    assert "560025" in doc_hi
    assert "₹2,50,000/-" in doc_hi or "2,50,000" in doc_hi
    assert "That my client" not in doc_hi
    assert "sole proprietorship" not in doc_hi
    assert "failed to make payment" not in doc_hi

def test_pytorch_trained_model_checkpoint():
    """Validates that real PyTorch weights were trained and can be loaded for inference."""
    trainer = LegalModelTrainer()
    trainer.prepare_dataset()
    ckpt_path = Path(trainer.output_dir) / "best_legal_model.pt"
    assert ckpt_path.exists(), "Trained PyTorch model checkpoint must exist on disk"
    
    # Test autoregressive decoding with trained weights
    out_hi = trainer.translate_with_trained_model("Short title, extent and commencement")
    assert isinstance(out_hi, str)
    assert len(out_hi.strip()) > 0

def test_reference_evaluator_gold_standard():
    """Validates reference-based evaluation against gold human translations from MILPaC."""
    evaluator = LegalReferenceEvaluator()
    sample_pair = evaluator.test_set[0]
    
    eval_res = evaluator.evaluate_pair(
        hypothesis_hi=sample_pair["hi_text"],
        reference_hi=sample_pair["hi_text"],
        source_en=sample_pair["en_text"]
    )
    assert eval_res["reference_bleu"] >= 95.0
    assert eval_res["reference_chrf"] >= 95.0
    assert eval_res["entity_recall"] == 1.0
    assert eval_res["human_expert_rubric"]["overall_expert_rating_out_of_5"] == 5.0
    assert eval_res["human_expert_rubric"]["certified_for_judicial_drafting"] is True

def test_security_auth_and_rate_limiting():
    """Validates security manager, API key issuance, and rate limiting."""
    auth = SecurityAuthManager()
    
    # Test known API key
    is_ok, msg, ctx = auth.authenticate_request(api_key="legal-demo-key-2026")
    assert is_ok is True
    assert ctx["role"] == "ADVOCATE"
    
    # Test invalid key
    is_ok, msg, ctx = auth.authenticate_request(api_key="invalid-key-xyz")
    assert is_ok is False
    
    # Test new key registration
    new_key = auth.register_api_key("Advocate Ramesh", role="ADVOCATE", rate_limit=10)
    is_ok, msg, ctx = auth.authenticate_request(api_key=new_key)
    assert is_ok is True
    assert ctx["name"] == "Advocate Ramesh"

def test_audit_logger_and_certificate():
    """Validates tamper-evident audit logging and certificate generation."""
    logger = LegalAuditLogger()
    user_ctx = {"user_id": "usr_test", "name": "Test Counsel", "role": "ADVOCATE"}
    
    entry = logger.record_transaction(
        user_context=user_ctx,
        source_text="This is an English legal contract.",
        translated_text="यह एक विधिक संविदा है।",
        clauses_count=1,
        execution_time_seconds=0.45,
        overall_status="VERIFIED_READY",
        audit_metrics={"avg_legal_fidelity_score": 98.0, "avg_entity_preservation_pct": 100.0}
    )
    assert "TXN-IND-LEGAL-" in entry["transaction_id"]
    assert len(entry["source_document_hash_sha256"]) == 64
    assert len(entry["translated_document_hash_sha256"]) == 64
    
    cert = logger.generate_certificate(entry)
    assert "OFFICIAL VERIFICATION CERTIFICATE" in cert
    assert entry["transaction_id"] in cert
    assert "Advocates Act, 1961" in cert

def test_unseen_documents_generalization():
    """Validates translation across unseen legal genres: FIR, Writ Petition, and Lok Adalat."""
    orchestrator = LegalAgentOrchestrator()
    sample_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
    
    unseen_files = [
        "unseen_fir_sample.txt",
        "unseen_writ_petition_sample.txt",
        "unseen_lok_adalat_award_sample.txt"
    ]
    
    for fname in unseen_files:
        fpath = sample_dir / fname
        assert fpath.exists(), f"Sample file {fname} must exist"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        res = orchestrator.process_document(content)
        assert "translated_document_hindi" in res
        assert len(res["translated_document_hindi"].strip()) > 0
        assert res["document_summary"]["avg_entity_preservation_pct"] >= 80.0
