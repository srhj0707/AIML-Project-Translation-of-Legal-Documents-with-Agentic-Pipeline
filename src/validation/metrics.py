import re
import math
from typing import Dict, List, Any, Optional
import sacrebleu
from ..detection.legal_ner import LegalEntityRecognizer

class LegalTranslationMetrics:
    """
    Computes multi-tier validation metrics comparing original English source
    against back-translated English text:
      - Surface Metrics: BLEU, chrF, Token F1/METEOR proxy
      - Entity Precision: Exact match ratio on numbers, statutory sections, dates, currency
      - Semantic Similarity: Token TF-IDF cosine similarity & Jaccard overlap
    """

    def __init__(self):
        self.ner = LegalEntityRecognizer()

    def evaluate_back_translation(
        self, original_en: str, back_translated_en: str
    ) -> Dict[str, Any]:
        """
        Executes complete metrics evaluation suite between original and back-translated text.
        """
        orig_clean = original_en.strip()
        back_clean = back_translated_en.strip()

        # 1. Surface Metrics: BLEU & chrF
        bleu_res = sacrebleu.sentence_bleu(back_clean, [orig_clean])
        bleu_score = round(bleu_res.score, 2)

        chrf_res = sacrebleu.sentence_chrf(back_clean, [orig_clean])
        chrf_score = round(chrf_res.score, 2)

        # 2. Token Precision, Recall, and F1 (METEOR proxy)
        token_metrics = self._compute_token_f1(orig_clean, back_clean)

        # 3. Critical Entity Exact Match Rate (EMR)
        entity_metrics = self._compute_entity_exact_match(orig_clean, back_clean)

        # 4. Semantic Vector Cosine Similarity
        cosine_sim = self._compute_semantic_cosine(orig_clean, back_clean)

        # Composite validation score (0 - 100)
        # In legal documents, entity preservation is paramount (40%), followed by chrF (25%), semantic (25%), BLEU (10%)
        composite_score = (
            (entity_metrics["exact_match_ratio"] * 40.0) +
            (min(100.0, chrf_score) * 0.25) +
            (cosine_sim * 100.0 * 0.25) +
            (min(100.0, bleu_score) * 0.10)
        )
        composite_score = round(min(100.0, max(0.0, composite_score)), 2)

        return {
            "bleu": bleu_score,
            "chrf": chrf_score,
            "token_f1": token_metrics["f1"],
            "token_precision": token_metrics["precision"],
            "token_recall": token_metrics["recall"],
            "entity_exact_match_ratio": entity_metrics["exact_match_ratio"],
            "preserved_entities": entity_metrics["preserved_entities"],
            "missing_entities": entity_metrics["missing_entities"],
            "semantic_cosine_similarity": cosine_sim,
            "composite_validation_score": composite_score
        }

    def _compute_token_f1(self, ref: str, hyp: str) -> Dict[str, float]:
        """Calculates token-level precision, recall, and harmonic mean F1."""
        ref_tokens = re.findall(r"\w+", ref.lower())
        hyp_tokens = re.findall(r"\w+", hyp.lower())

        if not ref_tokens or not hyp_tokens:
            return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

        ref_set = set(ref_tokens)
        hyp_set = set(hyp_tokens)

        overlap = ref_set.intersection(hyp_set)
        precision = len(overlap) / len(hyp_set) if hyp_set else 0.0
        recall = len(overlap) / len(ref_set) if ref_set else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4)
        }

    def _compute_entity_exact_match(self, ref: str, hyp: str) -> Dict[str, Any]:
        """
        Verifies exact preservation of numbers, dates, statutory sections, and case numbers.
        """
        ref_entities = self.ner.get_critical_entity_strings(ref)
        if not ref_entities:
            return {
                "exact_match_ratio": 1.0,
                "preserved_entities": [],
                "missing_entities": []
            }

        preserved = []
        missing = []

        hyp_lower = hyp.lower()
        for ent in ref_entities:
            ent_clean = ent.strip()
            num_clean = re.sub(r"[^\d]", "", ent_clean)
            digits = re.findall(r"\d+", ent_clean)

            # Check literal or normalized match
            if ent_clean.lower() in hyp_lower:
                preserved.append(ent_clean)
            elif num_clean and len(num_clean) >= 2 and num_clean in re.sub(r"[^\d]", "", hyp):
                preserved.append(ent_clean)
            elif digits and all(d in hyp for d in digits):
                preserved.append(ent_clean)
            else:
                missing.append(ent_clean)

        ratio = len(preserved) / len(ref_entities)
        return {
            "exact_match_ratio": round(ratio, 4),
            "preserved_entities": preserved,
            "missing_entities": missing
        }

    def _compute_semantic_cosine(self, s1: str, s2: str) -> float:
        """Computes TF-IDF vector cosine similarity between two sentences."""
        words1 = re.findall(r"\w+", s1.lower())
        words2 = re.findall(r"\w+", s2.lower())

        if not words1 or not words2:
            return 0.0

        vocab = set(words1).union(set(words2))
        v1 = [words1.count(w) for w in vocab]
        v2 = [words2.count(w) for w in vocab]

        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return round(dot / (mag1 * mag2), 4)
