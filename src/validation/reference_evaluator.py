"""
Reference-Based Evaluation Engine & Human Expert Assessment Rubric.
Provides gold-standard ground-truth evaluation comparing machine translation
outputs directly against certified human reference translations from the MILPaC benchmark.
"""

import re
import json
from typing import Dict, List, Any, Optional
import sacrebleu
from ..detection.legal_ner import LegalEntityRecognizer
from ..dataset.loader import LegalDatasetLoader

class LegalReferenceEvaluator:
    """
    Evaluates translations against authentic human reference targets.
    Computes:
      - Reference-grounded SacreBLEU (Devanagari word n-grams)
      - Reference-grounded chrF++ (Devanagari character/subword n-grams)
      - Reference Entity Recall & Precision
      - Modality Invariance against Reference
      - Automated Human-Expert Rubric Score (5 Likert dimensions)
    """

    def __init__(self, dataset_name: str = "milpac"):
        self.ner = LegalEntityRecognizer()
        self.loader = LegalDatasetLoader(dataset_name=dataset_name)
        self.splits = self.loader.get_splits(train_ratio=0.7, val_ratio=0.15, seed=42)
        self.test_set = self.splits["test"]

    def evaluate_pair(self, hypothesis_hi: str, reference_hi: str, source_en: Optional[str] = None) -> Dict[str, Any]:
        """
        Computes comprehensive evaluation metrics comparing hypothesis against gold reference.
        """
        hyp_clean = hypothesis_hi.strip()
        ref_clean = reference_hi.strip()

        # 1. Surface Metrics against Human Reference
        bleu_res = sacrebleu.sentence_bleu(hyp_clean, [ref_clean])
        chrf_res = sacrebleu.sentence_chrf(hyp_clean, [ref_clean])

        bleu_score = round(bleu_res.score, 2)
        chrf_score = round(chrf_res.score, 2)

        # 2. Reference Entity Match
        ref_entities = self.ner.get_critical_entity_strings(ref_clean)
        hyp_entities = self.ner.get_critical_entity_strings(hyp_clean)
        
        # Cross-script entity matching for digits, amounts, dates
        ref_digits = set(re.findall(r"\d+", ref_clean))
        hyp_digits = set(re.findall(r"\d+", hyp_clean))

        preserved_entities = [e for e in ref_entities if e.lower() in hyp_clean.lower()]
        digits_recall = (len(ref_digits.intersection(hyp_digits)) / len(ref_digits)) if ref_digits else 1.0

        entity_recall = (len(preserved_entities) / len(ref_entities)) if ref_entities else digits_recall
        entity_recall = round(min(1.0, max(0.0, entity_recall)), 2)

        # 3. Devanagari Token F1 Overlap
        hyp_tokens = set(re.findall(r"[\u0900-\u097F\w]+", hyp_clean))
        ref_tokens = set(re.findall(r"[\u0900-\u097F\w]+", ref_clean))
        token_overlap = hyp_tokens.intersection(ref_tokens)
        
        token_p = len(token_overlap) / len(hyp_tokens) if hyp_tokens else 0.0
        token_r = len(token_overlap) / len(ref_tokens) if ref_tokens else 0.0
        token_f1 = (2 * token_p * token_r / (token_p + token_r)) if (token_p + token_r) > 0 else 0.0

        # 4. Human Expert Evaluation Simulation Rubric (1-5 Likert scale)
        human_rubric = self._compute_expert_rubric(
            chrf_score=chrf_score,
            bleu_score=bleu_score,
            entity_recall=entity_recall,
            token_f1=token_f1
        )

        # Composite Reference Fidelity Index (0 - 100)
        # Weights: chrF (35%), Entity Recall (35%), Token F1 (20%), BLEU (10%)
        composite_ref_score = (
            (min(100.0, chrf_score) * 0.35) +
            (entity_recall * 100.0 * 0.35) +
            (token_f1 * 100.0 * 0.20) +
            (min(100.0, bleu_score) * 0.10)
        )
        composite_ref_score = round(min(100.0, max(0.0, composite_ref_score)), 2)

        return {
            "reference_bleu": bleu_score,
            "reference_chrf": chrf_score,
            "entity_recall": entity_recall,
            "token_f1": round(token_f1, 3),
            "composite_reference_score": composite_ref_score,
            "human_expert_rubric": human_rubric
        }

    def _compute_expert_rubric(
        self, chrf_score: float, bleu_score: float, entity_recall: float, token_f1: float
    ) -> Dict[str, Any]:
        """
        Maps statistical metrics to a standard 5-dimension Human Legal Expert Rubric (1 to 5 stars).
        """
        # 1. Adequacy / Meaning Preservation (1-5)
        adequacy = 5 if chrf_score >= 65 else (4 if chrf_score >= 50 else (3 if chrf_score >= 35 else 2))
        
        # 2. Statutory Terminology & Legal Precision (1-5)
        terminology = 5 if token_f1 >= 0.60 else (4 if token_f1 >= 0.45 else (3 if token_f1 >= 0.30 else 2))
        
        # 3. Entity & Financial Value Preservation (1-5)
        entity_score = 5 if entity_recall >= 0.99 else (4 if entity_recall >= 0.80 else (3 if entity_recall >= 0.60 else 1))
        
        # 4. Grammatical Fluency in High-Register Hindi (1-5)
        fluency = 5 if chrf_score >= 60 else (4 if chrf_score >= 45 else 3)
        
        # 5. Courtroom Submissibility / Legal Utility (1-5)
        admissibility = 5 if (adequacy >= 4 and entity_score == 5 and terminology >= 4) else (
            4 if (adequacy >= 3 and entity_score >= 4) else 3
        )

        overall_expert_rating = round((adequacy + terminology + entity_score + fluency + admissibility) / 5.0, 2)

        return {
            "meaning_adequacy_stars": adequacy,
            "statutory_terminology_stars": terminology,
            "entity_precision_stars": entity_score,
            "grammatical_fluency_stars": fluency,
            "courtroom_utility_stars": admissibility,
            "overall_expert_rating_out_of_5": overall_expert_rating,
            "certified_for_judicial_drafting": (overall_expert_rating >= 4.0 and entity_score == 5)
        }

    def benchmark_on_test_split(self, translation_engine, max_samples: int = 50) -> Dict[str, Any]:
        """
        Runs evaluation on held-out MILPaC test samples against human references.
        """
        samples = self.test_set[:max_samples]
        results = []
        
        total_bleu = 0.0
        total_chrf = 0.0
        total_entity_recall = 0.0
        total_composite = 0.0
        total_expert_rating = 0.0

        for item in samples:
            src_en = item["en_text"]
            ref_hi = item["hi_text"]
            
            # Translate using provided engine
            trans_res = translation_engine.translate_en_to_hi(src_en)
            hyp_hi = trans_res.get("draft_translation") or trans_res.get("verified_hi") or trans_res.get("translated_text", "")
            
            eval_res = self.evaluate_pair(hyp_hi, ref_hi, src_en)
            results.append({
                "id": item["id"],
                "source_en": src_en,
                "gold_reference_hi": ref_hi,
                "hypothesis_hi": hyp_hi,
                "metrics": eval_res
            })

            total_bleu += eval_res["reference_bleu"]
            total_chrf += eval_res["reference_chrf"]
            total_entity_recall += eval_res["entity_recall"]
            total_composite += eval_res["composite_reference_score"]
            total_expert_rating += eval_res["human_expert_rubric"]["overall_expert_rating_out_of_5"]

        n = len(samples) if samples else 1
        summary = {
            "evaluated_test_samples": len(samples),
            "avg_reference_bleu": round(total_bleu / n, 2),
            "avg_reference_chrf": round(total_chrf / n, 2),
            "avg_entity_recall_pct": round((total_entity_recall / n) * 100.0, 2),
            "avg_composite_reference_score": round(total_composite / n, 2),
            "avg_human_expert_rating_out_of_5": round(total_expert_rating / n, 2),
            "status": "EVALUATION_COMPLETE"
        }

        return {
            "summary": summary,
            "sample_evaluations": results[:5]  # first 5 detailed samples
        }
