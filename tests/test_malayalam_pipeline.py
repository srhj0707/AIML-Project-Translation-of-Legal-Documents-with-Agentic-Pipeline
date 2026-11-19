import pytest
from src.glossary.manager import LegalGlossaryManager
from src.translation.indictrans2_engine import IndicTrans2Engine
from src.translation.nlp_engine import LegalNLPEngine
from src.translation.agentic_reviewer import AgenticReviewer
from src.validation.back_translator import LegalBackTranslator
from src.pipeline.legal_agent_orchestrator import LegalAgentOrchestrator

def test_malayalam_glossary_lookup():
    """Verifies English-Malayalam legal jurisprudence and statutory glossary mapping."""
    manager = LegalGlossaryManager(target_lang="ml")
    ml_term = manager.get_malayalam_term("Petitioner")
    assert ml_term is not None
    assert "ഹർജിക്കാരൻ" in ml_term or "ഹർജി" in ml_term

    en_term = manager.get_english_term(ml_term)
    assert en_term == "Petitioner"

    # Test bail and notice terms
    bail_ml = manager.get_malayalam_term("Bail Application")
    assert "ജാമ്യ" in bail_ml

    notice_ml = manager.get_malayalam_term("Legal Notice")
    assert "നോട്ടീസ്" in notice_ml

def test_indictrans2_engine_malayalam_status():
    """Verifies IndicTrans2 Engine architecture, status telemetry, and Dravidian tags for Malayalam."""
    engine = IndicTrans2Engine(auto_load=False)
    status = engine.get_status()

    assert status["engine"] == "IndicTrans2 (AI4Bharat - IIT Madras)"
    assert "ml" in status["target_dravidian_languages"]
    assert status["target_dravidian_languages"]["ml"] == "Malayalam (mal_Mlym)"
    assert engine.LANGUAGE_TAGS["ml"] == "mal_Mlym"
    assert engine.LANGUAGE_TAGS["en"] == "eng_Latn"

def test_nlp_engine_malayalam_translation():
    """Verifies translation from English to formal Malayalam without English leakage."""
    nlp = LegalNLPEngine()
    en_clause = "The Bail Application is accordingly allowed."
    res = nlp.translate_en_to_ml(en_clause)

    assert "draft_translation" in res
    assert len(res["draft_translation"]) > 0
    # Must contain Malayalam script characters (U+0D00 - U+0D7F)
    assert any('\u0D00' <= char <= '\u0D7F' for char in res["draft_translation"])
    # Must not leak untranslated English
    assert nlp._has_malayalam_leakage(res["draft_translation"]) is False

def test_agentic_reviewer_malayalam_entity_preservation():
    """Verifies Malayalam entity and financial amount preservation during agent review."""
    reviewer = AgenticReviewer()
    source_en = "The Applicant furnished a bond of Rs. 1,00,000/- under Section 439."
    # Draft that omitted the financial amount
    flawed_draft_ml = "അപേക്ഷകൻ വകുപ്പ് 439 പ്രകാരം ബോണ്ട് സമർപ്പിച്ചു."

    review_res = reviewer.review_clause(
        source_en=source_en,
        draft_translation=flawed_draft_ml,
        target_lang="ml"
    )

    verified = review_res["verified_translation"]
    # Verified translation must have restored the financial amount
    assert "1,00,000" in verified or "₹" in verified or "രൂപ" in verified
    assert len(review_res["audit_log"]) > 0

def test_agentic_reviewer_malayalam_negation_audit():
    """Verifies strict legal negation and prohibition detection in Malayalam."""
    reviewer = AgenticReviewer()
    source_en = "The Contractor shall not assign this Agreement."
    # Corrupted translation where 'shall not' was omitted
    corrupted_ml = "കരാറുകാരൻ ഈ കരാർ കൈമാറുന്നതാണ്."

    review_res = reviewer.review_clause(
        source_en=source_en,
        draft_translation=corrupted_ml,
        target_lang="ml"
    )

    # Must flag critical risk or inject Malayalam negation marker
    assert review_res["requires_human_review"] is True or any(
        neg in review_res["verified_translation"] for neg in ["പാടില്ല", "അരുത്", "ഇല്ല", "വിലക്കിയിരിക്കുന്നു"]
    )

def test_malayalam_back_translation():
    """Verifies Malayalam to English round-trip back-translation."""
    back_trans = LegalBackTranslator()
    ml_text = "അതനുസരിച്ച് ജാമ്യാപേക്ഷ അനുവദിച്ചിരിക്കുന്നു."
    res = back_trans.translate_ml_to_en(ml_text)

    assert "back_translation" in res
    back_en = res["back_translation"].lower()
    assert "bail" in back_en
    assert "allowed" in back_en or "granted" in back_en or "application" in back_en

def test_full_malayalam_orchestrator_pipeline():
    """Verifies complete end-to-end multi-stage pipeline on a Malayalam legal document."""
    orch = LegalAgentOrchestrator()
    sample_doc = (
        "1. LEGAL NOTICE\n"
        "To AquaPure Solutions Private Limited, Kochi, Kerala.\n"
        "Dear Sir,\n"
        "Pursuant to the instructions from my client, I hereby serve you with this Legal Notice.\n"
        "You are liable to pay the outstanding balance of Rs. 2,50,000/- along with interest.\n"
        "Failing payment within 30 days, my client shall pursue remedies before the competent court."
    )

    res = orch.process_document(sample_doc, target_lang="ml")

    assert res["target_language"] == "Malayalam (മലയാളം)"
    assert res["target_lang_code"] == "ml"
    assert "translated_document_malayalam" in res
    assert len(res["clauses"]) >= 3

    # Verify Malayalam script presence in reconstructed document
    full_ml = res["translated_document"]
    assert any('\u0D00' <= char <= '\u0D7F' for char in full_ml)

    # High legal fidelity and entity preservation KPIs
    summary = res["document_summary"]
    assert summary["avg_legal_fidelity_score"] >= 80.0
    assert summary["avg_entity_preservation_pct"] >= 75.0
