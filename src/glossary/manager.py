import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

class LegalGlossaryManager:
    """
    Manages bilingual legal terminology, Latin maxims,
    statutory phrases, and procedural expressions for the legal translation pipeline.
    Supports Hindi ('hi') and Telugu ('te') seamlessly.
    """

    def __init__(self, glossary_path: Optional[str] = None, target_lang: str = "hi"):
        self.target_lang = target_lang.lower().strip()
        current_dir = Path(__file__).resolve().parent
        
        if glossary_path is None:
            filename = f"legal_terms_en_{self.target_lang}.json"
            chosen_path = current_dir.parent.parent / "data" / "glossaries" / filename
            if not chosen_path.exists():
                chosen_path = current_dir.parent.parent / "data" / "glossaries" / "legal_terms_en_hi.json"
            self.glossary_path = chosen_path
        else:
            self.glossary_path = Path(glossary_path)

        self.en_to_hi: Dict[str, str] = {}
        self.hi_to_en: Dict[str, str] = {}
        self.en_to_te: Dict[str, str] = {}
        self.te_to_en: Dict[str, str] = {}
        self.en_to_ml: Dict[str, str] = {}
        self.ml_to_en: Dict[str, str] = {}
        self.en_to_ta: Dict[str, str] = {}
        self.ta_to_en: Dict[str, str] = {}
        self.en_to_kn: Dict[str, str] = {}
        self.kn_to_en: Dict[str, str] = {}
        self.categories: Dict[str, Dict[str, str]] = {}
        self.load_glossary()

    def load_glossary(self) -> None:
        if not self.glossary_path.exists():
            raise FileNotFoundError(f"Glossary file not found at: {self.glossary_path}")

        with open(self.glossary_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.en_to_hi.clear()
        self.hi_to_en.clear()
        self.en_to_te.clear()
        self.te_to_en.clear()
        self.en_to_ml.clear()
        self.ml_to_en.clear()
        self.en_to_ta.clear()
        self.ta_to_en.clear()
        self.en_to_kn.clear()
        self.kn_to_en.clear()
        self.categories.clear()

        for category, terms in data.items():
            if category == "metadata":
                continue
            if isinstance(terms, dict):
                self.categories[category] = terms
                for en_term, target_term in terms.items():
                    k = en_term.strip().lower()
                    v = target_term.strip()
                    # Populate target-specific and general dictionaries
                    if self.target_lang == "te":
                        self.en_to_te[k] = v
                        self.te_to_en[v] = en_term.strip()
                        self.en_to_hi[k] = v
                        self.hi_to_en[v] = en_term.strip()
                    elif self.target_lang == "ml":
                        self.en_to_ml[k] = v
                        self.ml_to_en[v] = en_term.strip()
                        self.en_to_hi[k] = v
                        self.hi_to_en[v] = en_term.strip()
                    elif self.target_lang == "ta":
                        self.en_to_ta[k] = v
                        self.ta_to_en[v] = en_term.strip()
                        self.en_to_hi[k] = v
                        self.hi_to_en[v] = en_term.strip()
                    elif self.target_lang == "kn":
                        self.en_to_kn[k] = v
                        self.kn_to_en[v] = en_term.strip()
                        self.en_to_hi[k] = v
                        self.hi_to_en[v] = en_term.strip()
                    else:
                        self.en_to_hi[k] = v
                        self.hi_to_en[v] = en_term.strip()

    def get_hindi_term(self, en_term: str) -> Optional[str]:
        """Look up Hindi translation for an English legal term."""
        return self.en_to_hi.get(en_term.strip().lower())

    def get_telugu_term(self, en_term: str) -> Optional[str]:
        """Look up Telugu translation for an English legal term."""
        if self.en_to_te:
            return self.en_to_te.get(en_term.strip().lower())
        # Lazy load Telugu glossary if needed
        te_path = self.glossary_path.parent / "legal_terms_en_te.json"
        if te_path.exists():
            with open(te_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for category, terms in data.items():
                if category != "metadata" and isinstance(terms, dict):
                    for k, v in terms.items():
                        self.en_to_te[k.strip().lower()] = v.strip()
                        self.te_to_en[v.strip()] = k.strip()
            return self.en_to_te.get(en_term.strip().lower())
        return None

    def get_malayalam_term(self, en_term: str) -> Optional[str]:
        """Look up Malayalam translation for an English legal term."""
        if self.en_to_ml:
            return self.en_to_ml.get(en_term.strip().lower())
        # Lazy load Malayalam glossary if needed
        ml_path = self.glossary_path.parent / "legal_terms_en_ml.json"
        if ml_path.exists():
            with open(ml_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for category, terms in data.items():
                if category != "metadata" and isinstance(terms, dict):
                    for k, v in terms.items():
                        self.en_to_ml[k.strip().lower()] = v.strip()
                        self.ml_to_en[v.strip()] = k.strip()
            return self.en_to_ml.get(en_term.strip().lower())
        return None

    def get_tamil_term(self, en_term: str) -> Optional[str]:
        """Look up Tamil translation for an English legal term."""
        if self.en_to_ta:
            return self.en_to_ta.get(en_term.strip().lower())
        # Lazy load Tamil glossary if needed
        ta_path = self.glossary_path.parent / "legal_terms_en_ta.json"
        if ta_path.exists():
            with open(ta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for category, terms in data.items():
                if category != "metadata" and isinstance(terms, dict):
                    for k, v in terms.items():
                        self.en_to_ta[k.strip().lower()] = v.strip()
                        self.ta_to_en[v.strip()] = k.strip()
            return self.en_to_ta.get(en_term.strip().lower())
        return None

    def get_kannada_term(self, en_term: str) -> Optional[str]:
        """Look up Kannada translation for an English legal term."""
        if self.en_to_kn:
            return self.en_to_kn.get(en_term.strip().lower())
        # Lazy load Kannada glossary if needed
        kn_path = self.glossary_path.parent / "legal_terms_en_kn.json"
        if kn_path.exists():
            with open(kn_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for category, terms in data.items():
                if category != "metadata" and isinstance(terms, dict):
                    for k, v in terms.items():
                        self.en_to_kn[k.strip().lower()] = v.strip()
                        self.kn_to_en[v.strip()] = k.strip()
            return self.en_to_kn.get(en_term.strip().lower())
        return None

    def get_term(self, en_term: str) -> Optional[str]:
        """Look up target language translation for an English legal term."""
        if self.target_lang == "te":
            return self.get_telugu_term(en_term)
        elif self.target_lang == "ml":
            return self.get_malayalam_term(en_term)
        elif self.target_lang == "ta":
            return self.get_tamil_term(en_term)
        elif self.target_lang == "kn":
            return self.get_kannada_term(en_term)
        return self.get_hindi_term(en_term)

    def get_english_term(self, target_term: str) -> Optional[str]:
        """Reverse lookup English equivalent for a target language legal term."""
        clean = target_term.strip()
        if clean in self.hi_to_en:
            return self.hi_to_en[clean]
        if clean in self.te_to_en:
            return self.te_to_en[clean]
        if clean in self.ml_to_en:
            return self.ml_to_en[clean]
        if clean in self.ta_to_en:
            return self.ta_to_en[clean]
        if clean in self.kn_to_en:
            return self.kn_to_en[clean]
        return None

    def find_terms_in_text(self, text: str) -> List[Tuple[str, str, int, int]]:
        """
        Scan an English text for legal terms in the glossary.
        Returns a list of tuples: (original_en_match, canonical_hi_translation, start_pos, end_pos)
        sorted by occurrence order, longest terms first to handle compounds.
        """
        matches: List[Tuple[str, str, int, int]] = []
        # Sort terms by descending length so multi-word terms take precedence
        sorted_en_terms = sorted(self.en_to_hi.keys(), key=len, reverse=True)

        for term in sorted_en_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                original = text[m.start():m.end()]
                canonical_hi = self.en_to_hi[term]
                # Avoid overlapping matches
                overlap = any(
                    not (m.end() <= existing[2] or m.start() >= existing[3])
                    for existing in matches
                )
                if not overlap:
                    matches.append((original, canonical_hi, m.start(), m.end()))

        matches.sort(key=lambda x: x[2])
        return matches

    def check_terminology_compliance(
        self, en_text: str, hi_text: str
    ) -> Dict[str, Any]:
        """
        Verify whether expected legal terms present in en_text are appropriately
        represented in hi_text without terminology drift.
        """
        found_terms = self.find_terms_in_text(en_text)
        expected_terms = []
        compliant_terms = []
        drifted_terms = []

        for original_en, canonical_hi, _, _ in found_terms:
            expected_terms.append({"en": original_en, "expected_hi": canonical_hi})
            # Check if canonical_hi or its core root is in hi_text
            # Canonical might have alternatives separated by /
            alts = [alt.strip() for alt in canonical_hi.split("/")]
            matched = any(alt in hi_text for alt in alts)

            if matched:
                compliant_terms.append({"en": original_en, "found_hi": canonical_hi})
            else:
                drifted_terms.append({
                    "en": original_en,
                    "expected_hi": canonical_hi,
                    "status": "missing_or_drifted"
                })

        total = len(expected_terms)
        compliance_score = (len(compliant_terms) / total) if total > 0 else 1.0

        return {
            "total_terms_detected": total,
            "compliance_score": round(compliance_score, 4),
            "compliant_terms": compliant_terms,
            "drifted_terms": drifted_terms
        }

    def add_custom_term(self, en_term: str, hi_term: str, category: str = "custom") -> None:
        """Dynamically add or override a term in the active glossary."""
        en_key = en_term.strip().lower()
        hi_val = hi_term.strip()
        self.en_to_hi[en_key] = hi_val
        self.hi_to_en[hi_val] = en_term.strip()
        if category not in self.categories:
            self.categories[category] = {}
        self.categories[category][en_term.strip()] = hi_val
