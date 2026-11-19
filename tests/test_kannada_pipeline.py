import pytest
from src.glossary.manager import LegalGlossaryManager
from src.translation.indictrans2_engine import IndicTrans2Engine
from src.translation.nlp_engine import LegalNLPEngine
from src.translation.agentic_reviewer import AgenticReviewer
from src.validation.back_translator import LegalBackTranslator
from src.pipeline.legal_agent_orchestrator import LegalAgentOrchestrator

def test_kannada_glossary_lookup():
    """Verifies English-Kannada legal jurisprudence and statutory glossary mapping."""
    manager = LegalGlossaryManager(target_lang="kn")
    kn_term = manager.get_kannada_term("Petitioner")
    assert kn_term is not None
    assert "ಅರ್ಜಿದಾರ" in kn_term

    en_term = manager.get_english_term(kn_term)
    assert en_term in ["Petitioner", "Applicant"]

    # Test bail and notice terms
    bail_kn = manager.get_kannada_term("Bail Application")
    assert "ಜಾಮೀನು" in bail_kn or "ಅರ್ಜಿ" in bail_kn

    notice_kn = manager.get_kannada_term("Legal Notice")
    assert "ಕಾನೂನು" in notice_kn or "ನೋಟಿಸ್" in notice_kn

def test_indictrans2_engine_kannada_status():
    """Verifies IndicTrans2 Engine architecture, status telemetry, and Dravidian tags for Kannada."""
    engine = IndicTrans2Engine(auto_load=False)
    status = engine.get_status()

    assert status["engine"] == "IndicTrans2 (AI4Bharat - IIT Madras)"
    assert "kn" in status["target_dravidian_languages"]
    assert status["target_dravidian_languages"]["kn"] == "Kannada (kan_Knda)"
    assert engine.LANGUAGE_TAGS["kn"] == "kan_Knda"
    assert engine.LANGUAGE_TAGS["en"] == "eng_Latn"

def test_nlp_engine_kannada_translation():
    """Verifies translation from English to formal Kannada without English leakage."""
    nlp = LegalNLPEngine()
    en_clause = "The Bail Application is accordingly allowed."
    res = nlp.translate_en_to_kn(en_clause)

    assert "draft_translation" in res
    assert len(res["draft_translation"]) > 0
    # Must contain Kannada script characters (U+0C80 - U+0CFF)
    assert any('\u0C80' <= char <= '\u0CFF' for char in res["draft_translation"])
    # Must not leak untranslated English
    assert nlp._has_kannada_leakage(res["draft_translation"]) is False

def test_agentic_reviewer_kannada_entity_preservation():
    """Verifies Kannada entity and financial amount preservation during agent review."""
    reviewer = AgenticReviewer()
    source_en = "The Applicant furnished a bond of Rs. 1,00,000/- under Section 439."
    # Draft that omitted the financial amount
    flawed_draft_kn = "ಅರ್ಜಿದಾರರು ಕಲಂ 439 ರ ಅಡಿಯಲ್ಲಿ ಬಾಂಡ್ ಅನ್ನು ಸಲ್ಲಿಸಿದರು."

    review_res = reviewer.review_clause(
        source_en=source_en,
        draft_translation=flawed_draft_kn,
        target_lang="kn"
    )

    verified = review_res["verified_translation"]
    # Verified translation must have restored the financial amount
    assert "1,00,000" in verified or "₹" in verified or "ರೂಪಾಯಿ" in verified or "ರೂ" in verified
    assert len(review_res["audit_log"]) > 0

def test_agentic_reviewer_kannada_negation_audit():
    """Verifies strict legal negation and prohibition detection in Kannada."""
    reviewer = AgenticReviewer()
    source_en = "The Contractor shall not assign this Agreement."
    # Corrupted translation where 'shall not' was omitted
    corrupted_kn = "ಗುತ್ತಿಗೆದಾರನು ಈ ಒಪ್ಪಂದವನ್ನು ನಿಯೋಜಿಸಬಹುದು."

    review_res = reviewer.review_clause(
        source_en=source_en,
        draft_translation=corrupted_kn,
        target_lang="kn"
    )

    # Must flag critical risk or inject Kannada negation marker
    assert review_res["requires_human_review"] is True or any(
        neg in review_res["verified_translation"] for neg in ["ಮಾಡತಕ್ಕದ್ದಲ್ಲ", "ಕೂಡದು", "ಇಲ್ಲ", "ಅಲ್ಲ", "ಸಾಧ್ಯವಿಲ್ಲ", "ನಿಷೇಧಿಸಲಾಗಿದೆ", "ಅನೂರ್ಜಿತ"]
    )

def test_kannada_back_translation():
    """Verifies Kannada to English round-trip back-translation."""
    back_trans = LegalBackTranslator()
    kn_text = "ಅದರಂತೆ ಜಾಮೀನು ಅರ್ಜಿಯನ್ನು ಪುರಸ್ಕರಿಸಲಾಗಿದೆ."
    res = back_trans.translate_kn_to_en(kn_text)

    assert "back_translation" in res
    back_en = res["back_translation"].lower()
    assert "bail" in back_en
    assert "allowed" in back_en or "granted" in back_en or "application" in back_en

def test_full_kannada_orchestrator_pipeline():
    """Verifies complete end-to-end multi-stage pipeline on a Kannada legal document."""
    orch = LegalAgentOrchestrator()
    sample_doc = (
        "1. LEGAL NOTICE\n"
        "To Bengaluru Agro Enterprises, Bengaluru, Karnataka.\n"
        "Dear Sir,\n"
        "Pursuant to the instructions from my client, I hereby serve you with this Legal Notice.\n"
        "You are liable to pay the outstanding balance of Rs. 2,50,000/- along with interest.\n"
        "Failing payment within 30 days, my client shall pursue remedies before the competent court."
    )

    res = orch.process_document(sample_doc, target_lang="kn")

    assert res["target_language"] == "Kannada (ಕನ್ನಡ)"
    assert res["target_lang_code"] == "kn"
    assert "translated_document_kannada" in res
    assert len(res["clauses"]) >= 3

    # Verify Kannada script presence in reconstructed document
    full_kn = res["translated_document"]
    assert any('\u0C80' <= char <= '\u0CFF' for char in full_kn)

    # High legal fidelity and entity preservation KPIs
    summary = res["document_summary"]
    assert summary["avg_legal_fidelity_score"] >= 80.0
    assert summary["avg_entity_preservation_pct"] >= 75.0
