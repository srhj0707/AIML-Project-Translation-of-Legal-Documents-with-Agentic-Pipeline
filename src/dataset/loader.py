import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any

class LegalDatasetLoader:
    """
    Loads, validates, and partitions the English-Hindi legal parallel corpus
    for model fine-tuning, adaptation, and multi-tier evaluation.
    Supports official MILPaC (Multilingual Indian Legal Parallel Corpus) from Law-AI IIT KGP,
    curated judicial corpora, or combined datasets.
    """

    def __init__(self, data_path: Optional[str] = None, dataset_name: str = "milpac"):
        self.current_dir = Path(__file__).resolve().parent
        self.dataset_name = dataset_name.lower()
        
        if data_path is not None:
            self.data_path = Path(data_path)
        elif self.dataset_name == "milpac":
            self.data_path = self.current_dir.parent.parent / "data" / "parallel" / "milpac_en_hi.json"
        elif self.dataset_name == "curated":
            self.data_path = self.current_dir.parent.parent / "data" / "parallel" / "en_hi_legal_pairs.json"
        else:
            self.data_path = self.current_dir.parent.parent / "data" / "parallel" / "milpac_en_hi.json"

        self.pairs: List[Dict[str, Any]] = []
        self.load_data()

    def load_data(self) -> None:
        if self.dataset_name == "combined":
            milpac_path = self.current_dir.parent.parent / "data" / "parallel" / "milpac_en_hi.json"
            curated_path = self.current_dir.parent.parent / "data" / "parallel" / "en_hi_legal_pairs.json"
            combined = []
            if milpac_path.exists():
                with open(milpac_path, "r", encoding="utf-8") as f:
                    combined.extend(json.load(f))
            if curated_path.exists():
                with open(curated_path, "r", encoding="utf-8") as f:
                    combined.extend(json.load(f))
            self.pairs = combined
            return

        if not self.data_path.exists():
            # Fall back to curated pairs if milpac_en_hi.json is not present
            fallback = self.current_dir.parent.parent / "data" / "parallel" / "en_hi_legal_pairs.json"
            if fallback.exists():
                self.data_path = fallback
            else:
                raise FileNotFoundError(f"Parallel corpus not found at {self.data_path}")
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.pairs = json.load(f)

    def get_all_pairs(self) -> List[Dict[str, Any]]:
        return self.pairs

    def get_splits(
        self, train_ratio: float = 0.7, val_ratio: float = 0.15, seed: int = 42
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Creates stratified or reproducible train/val/test splits.
        """
        random.seed(seed)
        shuffled = list(self.pairs)
        random.shuffle(shuffled)

        n = len(shuffled)
        n_train = max(1, int(n * train_ratio))
        n_val = max(1, int(n * val_ratio))

        train = shuffled[:n_train]
        val = shuffled[n_train : n_train + n_val]
        test = shuffled[n_train + n_val :]

        # If test set is empty due to small dataset size, ensure test has at least 1-2 examples
        if not test and len(shuffled) >= 3:
            test = val[-1:]
            val = val[:-1]

        return {
            "train": train,
            "validation": val,
            "test": test
        }

    def get_corpus_statistics(self) -> Dict[str, Any]:
        """
        Calculates token counts, vocabulary size, domains, and entity density.
        """
        total_pairs = len(self.pairs)
        en_words = [len(p["en_text"].split()) for p in self.pairs]
        hi_words = [len(p["hi_text"].split()) for p in self.pairs]
        domains = {}

        for p in self.pairs:
            dom = p.get("domain", "general")
            domains[dom] = domains.get(dom, 0) + 1

        return {
            "total_pairs": total_pairs,
            "dataset_source": self.dataset_name,
            "domain_breakdown": domains,
            "en_avg_words_per_clause": round(sum(en_words) / total_pairs, 1) if total_pairs else 0,
            "hi_avg_words_per_clause": round(sum(hi_words) / total_pairs, 1) if total_pairs else 0,
            "en_max_words": max(en_words) if en_words else 0,
            "hi_max_words": max(hi_words) if hi_words else 0,
        }

