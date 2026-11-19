import pytest
from src.glossary.manager import LegalGlossaryManager
from src.translation.indictrans2_engine import IndicTrans2Engine
from src.translation.nlp_engine import LegalNLPEngine
from src.translation.agentic_reviewer import AgenticReviewer
from src.validation.back_translator import LegalBackTranslator
from src.pipeline.legal_agent_orchestrator import LegalAgentOrchestrator

def test_tamil_glossary_lookup():
    """Verifies English-Tamil legal jurisprudence and statutory glossary mapping."""
    manager = LegalGlossaryManager(target_lang="ta")
    ta_term = manager.get_tamil_term("Petitioner")
    assert ta_term is not None
    assert "மனுதாரர்" in ta_term

    en_term = manager.get_english_term(ta_term)
    assert en_term == "Petitioner"

    # Test bail and notice terms
    bail_ta = manager.get_tamil_term("Bail Application")
    assert "பிணை" in bail_ta or "ஜாமீன்" in bail_ta

    notice_ta = manager.get_tamil_term("Legal Notice")
    assert "அறிவிப்பு" in notice_ta or "நோட்டீஸ்" in notice_ta

def test_indictrans2_engine_tamil_status():
    """Verifies IndicTrans2 Engine architecture, status telemetry, and Dravidian tags for Tamil."""
    engine = IndicTrans2Engine(auto_load=False)
    status = engine.get_status()

    assert status["engine"] == "IndicTrans2 (AI4Bharat - IIT Madras)"
    assert "ta" in status["target_dravidian_languages"]
    assert status["target_dravidian_languages"]["ta"] == "Tamil (tam_Taml)"
    assert engine.LANGUAGE_TAGS["ta"] == "tam_Taml"
    assert engine.LANGUAGE_TAGS["en"] == "eng_Latn"

def test_nlp_engine_tamil_translation():
    """Verifies translation from English to formal Tamil without English leakage."""
    nlp = LegalNLPEngine()
    en_clause = "The Bail Application is accordingly allowed."
    res = nlp.translate_en_to_ta(en_clause)

    assert "draft_translation" in res
    assert len(res["draft_translation"]) > 0
    # Must contain Tamil script characters (U+0B80 - U+0BFF)
    assert any('\u0B80' <= char <= '\u0BFF' for char in res["draft_translation"])
    # Must not leak untranslated English
    assert nlp._has_tamil_leakage(res["draft_translation"]) is False

def test_agentic_reviewer_tamil_entity_preservation():
    """Verifies Tamil entity and financial amount preservation during agent review."""
    reviewer = AgenticReviewer()
    source_en = "The Applicant furnished a bond of Rs. 1,00,000/- under Section 439."
    # Draft that omitted the financial amount
    flawed_draft_ta = "விண்ணப்பதாரர் பிரிவு 439-இன் கீழ் பத்திரத்தை தாக்கல் செய்தார்."

    review_res = reviewer.review_clause(
        source_en=source_en,
        draft_translation=flawed_draft_ta,
        target_lang="ta"
    )

    verified = review_res["verified_translation"]
    # Verified translation must have restored the financial amount
    assert "1,00,000" in verified or "₹" in verified or "ரூபாய்" in verified or "ரூ" in verified
    assert len(review_res["audit_log"]) > 0

def test_agentic_reviewer_tamil_negation_audit():
    """Verifies strict legal negation and prohibition detection in Tamil."""
    reviewer = AgenticReviewer()
    source_en = "The Contractor shall not assign this Agreement."
    # Corrupted translation where 'shall not' was omitted
    corrupted_ta = "ஒப்பந்தக்காரர் இந்த ஒப்பந்தத்தை மாற்றலாம்."

    review_res = reviewer.review_clause(
        source_en=source_en,
        draft_translation=corrupted_ta,
        target_lang="ta"
    )

    # Must flag critical risk or inject Tamil negation marker
    assert review_res["requires_human_review"] is True or any(
        neg in review_res["verified_translation"] for neg in ["கூடாது", "இல்லை", "முடியாது", "தடைசெய்யப்பட்டுள்ளது", "செல்லாது"]
    )

def test_tamil_back_translation():
    """Verifies Tamil to English round-trip back-translation."""
    back_trans = LegalBackTranslator()
    ta_text = "அதன்படி பிணை மனு அனுமதிக்கப்படுகிறது."
    res = back_trans.translate_ta_to_en(ta_text)

    assert "back_translation" in res
    back_en = res["back_translation"].lower()
    assert "bail" in back_en
    assert "allowed" in back_en or "granted" in back_en or "application" in back_en

def test_full_tamil_orchestrator_pipeline():
    """Verifies complete end-to-end multi-stage pipeline on a Tamil legal document."""
    orch = LegalAgentOrchestrator()
    sample_doc = (
        "1. LEGAL NOTICE\n"
        "To Chennai Agro Enterprises, Chennai, Tamil Nadu.\n"
        "Dear Sir,\n"
        "Pursuant to the instructions from my client, I hereby serve you with this Legal Notice.\n"
        "You are liable to pay the outstanding balance of Rs. 2,50,000/- along with interest.\n"
        "Failing payment within 30 days, my client shall pursue remedies before the competent court."
    )

    res = orch.process_document(sample_doc, target_lang="ta")

    assert res["target_language"] == "Tamil (தமிழ்)"
    assert res["target_lang_code"] == "ta"
    assert "translated_document_tamil" in res
    assert len(res["clauses"]) >= 3

    # Verify Tamil script presence in reconstructed document
    full_ta = res["translated_document"]
    assert any('\u0B80' <= char <= '\u0BFF' for char in full_ta)

    # High legal fidelity and entity preservation KPIs
    summary = res["document_summary"]
    assert summary["avg_legal_fidelity_score"] >= 80.0
    assert summary["avg_entity_preservation_pct"] >= 75.0
