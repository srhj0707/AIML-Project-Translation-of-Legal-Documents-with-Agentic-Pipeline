from typing import List, Dict, Any
from ..dataset.preprocessor import LegalTextPreprocessor
from .language_detector import LegalLanguageDetector
from .legal_ner import LegalEntityRecognizer

class LegalClauseSegmenter:
    """
    Stage 1 Detection Orchestrator:
    Segments raw legal documents into translation units, performs language and script verification,
    extracts legal entities, and flags high-risk legal clauses (e.g., negative obligations, fines, bail).
    """

    def __init__(self):
        self.preprocessor = LegalTextPreprocessor()
        self.lang_detector = LegalLanguageDetector()
        self.ner = LegalEntityRecognizer()

    def process_document(self, document_text: str) -> List[Dict[str, Any]]:
        """
        Executes Stage 1 Detection over an entire legal document.
        Returns a structured list of annotated clauses.
        """
        # Step 1: Preprocessing & clause boundary segmentation
        raw_clauses = self.preprocessor.segment_into_clauses(document_text)
        annotated_clauses: List[Dict[str, Any]] = []

        for item in raw_clauses:
            text = item["source_text"]

            # Step 2: Language & script detection
            lang_info = self.lang_detector.detect(text)

            # Step 3: Legal entity recognition
            entities = self.ner.extract_entities(text)
            critical_tokens = self.ner.get_critical_entity_strings(text)

            # Step 4: Legal risk assessment
            # Clauses with financial obligations, criminal statutes, or negative obligations are high-risk
            has_modals = len(entities["legal_modals"]) > 0
            has_money = len(entities["monetary_amounts"]) > 0
            has_statutes = len(entities["statutes"]) > 0 or len(entities["sections"]) > 0
            has_prohibitions = any(
                m["text"] in ["shall not", "must not", "may not"]
                for m in entities["legal_modals"]
            )

            risk_level = "standard"
            if has_prohibitions or (has_money and has_statutes):
                risk_level = "critical"
            elif has_money or has_statutes or has_modals:
                risk_level = "elevated"

            annotated_clause = {
                "clause_id": item["clause_id"],
                "clause_marker": item["clause_marker"],
                "clause_type": item["clause_type"],
                "source_text": text,
                "word_count": item["word_count"],
                "language": lang_info,
                "entities": entities,
                "critical_tokens": critical_tokens,
                "risk_level": risk_level,
                "requires_heightened_scrutiny": (risk_level in ["critical", "elevated"])
            }
            annotated_clauses.append(annotated_clause)

        return annotated_clauses
