import pytest
from src.glossary.manager import LegalGlossaryManager

def test_glossary_lookup():
    manager = LegalGlossaryManager()
    hi = manager.get_hindi_term("Petitioner")
    assert hi == "याचिकाकर्ता"
    
    en = manager.get_english_term("याचिकाकर्ता")
    assert en == "Petitioner"

def test_glossary_find_terms():
    manager = LegalGlossaryManager()
    text = "The Petitioner filed an Affidavit before the High Court."
    matches = manager.find_terms_in_text(text)
    matched_en = [m[0].lower() for m in matches]
    assert "petitioner" in matched_en
    assert "affidavit" in matched_en
    assert "high court" in matched_en

def test_glossary_compliance():
    manager = LegalGlossaryManager()
    en = "The Petitioner shall indemnify the Company."
    hi_good = "याचिकाकर्ता कंपनी की क्षतिपूर्ति करेगा।"
    hi_drift = "शिकायतकर्ता कंपनी का हर्जाना भरेगा।"
    
    comp_good = manager.check_terminology_compliance(en, hi_good)
    assert comp_good["compliance_score"] >= 0.5
    
    comp_drift = manager.check_terminology_compliance(en, hi_drift)
    assert comp_drift["compliance_score"] < comp_good["compliance_score"]
