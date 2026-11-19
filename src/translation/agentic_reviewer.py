import re
from typing import Dict, List, Any, Optional
from ..glossary.manager import LegalGlossaryManager
from ..detection.legal_ner import LegalEntityRecognizer

class AgenticReviewer:
    """
    Agentic AI Reviewer for Legal Translation.
    Reviews the NLP draft translation against source text, detected entities,
    and statutory glossary to:
      1. Prevent and rectify legal terminology drift.
      2. Enforce exact preservation of statutory citations, numbers, dates, and amounts.
      3. Verify legal modal obligations (shall vs may) and strict negations.
      4. Calculate confidence scores and flag high-risk or ambiguous clauses for human review.
      5. Completely eliminate redundant duplicate entity tags and avoid inserting raw English words.
    """

    def __init__(self, glossary_manager: Optional[LegalGlossaryManager] = None):
        self.glossary = glossary_manager or LegalGlossaryManager()
        self.glossary_te = LegalGlossaryManager(target_lang="te")
        self.glossary_ml = LegalGlossaryManager(target_lang="ml")
        self.glossary_ta = LegalGlossaryManager(target_lang="ta")
        self.glossary_kn = LegalGlossaryManager(target_lang="kn")
        self.ner = LegalEntityRecognizer()

    def review_clause(
        self,
        source_en: str,
        draft_hi: str = "",
        detected_entities: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        target_lang: str = "hi",
        draft_translation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes multi-pass agentic verification and refinement on a translated clause.
        Supports target_lang='hi' (Hindi), target_lang='te' (Telugu), target_lang='ml' (Malayalam), target_lang='ta' (Tamil), and target_lang='kn' (Kannada).
        """
        # Unify draft translation text
        current_text = draft_translation if draft_translation is not None else draft_hi
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

        if not detected_entities:
            detected_entities = self.ner.extract_entities(source_en)

        current_trans = current_text
        audit_log: List[Dict[str, Any]] = []
        human_review_flags: List[str] = []

        # --- Pass 1: Entity Preservation Verification & Restoration ---
        entity_repairs = []
        critical_entities = self.ner.get_critical_entity_strings(source_en)

        for ent in critical_entities:
            if is_kannada:
                found = self._is_entity_present_in_kannada(ent, current_trans)
            elif is_tamil:
                found = self._is_entity_present_in_tamil(ent, current_trans)
            elif is_malayalam:
                found = self._is_entity_present_in_malayalam(ent, current_trans)
            elif is_telugu:
                found = self._is_entity_present_in_telugu(ent, current_trans)
            else:
                found = self._is_entity_present_in_hindi(ent, current_trans)

            if not found:
                # Entity is completely missing from translation! Attempt safe restoration
                if is_kannada:
                    localized_variants = self._generate_entity_variants_kn(ent)
                elif is_tamil:
                    localized_variants = self._generate_entity_variants_ta(ent)
                elif is_malayalam:
                    localized_variants = self._generate_entity_variants_ml(ent)
                elif is_telugu:
                    localized_variants = self._generate_entity_variants_te(ent)
                else:
                    localized_variants = self._generate_entity_variants(ent)
                best_variant = localized_variants[0]
                
                # Check whether inserting is safe and not duplicate
                if is_kannada:
                    current_trans, inserted = self._safe_insert_entity_kn(current_trans, ent, best_variant)
                elif is_tamil:
                    current_trans, inserted = self._safe_insert_entity_ta(current_trans, ent, best_variant)
                elif is_malayalam:
                    current_trans, inserted = self._safe_insert_entity_ml(current_trans, ent, best_variant)
                elif is_telugu:
                    current_trans, inserted = self._safe_insert_entity_te(current_trans, ent, best_variant)
                else:
                    current_trans, inserted = self._safe_insert_entity(current_trans, ent, best_variant)

                if inserted:
                    entity_repairs.append({
                        "original_entity": ent,
                        "restored_as": best_variant,
                        "reason": "Entity was missing in NLP draft"
                    })
                    audit_log.append({
                        "action": "RESTORE_ENTITY",
                        "details": f"Restored missing critical entity '{best_variant}' into translation"
                    })

        # --- Pass 2: Terminology Compliance & Drift Rectification ---
        term_check = active_glossary.check_terminology_compliance(source_en, current_trans)
        terminology_repairs = []

        for drifted in term_check.get("drifted_terms", []):
            en_term = drifted["en"]
            canonical_tgt = drifted["expected_hi"].split("/")[0].strip()

            if is_kannada:
                current_trans, substituted = self._fix_term_drift_kn(current_trans, en_term, canonical_tgt)
            elif is_tamil:
                current_trans, substituted = self._fix_term_drift_ta(current_trans, en_term, canonical_tgt)
            elif is_malayalam:
                current_trans, substituted = self._fix_term_drift_ml(current_trans, en_term, canonical_tgt)
            elif is_telugu:
                current_trans, substituted = self._fix_term_drift_te(current_trans, en_term, canonical_tgt)
            else:
                current_trans, substituted = self._fix_term_drift(current_trans, en_term, canonical_tgt)

            if substituted:
                terminology_repairs.append({
                    "term_en": en_term,
                    "enforced_target": canonical_tgt
                })
                audit_log.append({
                    "action": "ENFORCE_LEGAL_TERM",
                    "details": f"Replaced informal phrasing with canonical legal term '{canonical_tgt}' for '{en_term}'"
                })

        # --- Pass 3: Modality and Negation Safety Audit ---
        if is_kannada:
            modality_issues = self._verify_modality_and_negation_kn(source_en, current_trans)
        elif is_tamil:
            modality_issues = self._verify_modality_and_negation_ta(source_en, current_trans)
        elif is_malayalam:
            modality_issues = self._verify_modality_and_negation_ml(source_en, current_trans)
        elif is_telugu:
            modality_issues = self._verify_modality_and_negation_te(source_en, current_trans)
        else:
            modality_issues = self._verify_modality_and_negation(source_en, current_trans)

        for issue in modality_issues:
            if issue["severity"] == "critical":
                human_review_flags.append(issue["message"])
                audit_log.append({
                    "action": "FLAG_CRITICAL_LEGAL_RISK",
                    "details": issue["message"]
                })
                if "negation_missing" in issue["code"]:
                    if is_kannada:
                        current_trans = self._patch_missing_negation_kn(current_trans)
                    elif is_tamil:
                        current_trans = self._patch_missing_negation_ta(current_trans)
                    elif is_malayalam:
                        current_trans = self._patch_missing_negation_ml(current_trans)
                    elif is_telugu:
                        current_trans = self._patch_missing_negation_te(current_trans)
                    else:
                        current_trans = self._patch_missing_negation(current_trans)

        # --- Pass 4: Confidence Scoring ---
        total_critical = len(critical_entities)
        missing_count = 0
        for ent in critical_entities:
            if is_kannada:
                present = self._is_entity_present_in_kannada(ent, current_trans)
            elif is_tamil:
                present = self._is_entity_present_in_tamil(ent, current_trans)
            elif is_malayalam:
                present = self._is_entity_present_in_malayalam(ent, current_trans)
            elif is_telugu:
                present = self._is_entity_present_in_telugu(ent, current_trans)
            else:
                present = self._is_entity_present_in_hindi(ent, current_trans)
            if not present:
                missing_count += 1

        entity_preservation_score = 1.0 if total_critical == 0 else max(
            0.0, 1.0 - (missing_count / total_critical)
        )

        term_score = term_check.get("compliance_score", 1.0)
        has_critical_flags = any("CRITICAL" in f for f in human_review_flags)

        confidence = (entity_preservation_score * 0.45) + (term_score * 0.35) + (0.20 if not has_critical_flags else 0.05)
        confidence = round(min(1.0, max(0.1, confidence)), 4)

        if confidence < 0.80 and not human_review_flags:
            human_review_flags.append(f"Low translation confidence ({int(confidence * 100)}%) - legal verification recommended.")

        requires_human_review = len(human_review_flags) > 0

        return {
            "verified_translation": current_trans.strip(),
            "confidence_score": confidence,
            "requires_human_review": requires_human_review,
            "human_review_flags": human_review_flags,
            "audit_log": audit_log,
            "entity_preservation_score": round(entity_preservation_score, 4),
            "terminology_score": round(term_score, 4),
            "entity_repairs_count": len(entity_repairs),
            "terminology_repairs_count": len(terminology_repairs),
            "target_language": target_lang
        }

    def _is_entity_present_in_hindi(self, ent: str, hi_text: str) -> bool:
        """
        Robustly determines whether an entity (number, date, section, pin code, or currency)
        is genuinely present in the Hindi translation.
        """
        ent_lower = ent.lower().strip()

        # 1. Word amounts: "Rupees Two Lakh..." -> in Hindi "रुपये", "लाख", "हजार"
        if ent_lower.startswith(("rupees", "indian rupees")):
            return any(w in hi_text for w in ["रुपये", "रुपए", "लाख", "हजार", "करोड़", "₹"])

        # 2. Direct variants match
        variants = self._generate_entity_variants(ent)
        if any(var in hi_text for var in variants):
            return True

        # 3. Formatted numbers with commas (e.g. 2,50,000 or 30,000 or 2,80,000)
        formatted_nums = re.findall(r"\b\d{1,3}(?:,\d{2,3})*(?:\.\d+)?\b", ent)
        for fn in formatted_nums:
            if fn in hi_text:
                return True

        # 4. Check raw digit sequences
        raw_digits = re.findall(r"\d+", ent)
        if raw_digits:
            if all(d in hi_text for d in raw_digits):
                return True
            combined = "".join(raw_digits)
            hi_digits = "".join(re.findall(r"\d+", hi_text))
            if len(combined) >= 3 and combined in hi_digits:
                return True

        # 5. Dates check
        months_en_to_hi = {
            "january": "जनवरी", "february": "फरवरी", "march": "मार्च",
            "april": "अप्रैल", "may": "मई", "june": "जून",
            "july": "जुलाई", "august": "अगस्त", "september": "सितंबर",
            "october": "अक्टूबर", "november": "नवंबर", "december": "दिसंबर"
        }
        for m_en, m_hi in months_en_to_hi.items():
            if m_en in ent_lower and m_hi in hi_text:
                years = re.findall(r"\b(19\d\d|20\d\d)\b", ent)
                if not years or any(y in hi_text for y in years):
                    return True

        # 6. Percentage check
        if "%" in ent:
            pct_num = re.sub(r"[^\d.]", "", ent)
            if f"{pct_num}%" in hi_text or f"{pct_num} %" in hi_text or f"{pct_num} प्रतिशत" in hi_text:
                return True

        return False

    def _generate_entity_variants(self, ent: str) -> List[str]:
        """Generates possible representations of an entity in Hindi legal text."""
        variants = [ent]
        # Section variations
        sec_m = re.match(r"Sections?\s+(\d+[A-Z]?)", ent, re.IGNORECASE)
        if sec_m:
            num = sec_m.group(1)
            variants.extend([f"धारा {num}", f"धारा {num} के", f"धाराएं {num}"])

        art_m = re.match(r"Articles?\s+(\d+[A-Z]?)", ent, re.IGNORECASE)
        if art_m:
            num = art_m.group(1)
            variants.extend([f"अनुच्छेद {num}", f"अनुच्छेद {num} के"])

        # Currency variations
        if any(c in ent for c in ["INR", "Rs", "₹"]):
            num_clean = re.sub(r"[^\d,.]", "", ent)
            variants.extend([
                f"₹{num_clean}", f"₹ {num_clean}",
                f"{num_clean} /- रुपये", f"{num_clean}/- रुपये",
                f"{num_clean} रुपये", f"रुपये {num_clean}",
                f"₹{num_clean}/-", f"₹ {num_clean}/-"
            ])

        # Date variations
        months = [
            ("January", "जनवरी"), ("February", "फरवरी"), ("March", "मार्च"),
            ("April", "अप्रैल"), ("May", "मई"), ("June", "जून"),
            ("July", "जुलाई"), ("August", "अगस्त"), ("September", "सितंबर"),
            ("October", "अक्टूबर"), ("November", "नवंबर"), ("December", "दिसंबर")
        ]
        for en_m, hi_m in months:
            if en_m.lower() in ent.lower():
                variants.append(re.sub(en_m, hi_m, ent, flags=re.IGNORECASE))

        return variants

    def _safe_insert_entity(self, hi_text: str, original_ent: str, best_variant: str) -> (str, bool):
        """
        Safely restores a truly missing entity into the Hindi text without duplicate injection.
        """
        # Never insert written English word amounts
        if original_ent.lower().startswith(("rupees", "indian rupees")):
            return hi_text, False

        # If any numeric digit sequence from original_ent is already in hi_text, DO NOT insert!
        digits = re.findall(r"\d+", original_ent)
        if digits and any(len(d) >= 2 and d in hi_text for d in digits):
            return hi_text, False

        # If month or date components are already in hi_text
        if any(m in hi_text for m in ["जनवरी", "फरवरी", "मार्च", "अप्रैल", "मई", "जून", "जुलाई", "अगस्त", "सितंबर", "अक्टूबर", "नवंबर", "दिसंबर"]):
            if digits and all(d in hi_text for d in digits):
                return hi_text, False

        # If best_variant is already in text, do not duplicate
        if best_variant in hi_text:
            return hi_text, False

        # Localize variant before inserting so we never insert English
        localized = best_variant
        localized = re.sub(r"\bINR\s*", "₹", localized, flags=re.IGNORECASE)
        localized = re.sub(r"\bRs\.?\s*", "₹", localized, flags=re.IGNORECASE)
        localized = re.sub(r"\bSection\s+", "धारा ", localized, flags=re.IGNORECASE)

        return f"{hi_text} ({localized})", True

    def _fix_term_drift(self, hi_text: str, en_term: str, canonical_hi: str) -> (str, bool):
        """Attempts to replace informal equivalents with the canonical term."""
        informal_mappings = {
            "Petitioner": ["प्रार्थी", "याची", "वादी"],
            "Respondent": ["विपक्षी", "उत्तरदाता"],
            "Affidavit": ["हलफनामा"],
            "Quash": ["रद्द करना"],
            "Writ Petition": ["रिट अर्जी"],
            "Indemnity": ["हर्जाना"],
            "Notice": ["सूचना"],
            "Legal Notice": ["कानूनी नोटिस"]
        }

        if en_term in informal_mappings:
            for inf in informal_mappings[en_term]:
                if inf in hi_text and canonical_hi not in hi_text:
                    new_text = hi_text.replace(inf, canonical_hi)
                    return new_text, True
        return hi_text, False

    def _verify_modality_and_negation(self, source_en: str, target_hi: str) -> List[Dict[str, Any]]:
        """Audits modal obligation and strict negation consistency."""
        issues = []
        source_lower = source_en.lower()

        # Strict negations
        has_en_negation = any(neg in source_lower for neg in [
            "shall not", "must not", "may not", "no person shall", "in no event shall", "cannot", "void ab initio"
        ])

        has_hi_negation = any(neg in target_hi for neg in [
            "नहीं", "न ही", "शून्य", "प्रतिषिद्ध", "वर्जित", "इनकार"
        ])

        if has_en_negation and not has_hi_negation:
            issues.append({
                "severity": "critical",
                "code": "negation_missing",
                "message": "CRITICAL: English source contains strict legal negation/prohibition, but no negation was detected in Hindi translation!"
            })

        # Modal 'shall' vs permissive 'may'
        if "shall not" not in source_lower and "shall" in source_lower:
            # Source imposes mandatory obligation
            if "सकता है" in target_hi and not any(m in target_hi for m in ["होगा", "करेगा", "बाध्य", "अनिवार्य", "मानेंगे"]):
                issues.append({
                    "severity": "warning",
                    "code": "modality_weakened",
                    "message": "Warning: Mandatory obligation ('shall') appears to have been translated permissively ('सकता है')."
                })

        return issues

    def _patch_missing_negation(self, hi_text: str) -> str:
        """Injects negation marker when critical negation was omitted."""
        if "करेगा" in hi_text:
            return hi_text.replace("करेगा", "नहीं करेगा")
        elif "होगा" in hi_text:
            return hi_text.replace("होगा", "नहीं होगा")
        else:
            return f"{hi_text} (प्रतिषिद्ध होगा)"

    # ================= TELUGU (DRAVIDIAN) VERIFICATION HELPERS =================

    def _is_entity_present_in_telugu(self, ent: str, te_text: str) -> bool:
        """Determines whether an entity is genuinely present in the Telugu translation."""
        ent_lower = ent.lower().strip()

        # 1. Word amounts: "Rupees Two Lakh..." -> in Telugu "రూపాయలు", "లక్షలు", "వేలు", "₹"
        if ent_lower.startswith(("rupees", "indian rupees")):
            return any(w in te_text for w in ["రూపాయలు", "రూపాయి", "లక్షలు", "లక్షల", "వేలు", "వేల", "కోట్లు", "₹", "రూ."])

        # 2. Direct variants match
        variants = self._generate_entity_variants_te(ent)
        if any(var in te_text for var in variants):
            return True

        # 3. Formatted numbers with commas (e.g. 2,50,000 or 30,000)
        formatted_nums = re.findall(r"\b\d{1,3}(?:,\d{2,3})*(?:\.\d+)?\b", ent)
        for fn in formatted_nums:
            if fn in te_text:
                return True

        # 4. Check raw digit sequences
        raw_digits = re.findall(r"\d+", ent)
        if raw_digits:
            if all(d in te_text for d in raw_digits):
                return True
            combined = "".join(raw_digits)
            te_digits = "".join(re.findall(r"\d+", te_text))
            if len(combined) >= 3 and combined in te_digits:
                return True

        # 5. Telugu Dates check
        months_en_to_te = {
            "january": "జనవరి", "february": "ఫిబ్రవరి", "march": "మార్చి",
            "april": "ఏప్రిల్", "may": "మే", "june": "జూన్",
            "july": "జూలై", "august": "ఆగస్టు", "september": "సెప్టెంబర్",
            "october": "అక్టోబర్", "november": "నవంబర్", "december": "డిసెంబర్"
        }
        for m_en, m_te in months_en_to_te.items():
            if m_en in ent_lower and m_te in te_text:
                years = re.findall(r"\b(19\d\d|20\d\d)\b", ent)
                if not years or any(y in te_text for y in years):
                    return True

        # 6. Percentage check
        if "%" in ent:
            pct_num = re.sub(r"[^\d.]", "", ent)
            if f"{pct_num}%" in te_text or f"{pct_num} %" in te_text or f"{pct_num} శాతం" in te_text:
                return True

        return False

    def _generate_entity_variants_te(self, ent: str) -> List[str]:
        """Generates possible representations of an entity in Telugu legal text."""
        variants = [ent]
        # Section variations
        sec_m = re.match(r"Sections?\s+(\d+[A-Z]?)", ent, re.IGNORECASE)
        if sec_m:
            num = sec_m.group(1)
            variants.extend([f"సెక్షన్ {num}", f"సెక్షన్ {num} క్రింద", f"సెక్షన్లు {num}"])

        art_m = re.match(r"Articles?\s+(\d+[A-Z]?)", ent, re.IGNORECASE)
        if art_m:
            num = art_m.group(1)
            variants.extend([f"ఆర్టికల్ {num}", f"ఆర్టికల్ {num} క్రింద"])

        # Currency variations
        if any(c in ent for c in ["INR", "Rs", "₹"]):
            num_clean = re.sub(r"[^\d,.]", "", ent)
            variants.extend([
                f"₹{num_clean}", f"₹ {num_clean}",
                f"{num_clean}/- రూపాయలు", f"రూ. {num_clean}",
                f"రూ.{num_clean}", f"{num_clean} రూపాయలు",
                f"₹{num_clean}/-", f"₹ {num_clean}/-"
            ])

        # Date variations
        months = [
            ("January", "జనవరి"), ("February", "ఫిబ్రవరి"), ("March", "మార్చి"),
            ("April", "ఏప్రిల్"), ("May", "మే"), ("June", "జూన్"),
            ("July", "జూలై"), ("August", "ఆగస్టు"), ("September", "సెప్టెంబర్"),
            ("October", "అక్టోబర్"), ("November", "నవంబర్"), ("December", "డిసెంబర్")
        ]
        for en_m, te_m in months:
            if en_m.lower() in ent.lower():
                variants.append(re.sub(en_m, te_m, ent, flags=re.IGNORECASE))

        return variants

    def _safe_insert_entity_te(self, te_text: str, original_ent: str, best_variant: str) -> (str, bool):
        """Safely restores a truly missing entity into Telugu text without duplicate injection."""
        if original_ent.lower().startswith(("rupees", "indian rupees")):
            return te_text, False

        digits = re.findall(r"\d+", original_ent)
        if digits and any(len(d) >= 2 and d in te_text for d in digits):
            return te_text, False

        if any(m in te_text for m in ["జనవరి", "ఫిబ్రవరి", "మార్చి", "ఏప్రిల్", "మే", "జూన్", "జూలై", "ఆగస్టు", "సెప్టెంబర్", "అక్టోబర్", "నవంబర్", "డిసెంబర్"]):
            if digits and all(d in te_text for d in digits):
                return te_text, False

        if best_variant in te_text:
            return te_text, False

        localized = best_variant
        localized = re.sub(r"\bINR\s*", "₹", localized, flags=re.IGNORECASE)
        localized = re.sub(r"\bRs\.?\s*", "₹", localized, flags=re.IGNORECASE)
        localized = re.sub(r"\bSection\s+", "సెక్షన్ ", localized, flags=re.IGNORECASE)

        return f"{te_text} ({localized})", True

    def _fix_term_drift_te(self, te_text: str, en_term: str, canonical_te: str) -> (str, bool):
        """Attempts to replace informal Telugu equivalents with the canonical term."""
        informal_mappings = {
            "Petitioner": ["పిటిషన్ దారు", "ఫిర్యాదుదారుడు"],
            "Respondent": ["ఎదుటి పక్షం", "రెస్పాండెంట్"],
            "Affidavit": ["ప్రమాణపత్రం", "అఫిడవిట్ పత్రం"],
            "Quash": ["కొట్టివేయుట", "రద్దు చేయుట"],
            "Notice": ["సమాచారం", "నోటీస్"],
            "Legal Notice": ["లీగల్ నోటీసు", "చట్టపరమైన సమాచారం"]
        }

        if en_term in informal_mappings:
            for inf in informal_mappings[en_term]:
                if inf in te_text and canonical_te not in te_text:
                    new_text = te_text.replace(inf, canonical_te)
                    return new_text, True
        return te_text, False

    def _verify_modality_and_negation_te(self, source_en: str, target_te: str) -> List[Dict[str, Any]]:
        """Audits modal obligation and strict negation consistency in Telugu."""
        issues = []
        source_lower = source_en.lower()

        # Strict negations in Telugu
        has_en_negation = any(neg in source_lower for neg in [
            "shall not", "must not", "may not", "no person shall", "in no event shall", "cannot", "void ab initio"
        ])

        has_te_negation = any(neg in target_te for neg in [
            "లేదు", "కాదు", "కూడదు", "రాదు", "చేయరాదు", "చేయకూడదు", "నిషేధించబడినది", "రద్దు", "చెల్లదు"
        ])

        if has_en_negation and not has_te_negation:
            issues.append({
                "severity": "critical",
                "code": "negation_missing_te",
                "message": "CRITICAL: English source contains strict legal negation/prohibition, but no negation was detected in Telugu translation!"
            })

        # Mandatory 'shall' vs permissive 'may' in Telugu
        if "shall not" not in source_lower and "shall" in source_lower:
            if "వచ్చు" in target_te and not any(m in target_te for m in ["వలెను", "చేయాలి", "ఉండాలి", "బాధ్యత", "తప్పనిసరి"]):
                issues.append({
                    "severity": "warning",
                    "code": "modality_weakened_te",
                    "message": "Warning: Mandatory obligation ('shall') appears to have been translated permissively in Telugu ('వచ్చు')."
                })

        return issues

    def _patch_missing_negation_te(self, te_text: str) -> str:
        """Injects negation marker into Telugu when critical negation was omitted."""
        if "చేయవలెను" in te_text:
            return te_text.replace("చేయవలెను", "చేయకూడదు")
        elif "ఉండవలెను" in te_text:
            return te_text.replace("ఉండవలెను", "ఉండరాదు")
        else:
            return f"{te_text} (నిషేధించబడినది)"

    # ================= MALAYALAM (DRAVIDIAN) VERIFICATION HELPERS =================

    def _is_entity_present_in_malayalam(self, ent: str, ml_text: str) -> bool:
        """Determines whether an entity is genuinely present in the Malayalam translation."""
        ent_lower = ent.lower().strip()

        # 1. Word amounts: "Rupees Two Lakh..." -> in Malayalam "രൂപ", "ലക്ഷം", "കോടി", "₹"
        if ent_lower.startswith(("rupees", "indian rupees")):
            return any(w in ml_text for w in ["രൂപ", "ലക്ഷം", "ലക്ഷങ്ങൾ", "ആയിരം", "കോടി", "₹", "രൂ."])

        # 2. Direct variants match
        variants = self._generate_entity_variants_ml(ent)
        if any(var in ml_text for var in variants):
            return True

        # 3. Formatted numbers with commas (e.g. 2,50,000 or 30,000)
        formatted_nums = re.findall(r"\b\d{1,3}(?:,\d{2,3})*(?:\.\d+)?\b", ent)
        for fn in formatted_nums:
            if fn in ml_text:
                return True

        # 4. Check raw digit sequences
        raw_digits = re.findall(r"\d+", ent)
        if raw_digits:
            if all(d in ml_text for d in raw_digits):
                return True
            combined = "".join(raw_digits)
            ml_digits = "".join(re.findall(r"\d+", ml_text))
            if len(combined) >= 3 and combined in ml_digits:
                return True

        # 5. Malayalam Dates check
        months_en_to_ml = {
            "january": "ജനുവരി", "february": "ഫെബ്രുവരി", "march": "മാർച്ച്",
            "april": "ഏപ്രിൽ", "may": "മെയ്", "june": "ജൂൺ",
            "july": "ജൂലൈ", "august": "ആഗസ്റ്റ്", "september": "സെപ്റ്റംബർ",
            "october": "ഒക്ടോബർ", "november": "നവംബർ", "december": "ഡിസംബർ"
        }
        for m_en, m_ml in months_en_to_ml.items():
            if m_en in ent_lower and m_ml in ml_text:
                years = re.findall(r"\b(19\d\d|20\d\d)\b", ent)
                if not years or any(y in ml_text for y in years):
                    return True

        # 6. Percentage check
        if "%" in ent:
            pct_num = re.sub(r"[^\d.]", "", ent)
            if f"{pct_num}%" in ml_text or f"{pct_num} %" in ml_text or f"{pct_num} ശതമാനം" in ml_text:
                return True

        return False

    def _generate_entity_variants_ml(self, ent: str) -> List[str]:
        """Generates possible representations of an entity in Malayalam legal text."""
        variants = [ent]
        # Section variations
        sec_m = re.match(r"Sections?\s+(\d+[A-Z]?)", ent, re.IGNORECASE)
        if sec_m:
            num = sec_m.group(1)
            variants.extend([f"വകുപ്പ് {num}", f"വകുപ്പ് {num} പ്രകാരം", f"വകുപ്പുകൾ {num}"])

        art_m = re.match(r"Articles?\s+(\d+[A-Z]?)", ent, re.IGNORECASE)
        if art_m:
            num = art_m.group(1)
            variants.extend([f"അനുച്ഛേദം {num}", f"അനുച്ഛേദം {num} പ്രകാരം"])

        # Currency variations
        if any(c in ent for c in ["INR", "Rs", "₹"]):
            num_clean = re.sub(r"[^\d,.]", "", ent)
            variants.extend([
                f"₹{num_clean}", f"₹ {num_clean}",
                f"{num_clean}/- രൂപ", f"രൂ. {num_clean}",
                f"രൂ.{num_clean}", f"{num_clean} രൂപ",
                f"₹{num_clean}/-", f"₹ {num_clean}/-"
            ])

        # Date variations
        months = [
            ("January", "ജനുവരി"), ("February", "ഫെബ്രുവരി"), ("March", "മാർച്ച്"),
            ("April", "ഏപ്രിൽ"), ("May", "മെയ്"), ("June", "ജൂൺ"),
            ("July", "ജൂലൈ"), ("August", "ആഗസ്റ്റ്"), ("September", "സെപ്റ്റംബർ"),
            ("October", "ഒക്ടോബർ"), ("November", "നവംബർ"), ("December", "ഡിസംബർ")
        ]
        for en_m, ml_m in months:
            if en_m.lower() in ent.lower():
                variants.append(re.sub(en_m, ml_m, ent, flags=re.IGNORECASE))

        return variants

    def _safe_insert_entity_ml(self, ml_text: str, original_ent: str, best_variant: str) -> (str, bool):
        """Safely restores a truly missing entity into Malayalam text without duplicate injection."""
        if original_ent.lower().startswith(("rupees", "indian rupees")):
            return ml_text, False

        digits = re.findall(r"\d+", original_ent)
        if digits and any(len(d) >= 2 and d in ml_text for d in digits):
            return ml_text, False

        if any(m in ml_text for m in ["ജനുവരി", "ഫെബ്രുവരി", "മാർച്ച്", "ഏപ്രിൽ", "മെയ്", "ജൂൺ", "ജൂലൈ", "ആഗസ്റ്റ്", "സെപ്റ്റംബർ", "ഒക്ടോബർ", "നവംബർ", "ഡിസംബർ"]):
            if digits and all(d in ml_text for d in digits):
                return ml_text, False

        if best_variant in ml_text:
            return ml_text, False

        localized = best_variant
        localized = re.sub(r"\bINR\s*", "₹", localized, flags=re.IGNORECASE)
        localized = re.sub(r"\bRs\.?\s*", "₹", localized, flags=re.IGNORECASE)
        localized = re.sub(r"\bSection\s+", "വകുപ്പ് ", localized, flags=re.IGNORECASE)

        return f"{ml_text} ({localized})", True

    def _fix_term_drift_ml(self, ml_text: str, en_term: str, canonical_ml: str) -> (str, bool):
        """Attempts to replace informal Malayalam equivalents with the canonical term."""
        informal_mappings = {
            "Petitioner": ["ഹർജിക്കക്ഷി", "പരാതിക്കാരൻ"],
            "Respondent": ["എതിർകക്ഷി", "മറുപടി നൽകുന്നയാൾ"],
            "Affidavit": ["സത്യപ്രസ്താവന", "അഫിഡവിറ്റ്"],
            "Quash": ["റദ്ദാക്കുക", "തള്ളിക്കളയുക"],
            "Notice": ["വിവരം", "അറിയിപ്പ്"],
            "Legal Notice": ["ലീഗൽ നോട്ടീസ്", "വക്കീൽ നോട്ടീസ്"]
        }

        if en_term in informal_mappings:
            for inf in informal_mappings[en_term]:
                if inf in ml_text and canonical_ml not in ml_text:
                    new_text = ml_text.replace(inf, canonical_ml)
                    return new_text, True
        return ml_text, False

    def _verify_modality_and_negation_ml(self, source_en: str, target_ml: str) -> List[Dict[str, Any]]:
        """Audits modal obligation and strict negation consistency in Malayalam."""
        issues = []
        source_lower = source_en.lower()

        # Strict negations in Malayalam
        has_en_negation = any(neg in source_lower for neg in [
            "shall not", "must not", "may not", "no person shall", "in no event shall", "cannot", "void ab initio"
        ])

        has_ml_negation = any(neg in target_ml for neg in [
            "പാടില്ല", "അരുത്", "ഇല്ല", "അല്ല", "കഴിയില്ല", "ശൂന്യം", "റദ്ദാക്കി", "വിലക്കിയിരിക്കുന്നു", "പരാജയപ്പെട്ടു"
        ])

        if has_en_negation and not has_ml_negation:
            issues.append({
                "severity": "critical",
                "code": "negation_missing_ml",
                "message": "CRITICAL: English source contains strict legal negation/prohibition, but no negation was detected in Malayalam translation!"
            })

        # Mandatory 'shall' vs permissive 'may' in Malayalam
        if "shall not" not in source_lower and "shall" in source_lower:
            if any(p in target_ml for p in ["ചെയ്യാം", "ആകാം"]) and not any(m in target_ml for m in ["ചെയ്യേണ്ടതാണ്", "ബാധ്യസ്ഥനാണ്", "ഉത്തരവാദിയാണ്", "നിർബന്ധം"]):
                issues.append({
                    "severity": "warning",
                    "code": "modality_weakened_ml",
                    "message": "Warning: Mandatory obligation ('shall') appears to have been translated permissively in Malayalam ('ചെയ്യാം')."
                })

        return issues

    def _patch_missing_negation_ml(self, ml_text: str) -> str:
        """Injects negation marker into Malayalam when critical negation was omitted."""
        if "ചെയ്യേണ്ടതാണ്" in ml_text:
            return ml_text.replace("ചെയ്യേണ്ടതാണ്", "ചെയ്യാൻ പാടില്ല")
        elif "ആയിരിക്കേണ്ടതാണ്" in ml_text:
            return ml_text.replace("ആയിരിക്കേണ്ടതാണ്", "ആകാൻ പാടില്ല")
        else:
            return f"{ml_text} (വിലക്കിയിരിക്കുന്നു)"

    def _is_entity_present_in_tamil(self, ent: str, ta_text: str) -> bool:
        """
        Robustly determines whether an entity (number, date, section, pin code, or currency)
        is genuinely present in the Tamil translation.
        """
        ent_lower = ent.lower().strip()

        # 1. Word amounts: "Rupees Two Lakh..." -> in Tamil "ரூபாய்", "ரூ", "லட்சம்", "ஆயிரம்"
        if ent_lower.startswith(("rupees", "indian rupees")):
            return any(w in ta_text for w in ["ரூபாய்", "ரூ", "லட்சம்", "ஆயிரம்", "கோடி", "₹"])

        # 2. Direct variants match
        variants = self._generate_entity_variants_ta(ent)
        if any(var in ta_text for var in variants):
            return True

        # 3. Formatted numbers with commas (e.g. 2,50,000 or 30,000 or 2,80,000)
        formatted_nums = re.findall(r"\b\d{1,3}(?:,\d{2,3})*(?:\.\d+)?\b", ent)
        for fn in formatted_nums:
            if fn in ta_text:
                return True

        # 4. Check raw digit sequences
        raw_digits = re.findall(r"\d+", ent)
        if raw_digits:
            if all(d in ta_text for d in raw_digits):
                return True
            combined = "".join(raw_digits)
            ta_digits = "".join(re.findall(r"\d+", ta_text))
            if len(combined) >= 3 and combined in ta_digits:
                return True

        # 5. Tamil Dates check
        months_en_to_ta = {
            "january": "ஜனவரி", "february": "பிப்ரவரி", "march": "மார்ச்",
            "april": "ஏப்ரல்", "may": "மே", "june": "ஜூன்",
            "july": "ஜூலை", "august": "ஆகஸ்ட்", "september": "செப்டம்பர்",
            "october": "அக்டோபர்", "november": "நவம்பர்", "december": "டிசம்பர்"
        }
        for m_en, m_ta in months_en_to_ta.items():
            if m_en in ent_lower and m_ta in ta_text:
                years = re.findall(r"\b(19\d\d|20\d\d)\b", ent)
                if not years or any(y in ta_text for y in years):
                    return True

        # 6. Percentage check
        if "%" in ent:
            pct_num = re.sub(r"[^\d.]", "", ent)
            if f"{pct_num}%" in ta_text or f"{pct_num} %" in ta_text or f"{pct_num} சதவீதம்" in ta_text:
                return True

        return False

    def _generate_entity_variants_ta(self, ent: str) -> List[str]:
        """Generates possible representations of an entity in Tamil legal text."""
        variants = [ent]
        # Section variations
        sec_m = re.match(r"Sections?\s+(\d+[A-Z]?)", ent, re.IGNORECASE)
        if sec_m:
            num = sec_m.group(1)
            variants.extend([f"பிரிவு {num}", f"பிரிவு {num}-இன் கீழ்", f"பிரிவுகள் {num}"])

        art_m = re.match(r"Articles?\s+(\d+[A-Z]?)", ent, re.IGNORECASE)
        if art_m:
            num = art_m.group(1)
            variants.extend([f"சரத்து {num}", f"சரத்து {num}-இன் கீழ்", f"உறுப்பு {num}"])

        # Currency variations
        if any(c in ent for c in ["INR", "Rs", "₹"]):
            num_clean = re.sub(r"[^\d,.]", "", ent)
            variants.extend([
                f"₹{num_clean}", f"₹ {num_clean}",
                f"{num_clean}/- ரூபாய்", f"ரூ. {num_clean}",
                f"ரூ.{num_clean}", f"{num_clean} ரூபாய்",
                f"₹{num_clean}/-", f"₹ {num_clean}/-"
            ])

        # Date variations
        months = [
            ("January", "ஜனவரி"), ("February", "பிப்ரவரி"), ("March", "மார்ச்"),
            ("April", "ஏப்ரல்"), ("May", "மே"), ("June", "ஜூன்"),
            ("July", "ஜூலை"), ("August", "ஆகஸ்ட்"), ("September", "செப்டம்பர்"),
            ("October", "அக்டோபர்"), ("November", "நவம்பர்"), ("December", "டிசம்பர்")
        ]
        for en_m, ta_m in months:
            if en_m.lower() in ent.lower():
                variants.append(re.sub(en_m, ta_m, ent, flags=re.IGNORECASE))

        return variants

    def _safe_insert_entity_ta(self, ta_text: str, original_ent: str, best_variant: str) -> (str, bool):
        """Safely restores a truly missing entity into Tamil text without duplicate injection."""
        if original_ent.lower().startswith(("rupees", "indian rupees")):
            return ta_text, False

        digits = re.findall(r"\d+", original_ent)
        if digits and any(len(d) >= 2 and d in ta_text for d in digits):
            return ta_text, False

        if any(m in ta_text for m in ["ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்", "ஜூலை", "ஆகஸ்ட்", "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"]):
            if digits and all(d in ta_text for d in digits):
                return ta_text, False

        if best_variant in ta_text:
            return ta_text, False

        localized = best_variant
        localized = re.sub(r"\bINR\s*", "₹", localized, flags=re.IGNORECASE)
        localized = re.sub(r"\bRs\.?\s*", "₹", localized, flags=re.IGNORECASE)
        localized = re.sub(r"\bSection\s+", "பிரிவு ", localized, flags=re.IGNORECASE)

        return f"{ta_text} ({localized})", True

    def _fix_term_drift_ta(self, ta_text: str, en_term: str, canonical_ta: str) -> (str, bool):
        """Attempts to replace informal Tamil equivalents with the canonical term."""
        informal_mappings = {
            "Petitioner": ["மனுசெய்தவர்", "புகார்தாரர்"],
            "Respondent": ["பதில் மனுதாரர்", "மறுமொழி தருபவர்"],
            "Affidavit": ["உறுதிமொழி", "வாக்குமூலம்"],
            "Quash": ["ரத்து செய்ய", "தள்ளுபடி"],
            "Notice": ["அறிவிப்பு", "தகவல்"],
            "Legal Notice": ["வழக்கறிஞர் நோட்டீஸ்", "சட்ட அறிவிப்பு"]
        }

        if en_term in informal_mappings:
            for inf in informal_mappings[en_term]:
                if inf in ta_text and canonical_ta not in ta_text:
                    new_text = ta_text.replace(inf, canonical_ta)
                    return new_text, True
        return ta_text, False

    def _verify_modality_and_negation_ta(self, source_en: str, target_ta: str) -> List[Dict[str, Any]]:
        """Audits modal obligation and strict negation consistency in Tamil."""
        issues = []
        source_lower = source_en.lower()

        # Strict negations in Tamil
        has_en_negation = any(neg in source_lower for neg in [
            "shall not", "must not", "may not", "no person shall", "in no event shall", "cannot", "void ab initio"
        ])

        has_ta_negation = any(neg in target_ta for neg in [
            "கூடாது", "இல்லை", "முடியாது", "தவறியது", "பூஜ்ஜியம்", "ரத்து", "தடைசெய்யப்பட்டுள்ளது", "செல்லாது"
        ])

        if has_en_negation and not has_ta_negation:
            issues.append({
                "severity": "critical",
                "code": "negation_missing_ta",
                "message": "CRITICAL: English source contains strict legal negation/prohibition, but no negation was detected in Tamil translation!"
            })

        # Mandatory 'shall' vs permissive 'may' in Tamil
        if "shall not" not in source_lower and "shall" in source_lower:
            if any(p in target_ta for p in ["செய்யலாம்", "ஆகலாம்"]) and not any(m in target_ta for m in ["வேண்டும்", "கடமைப்பட்டவர்", "பொறுப்பாவார்", "கட்டாயம்"]):
                issues.append({
                    "severity": "warning",
                    "code": "modality_weakened_ta",
                    "message": "Warning: Mandatory obligation ('shall') appears to have been translated permissively in Tamil ('செய்யலாம்')."
                })

        return issues

    def _patch_missing_negation_ta(self, ta_text: str) -> str:
        """Injects negation marker into Tamil when critical negation was omitted."""
        if "செய்ய வேண்டும்" in ta_text:
            return ta_text.replace("செய்ய வேண்டும்", "செய்யக்கூடாது")
        elif "இருக்க வேண்டும்" in ta_text:
            return ta_text.replace("இருக்க வேண்டும்", "இருக்கக்கூடாது")
        else:
            return f"{ta_text} (தடைசெய்யப்பட்டுள்ளது)"

    def _is_entity_present_in_kannada(self, ent: str, kn_text: str) -> bool:
        """
        Robustly determines whether an entity (number, date, section, pin code, or currency)
        is genuinely present in the Kannada translation.
        """
        ent_lower = ent.lower().strip()

        # 1. Word amounts: "Rupees Two Lakh..." -> in Kannada "ರೂಪಾಯಿ", "ರೂ", "ಲಕ್ಷ", "ಸಾವಿರ"
        if ent_lower.startswith(("rupees", "indian rupees")):
            return any(w in kn_text for w in ["ರೂಪಾಯಿ", "ರೂ", "ಲಕ್ಷ", "ಸಾವಿರ", "ಕೋಟಿ", "₹"])

        # 2. Direct variants match
        variants = self._generate_entity_variants_kn(ent)
        if any(var in kn_text for var in variants):
            return True

        # 3. Formatted numbers with commas (e.g. 2,50,000 or 30,000 or 2,80,000)
        formatted_nums = re.findall(r"\b\d{1,3}(?:,\d{2,3})*(?:\.\d+)?\b", ent)
        for fn in formatted_nums:
            if fn in kn_text:
                return True

        # 4. Check raw digit sequences
        raw_digits = re.findall(r"\d+", ent)
        if raw_digits:
            if all(d in kn_text for d in raw_digits):
                return True
            combined = "".join(raw_digits)
            kn_digits = "".join(re.findall(r"\d+", kn_text))
            if len(combined) >= 3 and combined in kn_digits:
                return True

        # 5. Kannada Dates check
        months_en_to_kn = {
            "january": "ಜನವರಿ", "february": "ಫೆಬ್ರವರಿ", "march": "ಮಾರ್ಚ್",
            "april": "ಏಪ್ರಿಲ್", "may": "ಮೇ", "june": "ಜೂನ್",
            "july": "ಜುಲೈ", "august": "ಆಗಸ್ಟ್", "september": "ಸೆಪ್ಟೆಂಬರ್",
            "october": "ಅಕ್ಟೋಬರ್", "november": "ನವೆಂಬರ್", "december": "ಡಿಸೆಂಬರ್"
        }
        for m_en, m_kn in months_en_to_kn.items():
            if m_en in ent_lower and m_kn in kn_text:
                years = re.findall(r"\b(19\d\d|20\d\d)\b", ent)
                if not years or any(y in kn_text for y in years):
                    return True

        # 6. Percentage check
        if "%" in ent:
            pct_num = re.sub(r"[^\d.]", "", ent)
            if f"{pct_num}%" in kn_text or f"{pct_num} %" in kn_text or f"{pct_num} ಪ್ರತಿಶತ" in kn_text or f"{pct_num} ಶೇಕಡಾ" in kn_text:
                return True

        return False

    def _generate_entity_variants_kn(self, ent: str) -> List[str]:
        """Generates possible representations of an entity in Kannada legal text."""
        variants = [ent]
        # Section variations
        sec_m = re.match(r"Sections?\s+(\d+[A-Z]?)", ent, re.IGNORECASE)
        if sec_m:
            num = sec_m.group(1)
            variants.extend([f"ಸೆಕ್ಷನ್ {num}", f"ವಿಭಾಗ {num}", f"ವಿಭಾಗ {num} ರ ಅಡಿಯಲ್ಲಿ", f"ಸೆಕ್ಷನ್‌ಗಳು {num}"])

        art_m = re.match(r"Articles?\s+(\d+[A-Z]?)", ent, re.IGNORECASE)
        if art_m:
            num = art_m.group(1)
            variants.extend([f"ವಿಧಿ {num}", f"ಅನುಚ್ಛೇದ {num}"])

        # Currency variations
        if any(c in ent for c in ["INR", "Rs", "₹"]):
            num_clean = re.sub(r"[^\d,.]", "", ent)
            variants.extend([
                f"₹{num_clean}", f"₹ {num_clean}",
                f"{num_clean}/- ರೂಪಾಯಿ", f"ರೂ. {num_clean}",
                f"ರೂ.{num_clean}", f"{num_clean} ರೂಪಾಯಿ",
                f"₹{num_clean}/-", f"₹ {num_clean}/-"
            ])

        # Date variations
        months = [
            ("January", "ಜನವರಿ"), ("February", "ಫೆಬ್ರವರಿ"), ("March", "ಮಾರ್ಚ್"),
            ("April", "ಏಪ್ರಿಲ್"), ("May", "ಮೇ"), ("June", "ಜೂನ್"),
            ("July", "ಜುಲೈ"), ("August", "ಆಗಸ್ಟ್"), ("September", "ಸೆಪ್ಟೆಂಬರ್"),
            ("October", "ಅಕ್ಟೋಬರ್"), ("November", "ನವೆಂಬರ್"), ("December", "ಡಿಸೆಂಬರ್")
        ]
        for en_m, kn_m in months:
            if en_m.lower() in ent.lower():
                variants.append(re.sub(en_m, kn_m, ent, flags=re.IGNORECASE))

        return variants

    def _safe_insert_entity_kn(self, kn_text: str, original_ent: str, best_variant: str) -> (str, bool):
        """Safely restores a truly missing entity into Kannada text without duplicate injection."""
        if original_ent.lower().startswith(("rupees", "indian rupees")):
            return kn_text, False

        digits = re.findall(r"\d+", original_ent)
        if digits and any(len(d) >= 2 and d in kn_text for d in digits):
            return kn_text, False

        if any(m in kn_text for m in ["ಜನವರಿ", "ಫೆಬ್ರವರಿ", "ಮಾರ್ಚ್", "ಏಪ್ರಿಲ್", "ಮೇ", "ಜೂನ್", "ಜುಲೈ", "ಆಗಸ್ಟ್", "ಸೆಪ್ಟೆಂಬರ್", "ಅಕ್ಟೋಬರ್", "ನವೆಂಬರ್", "ಡಿಸೆಂಬರ್"]):
            if digits and all(d in kn_text for d in digits):
                return kn_text, False

        if best_variant in kn_text:
            return kn_text, False

        localized = best_variant
        localized = re.sub(r"\bINR\s*", "₹", localized, flags=re.IGNORECASE)
        localized = re.sub(r"\bRs\.?\s*", "₹", localized, flags=re.IGNORECASE)
        localized = re.sub(r"\bSection\s+", "ಸೆಕ್ಷನ್ ", localized, flags=re.IGNORECASE)

        return f"{kn_text} ({localized})", True

    def _fix_term_drift_kn(self, kn_text: str, en_term: str, canonical_kn: str) -> (str, bool):
        """Attempts to replace informal Kannada equivalents with the canonical term."""
        informal_mappings = {
            "Petitioner": ["ಅರ್ಜಿದಾರರು", "ಫಿರ್ಯಾದಿ", "ದೂರುದಾರ"],
            "Respondent": ["ಎದುರುದಾರ", "ಉತ್ತರವಾದಿ"],
            "Affidavit": ["ಪ್ರಮಾಣ ವಚನ", "ಅಫಿಡವಿಟ್"],
            "Quash": ["ರದ್ದು", "ಖುಲಾಸೆ"],
            "Notice": ["ಸೂಚನೆ", "ಮಾಹಿತಿ"],
            "Legal Notice": ["ವಕೀಲರ ನೋಟಿಸ್", "ಕಾನೂನು ಸೂಚನೆ"]
        }

        if en_term in informal_mappings:
            for inf in informal_mappings[en_term]:
                if inf in kn_text and canonical_kn not in kn_text:
                    new_text = kn_text.replace(inf, canonical_kn)
                    return new_text, True
        return kn_text, False

    def _verify_modality_and_negation_kn(self, source_en: str, target_kn: str) -> List[Dict[str, Any]]:
        """Audits modal obligation and strict negation consistency in Kannada."""
        issues = []
        source_lower = source_en.lower()

        # Strict negations in Kannada
        has_en_negation = any(neg in source_lower for neg in [
            "shall not", "must not", "may not", "no person shall", "in no event shall", "cannot", "void ab initio"
        ])

        has_kn_negation = any(neg in target_kn for neg in [
            "ಮಾಡತಕ್ಕದ್ದಲ್ಲ", "ಕೂಡದು", "ಇಲ್ಲ", "ಅಲ್ಲ", "ಸಾಧ್ಯವಿಲ್ಲ", "ವಿಫಲ", "ಶೂನ್ಯ", "ರದ್ದು", "ನಿಷೇಧಿಸಲಾಗಿದೆ", "ಅನೂರ್ಜಿತ"
        ])

        if has_en_negation and not has_kn_negation:
            issues.append({
                "severity": "critical",
                "code": "negation_missing_kn",
                "message": "CRITICAL: English source contains strict legal negation/prohibition, but no negation was detected in Kannada translation!"
            })

        # Mandatory 'shall' vs permissive 'may' in Kannada
        if "shall not" not in source_lower and "shall" in source_lower:
            if any(p in target_kn for p in ["ಮಾಡಬಹುದು", "ಆಗಬಹುದು"]) and not any(m in target_kn for m in ["ಮಾಡತಕ್ಕದ್ದು", "ಬದ್ಧನಾಗಿರತಕ್ಕದ್ದು", "ಹೊಣೆಗಾರ", "ಖಡ್ಡಾಯ"]):
                issues.append({
                    "severity": "warning",
                    "code": "modality_weakened_kn",
                    "message": "Warning: Mandatory obligation ('shall') appears to have been translated permissively in Kannada ('ಮಾಡಬಹುದು')."
                })

        return issues

    def _patch_missing_negation_kn(self, kn_text: str) -> str:
        """Injects negation marker into Kannada when critical negation was omitted."""
        if "ಮಾಡತಕ್ಕದ್ದು" in kn_text:
            return kn_text.replace("ಮಾಡತಕ್ಕದ್ದು", "ಮಾಡತಕ್ಕದ್ದಲ್ಲ")
        elif "ಆಗಿರತಕ್ಕದ್ದು" in kn_text:
            return kn_text.replace("ಆಗಿರತಕ್ಕದ್ದು", "ಆಗಿರತಕ್ಕದ್ದಲ್ಲ")
        else:
            return f"{kn_text} (ನಿಷೇಧಿಸಲಾಗಿದೆ)"
