import re
from typing import List, Dict, Any, Tuple

class LegalTextPreprocessor:
    """
    Cleans, normalizes, and segments legal documents into clause-level translation units
    while preserving legal numbering, abbreviations, statutory references, and recitals.
    """

    # Common legal abbreviations that must not trigger sentence splits
    LEGAL_ABBREVIATIONS = [
        r"vs\.", r"v\.", r"no\.", r"nos\.", r"sec\.", r"secs\.", r"art\.", r"arts\.",
        r"para\.", r"paras\.", r"hon'ble", r"mr\.", r"mrs\.", r"ms\.", r"dr\.",
        r"adv\.", r"pvt\.", r"ltd\.", r"co\.", r"corp\.", r"inc\.", r"ors\.", r"anr\.",
        r"air", r"scc", r"scr", r"cr\.?l\.?j\.", r"u/s\.", r"i\.e\.", r"e\.g\.",
        r"viz\.", r"etc\.", r"al\.", r"govt\.", r"dept\.", r"dist\."
    ]

    # Patterns for legal clause numbering and recital boundaries
    CLAUSE_NUMBER_PATTERNS = [
        # Numeric standard & hierarchical with dot, hyphen, parenthesis, or colon:
        # e.g., "1.", "1-", "1 -", "1)", "(1)", "1.1", "1.1.1", "1:", "Clause 1:", "Section 1:"
        r"^\s*(?:(?:Clause|Article|Section|Rule|Para|Paragraph|Point|Item)\s+)?(\d+(?:\.\d+)*[\.\-\:\)]|\(\d+\))\s*",
        # Hyphenated digits: "1-", "2-", etc.
        r"^\s*(\d+\s*[-–—]\s*)",
        # Alphabetical: "(a)", "(b)", "a)", "a.", "A.", "(A)"
        r"^\s*(\([a-zA-Z]\)|[a-zA-Z][\.\-\:\)])\s*",
        # Roman numerals: "(i)", "(ii)", "(iv)", "i)", "i.", "IV.", "(IV)"
        r"^\s*(\([ivxIVX]+\)|[ivxIVX]+[\.\-\:\)])\s*",
        # Bullet markers: •, -, *, –, —
        r"^\s*([•\*\-\–\—])\s+",
        # Legal recitals and formal headings:
        r"^\s*(WHEREAS|AND\s+WHEREAS|NOW,?\s+THEREFORE|PURSUANT\s+TO|TAKE\s+NOTICE|ORDER|CORAM|JUDGMENT|PRAYER|IN\s+WITNESS\s+WHEREOF|IN\s+THE\s+MATTER\s+OF|BETWEEN|AND|BEFORE\s+THE|DEAR\s+SIR|TO,):?\s*"
    ]

    def __init__(self):
        # Compile abbreviation replacement patterns for segmentation safety
        self._abbr_regex = re.compile(
            r"\b(" + "|".join(self.LEGAL_ABBREVIATIONS) + r")", re.IGNORECASE
        )

    def normalize(self, text: str) -> str:
        """
        Normalizes unicode characters, typography, quotes, and whitespace.
        """
        if not text:
            return ""

        # Normalize quotes and apostrophes
        text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
        # Normalize dashes
        text = text.replace("—", " - ").replace("–", " - ")
        # Non-breaking space to regular space
        text = text.replace("\u00a0", " ")
        # Replace Windows carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Collapse excessive blank lines to max 2
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def is_clause_boundary(self, line: str) -> Tuple[bool, str, str]:
        """
        Detects if a line starts with a legal clause marker or recital.
        Returns (is_boundary, prefix_marker, remaining_text).
        """
        line_clean = line.strip()
        for pat in self.CLAUSE_NUMBER_PATTERNS:
            m = re.match(pat, line_clean, flags=re.IGNORECASE)
            if m:
                marker = m.group(0).strip()
                remainder = line_clean[m.end():].strip()
                return True, marker, remainder
        return False, "", line_clean

    def segment_into_clauses(self, document_text: str) -> List[Dict[str, Any]]:
        """
        Segments a legal document into structured clause translation units.
        Each unit preserves its hierarchical numbering, title/type, and content.
        """
        normalized_doc = self.normalize(document_text)
        raw_paragraphs = [p.strip() for p in normalized_doc.split("\n\n") if p.strip()]

        clauses: List[Dict[str, Any]] = []
        clause_index = 1

        for para in raw_paragraphs:
            lines = [l.strip() for l in para.split("\n") if l.strip()]
            if not lines:
                continue

            # Check if paragraph has multiple sub-clauses (e.g. (i), (ii), etc.)
            current_clause_marker = ""
            current_buffer = []

            for line in lines:
                is_boundary, marker, remainder = self.is_clause_boundary(line)
                if is_boundary and current_buffer:
                    # Flush previous clause
                    clause_text = " ".join(current_buffer)
                    clauses.append(self._create_clause_dict(
                        clause_index, current_clause_marker, clause_text
                    ))
                    clause_index += 1
                    current_buffer = [line]
                    current_clause_marker = marker
                elif is_boundary:
                    current_clause_marker = marker
                    current_buffer.append(line)
                else:
                    current_buffer.append(line)

            if current_buffer:
                clause_text = " ".join(current_buffer)
                clauses.append(self._create_clause_dict(
                    clause_index, current_clause_marker, clause_text
                ))
                clause_index += 1

        return clauses

    def _create_clause_dict(self, index: int, marker: str, text: str) -> Dict[str, Any]:
        """Classifies clause type and structures the dictionary."""
        clause_type = "operative"
        text_upper = text.upper()

        if marker.startswith("WHEREAS") or "WHEREAS:" in text_upper:
            clause_type = "recital"
        elif "NOW, THEREFORE" in text_upper:
            clause_type = "transition_recital"
        elif any(w in text_upper for w in ["DEFINITIONS", "INTERPRETATION"]):
            clause_type = "definitions"
        elif any(w in text_upper for w in ["ORDER:", "CORAM:", "JUDGMENT"]):
            clause_type = "judicial_heading"
        elif any(w in text_upper for w in ["IN THE HIGH COURT", "IN THE SUPREME COURT", "MASTER SERVICES AGREEMENT"]):
            clause_type = "document_header"
        elif "INDEMNI" in text_upper:
            clause_type = "indemnity"
        elif "TERMINAT" in text_upper:
            clause_type = "termination"
        elif "GOVERNING LAW" in text_upper or "DISPUTE RESOLUTION" in text_upper or "ARBITRATION" in text_upper:
            clause_type = "dispute_resolution"
        elif "BAIL" in text_upper:
            clause_type = "bail_condition"

        return {
            "clause_id": f"C_{index:03d}",
            "clause_marker": marker,
            "clause_type": clause_type,
            "source_text": text,
            "word_count": len(text.split())
        }
