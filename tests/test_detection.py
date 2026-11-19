import pytest
from src.detection.language_detector import LegalLanguageDetector
from src.detection.legal_ner import LegalEntityRecognizer
from src.detection.clause_segmenter import LegalClauseSegmenter

def test_language_detector_english():
    detector = LegalLanguageDetector()
    res = detector.detect("The Petitioner has filed an application under Section 482 of the CrPC.")
    assert res["is_english"] is True
    assert res["is_hindi"] is False
    assert res["script"] == "Latin"

def test_language_detector_hindi():
    detector = LegalLanguageDetector()
    res = detector.detect("याचिकाकर्ता ने दंड प्रक्रिया संहिता की धारा 482 के अधीन याचिका प्रस्तुत की है।")
    assert res["is_hindi"] is True
    assert res["is_english"] is False
    assert res["script"] == "Devanagari"

def test_legal_ner_statutes_and_sections():
    ner = LegalEntityRecognizer()
    text = "In a prosecution under Section 138 of the Negotiable Instruments Act, 1881, bail was sought under Section 439."
    entities = ner.extract_entities(text)
    
    sections = [s["text"] for s in entities["sections"]]
    assert any("Section 138" in s for s in sections)
    assert any("Section 439" in s for s in sections)
    
    statutes = [st["text"] for st in entities["statutes"]]
    assert any("Negotiable Instruments Act" in st for st in statutes)

def test_legal_ner_amounts_and_dates():
    ner = LegalEntityRecognizer()
    text = "The Applicant furnished a bond of Rs. 50,000/- on 15th day of November, 2023 within thirty (30) days."
    entities = ner.extract_entities(text)
    
    amounts = [a["text"] for a in entities["monetary_amounts"]]
    assert any("50,000" in a for a in amounts)
    
    dates = [d["text"] for d in entities["dates_and_periods"]]
    assert any("November" in d for d in dates)
    assert any("thirty (30) days" in d for d in dates)

def test_clause_segmenter():
    segmenter = LegalClauseSegmenter()
    doc = """
    1. DEFINITIONS
    1.1 "Applicable Law" shall mean statutory laws in India.
    
    2. INDEMNITY
    2.1 The Contractor shall indemnify the Client against all losses.
    """
    clauses = segmenter.process_document(doc)
    assert len(clauses) >= 2
    assert any(c["clause_id"] == "C_001" for c in clauses)
    assert any(c["risk_level"] in ["elevated", "critical", "standard"] for c in clauses)
