import os
import re
from typing import Dict, List, Any, Optional
from ..detection.legal_ner import LegalEntityRecognizer
from ..glossary.manager import LegalGlossaryManager

class LegalMeaningJudge:
    """
    Legal-Meaning Fidelity Judge (LLM-as-Judge & Deterministic Legal Verifier):
    Audits translated and back-translated legal clauses across 5 core dimensions:
      1. Numerical, Financial, and Statutory Entity Precision
      2. Legal Obligation and Modality Consistency (shall / must / may)
      3. Strict Negation Preservation (no negation loss or inversion)
      4. Statutory Terminology Fidelity
      5. Clause Completeness and Omission Prevention
    """

    def __init__(self, glossary_manager: Optional[LegalGlossaryManager] = None):
        self.glossary = glossary_manager or LegalGlossaryManager()
        self.glossary_te = LegalGlossaryManager(target_lang="te")
        self.glossary_ml = LegalGlossaryManager(target_lang="ml")
        self.glossary_ta = LegalGlossaryManager(target_lang="ta")
        self.glossary_kn = LegalGlossaryManager(target_lang="kn")
        self.ner = LegalEntityRecognizer()
        self.gemini_client = None
        self._init_llm_judge()

    def _init_llm_judge(self) -> None:
        """Initializes Gemini client if GEMINI_API_KEY is available."""
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=api_key)
            except Exception:
                self.gemini_client = None

    def evaluate_clause_fidelity(
        self, original_en: str, translated_hi: str, back_translated_en: str, target_lang: str = "hi"
    ) -> Dict[str, Any]:
        """
        Evaluates legal meaning fidelity between original English, target translation,
        and back-translated English.
        """
        if self.gemini_client:
            try:
                return self._evaluate_with_gemini(original_en, translated_hi, back_translated_en)
            except Exception:
                pass

        return self._evaluate_deterministic_audit(original_en, translated_hi, back_translated_en, target_lang=target_lang)

    def _evaluate_deterministic_audit(
        self, original_en: str, translated_hi: str, back_translated_en: str, target_lang: str = "hi"
    ) -> Dict[str, Any]:
        """
        Performs rule-grounded, multi-dimensional legal meaning verification.
        """
        lang = target_lang.lower().strip()
        is_telugu = (lang == "te")
        is_malayalam = (lang == "ml")
        is_tamil = (lang == "ta")
        is_kannada = (lang == "kn")
        active_glossary = (
            self.glossary_kn if is_kannada
            else (self.glossary_ta if is_tamil
                  else (self.glossary_ml if is_malayalam
                        else (self.glossary_te if is_telugu else self.glossary)))
        )
        orig_lower = original_en.lower()
        back_lower = back_translated_en.lower()
        hi_lower = translated_hi.lower()
        violations: List[Dict[str, str]] = []

        # 1. Entity & Numerical Preservation Check
        critical_entities = self.ner.get_critical_entity_strings(original_en)
        preserved_entities = 0
        for ent in critical_entities:
            ent_lower = ent.lower()
            clean_digits = re.findall(r"\d+", ent)

            is_in_back = (ent_lower in back_lower)
            is_in_hi = (ent_lower in hi_lower)
            digits_in_back = bool(clean_digits and all(d in back_translated_en for d in clean_digits))
            digits_in_hi = bool(clean_digits and all(d in translated_hi for d in clean_digits))

            # Month checks (Hindi, Telugu, Malayalam, & Tamil)
            month_map = {
                "october": ["ಅಕ್ಟೋಬರ್", "अक्टूबर", "అక్టోబర్", "ഒക്ടോബർ", "அக்டோபர்"],
                "january": ["ಜನವರಿ", "जनवरी", "జనవరి", "ജനുവരി", "ஜனவரி"],
                "february": ["ಫೆಬ್ರವರಿ", "फरवरी", "ఫిబ్రవరి", "ഫെബ്രുവരി", "பிப்ரவரி"],
                "march": ["ಮಾರ್ಚ್", "मार्च", "మార్చి", "മാർച്ച്", "மார்ச்"],
                "april": ["ಏಪ್ರಿಲ್", "अप्रैल", "ఏప్రిల్", "ഏപ്രിൽ", "ஏப்ரல்"],
                "may": ["ಮೇ", "मई", "మే", "മെയ്", "மே"],
                "june": ["ಜೂನ್", "जून", "జూన్", "ജൂൺ", "ஜூன்"],
                "july": ["ಜುಲೈ", "जुलाई", "జూలై", "ജൂലൈ", "ஜூலை"],
                "august": ["ಆಗಸ್ಟ್", "अगस्त", "ఆగస్టు", "ആഗസ്റ്റ്", "ஆகஸ்ட்"],
                "september": ["ಸೆಪ್ಟೆಂಬರ್", "सितंबर", "సెప్టెంబర్", "സെപ്റ്റംബർ", "செப்டம்பர்"],
                "november": ["ನವೆಂಬರ್", "नवंबर", "నవంబర్", "നവംബർ", "நவம்பர்"],
                "december": ["ಡಿಸೆಂಬರ್", "दिसंबर", "డిసెంబర్", "ഡിസംബർ", "டிசம்பர்"]
            }
            month_match = any(
                (m in ent_lower and (m in back_lower or any(loc in translated_hi for loc in loc_list)))
                for m, loc_list in month_map.items()
            )

            if is_in_back or is_in_hi or digits_in_back or digits_in_hi or month_match:
                preserved_entities += 1
            else:
                violations.append({
                    "dimension": "entity_preservation",
                    "severity": "high",
                    "details": f"Critical entity '{ent}' missing or corrupted in round-trip validation"
                })

        entity_score = (preserved_entities / len(critical_entities)) * 100 if critical_entities else 100.0

        # 2. Obligation & Modality Check
        modality_score = 100.0
        orig_has_shall = "shall" in orig_lower
        orig_has_may = "may" in orig_lower and "may not" not in orig_lower
        back_has_obligation = any(m in back_lower for m in ["shall", "must", "will", "is liable", "liable to", "obliged", "call upon"])
        back_has_may = "may" in back_lower or "can" in back_lower

        if orig_has_shall and not back_has_obligation:
            modality_score -= 25.0
            violations.append({
                "dimension": "legal_modality",
                "severity": "medium",
                "details": "Mandatory obligation ('shall') degraded or altered during round-trip translation"
            })
        if orig_has_may and not back_has_may:
            modality_score -= 15.0

        modality_score = max(0.0, modality_score)

        # 3. Negation Preservation Check
        negation_score = 100.0
        neg_words = ["shall not", "must not", "may not", "no person shall", "not paid", "failed to make payment", "failed", "void"]
        orig_has_negation = any(n in orig_lower for n in neg_words)
        if is_kannada:
            negation_markers = ["ಮಾಡತಕ್ಕದ್ದಲ್ಲ", "ಕೂಡದು", "ಇಲ್ಲ", "ಅಲ್ಲ", "ಸಾಧ್ಯವಿಲ್ಲ", "ವಿಫಲ", "ಶೂನ್ಯ", "ರದ್ದು", "ನಿಷೇಧಿಸಲಾಗಿದೆ", "ಅನೂರ್ಜಿತ"]
        elif is_tamil:
            negation_markers = ["கூடாது", "இல்லை", "முடியாது", "தவறியது", "பூஜ்ஜியம்", "ரத்து", "தடைசெய்யப்பட்டுள்ளது", "செல்லாது"]
        elif is_malayalam:
            negation_markers = ["ഇല്ല", "അല്ല", "പാടില്ല", "അരുത്", "കഴിയില്ല", "പരാജയപ്പെട്ടു", "ശൂന്യം", "റദ്ദാക്കി", "വിലക്കിയിരിക്കുന്നു"]
        elif is_telugu:
            negation_markers = ["లేదు", "కాదు", "కూడదు", "రాదు", "విఫల", "నిషేధించబడినది"]
        else:
            negation_markers = ["नहीं", "न ही", "शून्य", "प्रतिषिद्ध", "विफल", "चूक", "असमर्थ"]
        hi_has_negation = any(n in translated_hi for n in negation_markers)
        back_has_negation = any(n in back_lower for n in ["not", "no", "never", "cannot", "void", "failed", "failure"])

        if orig_has_negation and (not hi_has_negation or not back_has_negation):
            negation_score = 0.0
            violations.append({
                "dimension": "negation_fidelity",
                "severity": "critical",
                "details": "CRITICAL: Negation or liability denial present in English source was lost in translation!"
            })

        # 4. Terminology Consistency
        term_check = active_glossary.check_terminology_compliance(original_en, translated_hi)
        term_score = term_check.get("compliance_score", 1.0) * 100.0
        if term_check.get("drifted_terms"):
            for drifted in term_check["drifted_terms"]:
                violations.append({
                    "dimension": "terminology_fidelity",
                    "severity": "low",
                    "details": f"Term drift: '{drifted['en']}' was not translated to expected statutory term '{drifted['expected_hi']}'"
                })

        # 5. Completeness & Word Count Ratio Check
        completeness_score = 100.0
        orig_words = len(original_en.split())
        back_words = len(back_translated_en.split())
        ratio = back_words / orig_words if orig_words > 0 else 1.0

        if ratio < 0.45:
            completeness_score = 50.0
            violations.append({
                "dimension": "completeness",
                "severity": "high",
                "details": f"Substantial omission detected: back-translation length is only {int(ratio*100)}% of source."
            })

        # Weighted Overall Legal Meaning Fidelity Score
        overall_score = (
            (entity_score * 0.35) +
            (negation_score * 0.25) +
            (modality_score * 0.15) +
            (term_score * 0.15) +
            (completeness_score * 0.10)
        )
        overall_score = round(min(100.0, max(0.0, overall_score)), 2)

        verdict = "PASSED"
        if overall_score < 70.0 or any(v["severity"] == "critical" for v in violations):
            verdict = "FAILED_CRITICAL_DISCREPANCY"
        elif overall_score < 85.0 or any(v["severity"] == "high" for v in violations):
            verdict = "WARNING_REVIEW_RECOMMENDED"

        return {
            "overall_fidelity_score": overall_score,
            "verdict": verdict,
            "dimension_scores": {
                "entity_preservation": round(entity_score, 1),
                "negation_fidelity": round(negation_score, 1),
                "modality_consistency": round(modality_score, 1),
                "terminology_fidelity": round(term_score, 1),
                "completeness": round(completeness_score, 1)
            },
            "violations": violations,
            "judge_type": "deterministic_legal_rubric"
        }

    def _evaluate_with_gemini(
        self, original_en: str, translated_hi: str, back_translated_en: str
    ) -> Dict[str, Any]:
        """Calls Gemini API as an LLM judge for legal nuance evaluation."""
        prompt = f"""
You are an expert bilingual legal jurist and translation judge specialized in Indian Law.
Evaluate the legal meaning preservation of this translation:

ORIGINAL ENGLISH:
"{original_en}"

HINDI TRANSLATION:
"{translated_hi}"

BACK-TRANSLATED ENGLISH:
"{back_translated_en}"

Analyze:
1. Did any statutory sections, case numbers, dates, or financial amounts change?
2. Are legal obligations ('shall' vs 'may') strictly preserved?
3. Are negations and prohibitions preserved?
4. Are formal legal terms used correctly?

Output your evaluation in strict JSON with fields:
overall_fidelity_score (0-100 float),
verdict (one of: PASSED, WARNING_REVIEW_RECOMMENDED, FAILED_CRITICAL_DISCREPANCY),
explanation (string).
"""
        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        import json
        text = response.text
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            data = json.loads(m.group(0))
            data["judge_type"] = "llm_as_judge_gemini"
            return data
        return self._evaluate_deterministic_audit(original_en, translated_hi, back_translated_en)
