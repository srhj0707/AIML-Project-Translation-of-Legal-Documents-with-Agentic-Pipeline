from typing import Dict, List, Any, Optional
from ..glossary.manager import LegalGlossaryManager
from ..detection.clause_segmenter import LegalClauseSegmenter
from ..translation.nlp_engine import LegalNLPEngine
from ..translation.agentic_reviewer import AgenticReviewer
from ..validation.back_translator import LegalBackTranslator
from ..validation.metrics import LegalTranslationMetrics
from ..validation.legal_judge import LegalMeaningJudge

class LegalAgentOrchestrator:
    """
    End-to-End Orchestrator for English-to-Hindi Legal Document Translation,
    Agentic Review, and Round-Trip Validation.

    Workflow:
      Document -> Stage 1: Detection -> Stage 2: Translation (NLP + Agentic AI)
               -> Stage 3: Validation (Back-Translation + Metrics + Legal Judge)
               -> Aggregated Evaluation & Audit Report
    """

    def __init__(self, glossary_path: Optional[str] = None):
        self.glossary = LegalGlossaryManager(glossary_path)
        self.segmenter = LegalClauseSegmenter()
        self.nlp_engine = LegalNLPEngine(self.glossary)
        self.agent_reviewer = AgenticReviewer(self.glossary)
        self.back_translator = LegalBackTranslator(self.glossary)
        self.metrics_engine = LegalTranslationMetrics()
        self.legal_judge = LegalMeaningJudge(self.glossary)

    def process_document(self, document_text: str, target_lang: str = "hi") -> Dict[str, Any]:
        """
        Executes full multi-stage translation, agentic review, and validation on a legal document.
        Supports target_lang='hi' (Hindi), target_lang='te' (Telugu - Dravidian), target_lang='ml' (Malayalam - Dravidian), target_lang='ta' (Tamil - Dravidian), and target_lang='kn' (Kannada - Dravidian).
        """
        lang = target_lang.lower().strip()
        is_telugu = (lang == "te")
        is_malayalam = (lang == "ml")
        is_tamil = (lang == "ta")
        is_kannada = (lang == "kn")

        # ================= STAGE 1: DETECTION =================
        detected_clauses = self.segmenter.process_document(document_text)

        processed_clauses: List[Dict[str, Any]] = []
        total_bleu = 0.0
        total_chrf = 0.0
        total_emr = 0.0
        total_fidelity = 0.0
        flagged_clauses_count = 0

        for clause in detected_clauses:
            source_en = clause["source_text"]

            # ================= STAGE 2: TRANSLATION =================
            # 2a. Base NLP Translation Draft
            if is_kannada:
                nlp_result = self.nlp_engine.translate_en_to_kn(source_en)
            elif is_tamil:
                nlp_result = self.nlp_engine.translate_en_to_ta(source_en)
            elif is_malayalam:
                nlp_result = self.nlp_engine.translate_en_to_ml(source_en)
            elif is_telugu:
                nlp_result = self.nlp_engine.translate_en_to_te(source_en)
            else:
                nlp_result = self.nlp_engine.translate_en_to_hi(source_en)
            draft_trans = nlp_result["draft_translation"]

            # 2b. Agentic AI Review & Rectification
            agent_review = self.agent_reviewer.review_clause(
                source_en=source_en,
                draft_hi=draft_trans,
                detected_entities=clause["entities"],
                target_lang=lang,
                draft_translation=draft_trans
            )
            verified_trans = agent_review["verified_translation"]

            # ================= STAGE 3: VALIDATION =================
            # 3a. Back-Translation (Target -> EN)
            if is_kannada:
                back_trans_result = self.back_translator.translate_kn_to_en(verified_trans)
            elif is_tamil:
                back_trans_result = self.back_translator.translate_ta_to_en(verified_trans)
            elif is_malayalam:
                back_trans_result = self.back_translator.translate_ml_to_en(verified_trans)
            elif is_telugu:
                back_trans_result = self.back_translator.translate_te_to_en(verified_trans)
            else:
                back_trans_result = self.back_translator.translate_hi_to_en(verified_trans)
            back_en = back_trans_result["back_translation"]

            # 3b. Quantitative Metrics
            metrics = self.metrics_engine.evaluate_back_translation(source_en, back_en)

            # 3c. Legal-Meaning Fidelity Judge
            judge_eval = self.legal_judge.evaluate_clause_fidelity(
                original_en=source_en,
                translated_hi=verified_trans,
                back_translated_en=back_en,
                target_lang=lang
            )

            # Check if clause needs human review
            requires_human_review = (
                agent_review["requires_human_review"] or
                judge_eval["verdict"] != "PASSED" or
                metrics["entity_exact_match_ratio"] < 1.0
            )

            if requires_human_review:
                flagged_clauses_count += 1

            total_bleu += metrics["bleu"]
            total_chrf += metrics["chrf"]
            total_emr += metrics["entity_exact_match_ratio"]
            total_fidelity += judge_eval["overall_fidelity_score"]

            clause_record = {
                "clause_id": clause["clause_id"],
                "clause_marker": clause["clause_marker"],
                "clause_type": clause["clause_type"],
                "risk_level": clause["risk_level"],
                "source_en": source_en,
                "draft_translation": draft_trans,
                "verified_translation": verified_trans,
                "draft_hi": draft_trans,      # Backward compatibility
                "verified_hi": verified_trans,  # Backward compatibility
                "back_translated_en": back_en,
                "agent_review": agent_review,
                "metrics": metrics,
                "judge_evaluation": judge_eval,
                "requires_human_review": requires_human_review,
                "critical_entities": clause["critical_tokens"],
                "target_lang": lang
            }
            processed_clauses.append(clause_record)

        n = len(processed_clauses)
        avg_bleu = round(total_bleu / n, 2) if n else 0.0
        avg_chrf = round(total_chrf / n, 2) if n else 0.0
        avg_emr = round((total_emr / n) * 100.0, 2) if n else 0.0
        avg_fidelity = round(total_fidelity / n, 2) if n else 0.0

        overall_status = "VERIFIED_READY" if flagged_clauses_count == 0 else "REVIEW_REQUIRED"

        # Reconstructed translated document
        full_translated_document = "\n\n".join(
            c["verified_translation"] for c in processed_clauses
        )

        if is_kannada:
            target_lang_display = "Kannada (ಕನ್ನಡ)"
        elif is_tamil:
            target_lang_display = "Tamil (தமிழ்)"
        elif is_malayalam:
            target_lang_display = "Malayalam (മലയാളം)"
        elif is_telugu:
            target_lang_display = "Telugu (తెలుగు)"
        else:
            target_lang_display = "Hindi (हिंदी)"

        result_dict = {
            "overall_status": overall_status,
            "target_language": target_lang_display,
            "target_lang_code": lang,
            "document_summary": {
                "total_clauses": n,
                "flagged_clauses_count": flagged_clauses_count,
                "verified_clauses_count": n - flagged_clauses_count,
                "avg_back_trans_bleu": avg_bleu,
                "avg_back_trans_chrf": avg_chrf,
                "avg_entity_preservation_pct": avg_emr,
                "avg_legal_fidelity_score": avg_fidelity
            },
            "translated_document": full_translated_document,
            "clauses": processed_clauses
        }

        # Maintain backwards-compatible fields
        if is_kannada:
            result_dict["translated_document_kannada"] = full_translated_document
            result_dict["translated_document_hindi"] = full_translated_document  # For callers expecting translated_document_hindi
        elif is_tamil:
            result_dict["translated_document_tamil"] = full_translated_document
            result_dict["translated_document_hindi"] = full_translated_document  # For callers expecting translated_document_hindi
        elif is_malayalam:
            result_dict["translated_document_malayalam"] = full_translated_document
            result_dict["translated_document_hindi"] = full_translated_document  # For callers expecting translated_document_hindi
        elif is_telugu:
            result_dict["translated_document_telugu"] = full_translated_document
            result_dict["translated_document_hindi"] = full_translated_document  # For callers expecting translated_document_hindi
        else:
            result_dict["translated_document_hindi"] = full_translated_document

        return result_dict
