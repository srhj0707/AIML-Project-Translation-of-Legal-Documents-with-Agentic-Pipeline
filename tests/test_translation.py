import pytest
from src.translation.nlp_engine import LegalNLPEngine
from src.translation.agentic_reviewer import AgenticReviewer

def test_nlp_engine_translation():
    engine = LegalNLPEngine()
    en = "The Bail Application is accordingly allowed."
    res = engine.translate_en_to_hi(en)
    assert "जमानत याचिका" in res["draft_translation"]
    assert "स्वीकार" in res["draft_translation"]

def test_agentic_reviewer_entity_preservation():
    reviewer = AgenticReviewer()
    source_en = "The Applicant furnished a bond of Rs. 1,00,000/- under Section 439."
    # Draft that omitted the amount
    flawed_draft_hi = "आवेदक ने धारा 439 के अधीन बंधपत्र प्रस्तुत किया।"
    
    review_res = reviewer.review_clause(source_en, flawed_draft_hi)
    # The agent should restore the missing entity
    assert "1,00,000" in review_res["verified_translation"] or "₹" in review_res["verified_translation"]
    assert len(review_res["audit_log"]) > 0

def test_agentic_reviewer_negation_audit():
    reviewer = AgenticReviewer()
    source_en = "The Contractor shall not assign this Agreement."
    # Draft that omitted 'shall not'
    corrupted_hi = "ठेकेदार इस करार का समनुदेशन करेगा।"
    
    review_res = reviewer.review_clause(source_en, corrupted_hi)
    # The agent must flag this critical legal risk or patch it
    assert review_res["requires_human_review"] is True or "नहीं" in review_res["verified_translation"]
