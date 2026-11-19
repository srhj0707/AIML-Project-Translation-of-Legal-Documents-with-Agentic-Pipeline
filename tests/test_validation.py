import pytest
from src.validation.back_translator import LegalBackTranslator
from src.validation.metrics import LegalTranslationMetrics
from src.validation.legal_judge import LegalMeaningJudge

def test_back_translator():
    bt = LegalBackTranslator()
    hi = "तदनुसार जमानत याचिका स्वीकार की जाती है।"
    res = bt.translate_hi_to_en(hi)
    assert "Bail Application" in res["back_translation"]
    assert "allowed" in res["back_translation"].lower()

def test_metrics_evaluation():
    metrics_engine = LegalTranslationMetrics()
    orig = "The Petitioner approached the Court under Section 482 of the Code."
    back = "The Petitioner approached the Court under Section 482 of the Code."
    
    m = metrics_engine.evaluate_back_translation(orig, back)
    assert m["bleu"] > 90.0
    assert m["chrf"] > 90.0
    assert m["entity_exact_match_ratio"] == 1.0
    assert m["composite_validation_score"] > 90.0

def test_legal_judge_verdict():
    judge = LegalMeaningJudge()
    orig = "In no event shall the total liability exceed INR 25,00,000/-."
    hi = "किसी भी स्थिति में कुल दायित्व ₹25,00,000/- से अधिक नहीं होगा।"
    back = "In no event shall the total liability exceed INR 25,00,000/-."
    
    res = judge.evaluate_clause_fidelity(orig, hi, back)
    assert res["verdict"] == "PASSED"
    assert res["overall_fidelity_score"] >= 85.0
