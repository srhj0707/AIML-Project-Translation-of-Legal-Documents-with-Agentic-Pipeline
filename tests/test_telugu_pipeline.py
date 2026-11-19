import pytest
from src.glossary.manager import LegalGlossaryManager
from src.translation.indictrans2_engine import IndicTrans2Engine
from src.translation.nlp_engine import LegalNLPEngine
from src.translation.agentic_reviewer import AgenticReviewer
from src.validation.back_translator import LegalBackTranslator
from src.pipeline.legal_agent_orchestrator import LegalAgentOrchestrator

def test_telugu_glossary_lookup():
    """Verifies English-Telugu legal jurisprudence and statutory glossary mapping."""
    manager = LegalGlossaryManager(target_lang="te")
    te_term = manager.get_telugu_term("Petitioner")
    assert te_term is not None
    assert "పిటిషనర్" in te_term or "వాది" in te_term

    en_term = manager.get_english_term(te_term)
    assert en_term == "Petitioner"

    # Test bail and notice terms
    bail_te = manager.get_telugu_term("Bail Application")
    assert "బెయిల్" in bail_te

    notice_te = manager.get_telugu_term("Legal Notice")
    assert "నోటీసు" in notice_te

def test_indictrans2_engine_status():
    """Verifies IndicTrans2 Engine architecture, status telemetry, and Dravidian tags."""
    engine = IndicTrans2Engine(auto_load=False)
    status = engine.get_status()

    assert status["engine"] == "IndicTrans2 (AI4Bharat - IIT Madras)"
    assert "te" in status["target_dravidian_languages"]
    assert status["target_dravidian_languages"]["te"] == "Telugu (tel_Telu)"
    assert engine.LANGUAGE_TAGS["te"] == "tel_Telu"
    assert engine.LANGUAGE_TAGS["en"] == "eng_Latn"

def test_nlp_engine_telugu_translation():
    """Verifies translation from English to formal Telugu without English leakage."""
    nlp = LegalNLPEngine()
    en_clause = "The Bail Application is accordingly allowed."
    res = nlp.translate_en_to_te(en_clause)

    assert "draft_translation" in res
    assert len(res["draft_translation"]) > 0
    # Must contain Telugu script characters
    assert any('\u0C00' <= char <= '\u0C7F' for char in res["draft_translation"])
    # Must not leak untranslated English
    assert nlp._has_telugu_leakage(res["draft_translation"]) is False

def test_agentic_reviewer_telugu_entity_preservation():
    """Verifies Telugu entity and financial amount preservation during agent review."""
    reviewer = AgenticReviewer()
    source_en = "The Applicant furnished a bond of Rs. 1,00,000/- under Section 439."
    # Draft that omitted the financial amount
    flawed_draft_te = "దరఖాస్తుదారు సెక్షన్ 439 క్రింద పూచీకత్తు సమర్పించారు."

    review_res = reviewer.review_clause(
        source_en=source_en,
        draft_translation=flawed_draft_te,
        target_lang="te"
    )

    verified = review_res["verified_translation"]
    # Verified translation must have restored the financial amount
    assert "1,00,000" in verified or "₹" in verified or "రూ" in verified
    assert len(review_res["audit_log"]) > 0

def test_agentic_reviewer_telugu_negation_audit():
    """Verifies strict legal negation and prohibition detection in Telugu."""
    reviewer = AgenticReviewer()
    source_en = "The Contractor shall not assign this Agreement."
    # Corrupted translation where 'shall not' was omitted
    corrupted_te = "కాంట్రాక్టర్ ఈ ఒప్పందాన్ని అప్పగిస్తారు."

    review_res = reviewer.review_clause(
        source_en=source_en,
        draft_translation=corrupted_te,
        target_lang="te"
    )

    # Must flag critical risk or inject Telugu negation marker
    assert review_res["requires_human_review"] is True or any(
        neg in review_res["verified_translation"] for neg in ["చేయకూడదు", "రాదు", "లేదు", "నిషేధించబడినది"]
    )

def test_telugu_back_translation():
    """Verifies Telugu to English round-trip back-translation."""
    back_trans = LegalBackTranslator()
    te_text = "తదనుగుణంగా బెయిల్ దరఖాస్తు మంజూరు చేయబడింది."
    res = back_trans.translate_te_to_en(te_text)

    assert "back_translation" in res
    back_en = res["back_translation"].lower()
    assert "bail" in back_en
    assert "allowed" in back_en or "granted" in back_en or "application" in back_en

def test_full_telugu_orchestrator_pipeline():
    """Verifies complete end-to-end multi-stage pipeline on a Telugu legal document."""
    orch = LegalAgentOrchestrator()
    sample_doc = (
        "1. LEGAL NOTICE\n"
        "To AquaPure Solutions Private Limited, Bengaluru.\n"
        "Dear Sir,\n"
        "Pursuant to the instructions from my client, I hereby serve you with this Legal Notice.\n"
        "You are liable to pay the outstanding balance of Rs. 2,50,000/- along with interest.\n"
        "Failing payment within 30 days, my client shall pursue remedies before the competent court."
    )

    res = orch.process_document(sample_doc, target_lang="te")

    assert res["target_language"] == "Telugu (తెలుగు)"
    assert res["target_lang_code"] == "te"
    assert "translated_document_telugu" in res
    assert len(res["clauses"]) >= 3

    # Verify Telugu script presence in reconstructed document
    full_te = res["translated_document"]
    assert any('\u0C00' <= char <= '\u0C7F' for char in full_te)

    # High legal fidelity and entity preservation KPIs
    summary = res["document_summary"]
    assert summary["avg_legal_fidelity_score"] >= 80.0
    assert summary["avg_entity_preservation_pct"] >= 75.0
