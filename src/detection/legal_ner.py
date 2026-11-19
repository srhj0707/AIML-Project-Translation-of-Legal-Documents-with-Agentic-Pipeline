import re
from typing import Dict, List, Any

class LegalEntityRecognizer:
    """
    Specialized Named Entity Recognizer for Indian legal documents and contracts.
    Extracts statutes, sections, case citations, dates, monetary amounts,
    party roles, and legal obligation modal verbs.
    """

    STATUTE_NAMES = [
        r"Code of Criminal Procedure(?:,\s*\d{4})?",
        r"Indian Penal Code(?:,\s*\d{4})?",
        r"Bharatiya Nagarik Suraksha Sanhita(?:,\s*\d{4})?",
        r"Bharatiya Nyaya Sanhita(?:,\s*\d{4})?",
        r"Bharatiya Sakshya Adhiniyam(?:,\s*\d{4})?",
        r"Indian Evidence Act(?:,\s*\d{4})?",
        r"Negotiable Instruments Act(?:,\s*\d{4})?",
        r"Arbitration and Conciliation Act(?:,\s*\d{4})?",
        r"Indian Contract Act(?:,\s*\d{4})?",
        r"Specific Relief Act(?:,\s*\d{4})?",
        r"Companies Act(?:,\s*\d{4})?",
        r"Constitution of India",
        r"Insolvency and Bankruptcy Code(?:,\s*\d{4})?",
        r"Prevention of Money Laundering Act(?:,\s*\d{4})?",
        r"Information Technology Act(?:,\s*\d{4})?"
    ]

    def __init__(self):
        # Compile patterns
        self.section_pattern = re.compile(
            r"\b(Sections?|Articles?)\s+(\d+[A-Z]?(?:\s*(?:,|and)\s*\d+[A-Z]?)*)",
            re.IGNORECASE
        )

        statute_union = "|".join(self.STATUTE_NAMES)
        self.statute_pattern = re.compile(rf"\b({statute_union})\b", re.IGNORECASE)

        self.citation_pattern = re.compile(
            r"\b((?:Criminal|Civil)\s+(?:Misc\.?\s+)?(?:Bail\s+Application|Appeal|Petition|Suit|Writ)\s+No\.?\s+\d+(?:\s*(?:of|/)\s*\d{4})?|"
            r"FIR\s+No\.?\s+\d+(?:\s*(?:of|/)\s*\d{4})?|"
            r"Case\s+Crime\s+No\.?\s+\d+(?:\s*(?:of|/)\s*\d{4})?|"
            r"AIR\s+\d{4}\s+SC\s+\d+|"
            r"\(\d{4}\)\s+\d+\s+SCC\s+\d+)",
            re.IGNORECASE
        )

        self.monetary_pattern = re.compile(
            r"((?:INR|Rs\.?|₹)\s*[\d,]+(?:\.\d+)?(?:/-)?|"
            r"(?:Rupees|Indian Rupees)\s+[A-Za-z\s]+only|"
            r"\d+(?:\.\d+)?%\s*(?:per annum)?)",
            re.IGNORECASE
        )

        self.date_pattern = re.compile(
            r"(\b\d{1,2}(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4}\b|"
            r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b|"
            r"\b(?:thirty|fifteen|twelve|sixty|forty-five|twenty-one)\s*\(\d+\)\s*(?:days|months|years)\b)",
            re.IGNORECASE
        )

        self.party_roles_pattern = re.compile(
            r"\b(Petitioner|Respondent|Appellant|Plaintiff|Defendant|Complainant|Accused|"
            r"Applicant|Deponent|Contractor|Company|Client|Service Provider|Sole Arbitrator)\b",
            re.IGNORECASE
        )

        self.modal_pattern = re.compile(
            r"\b(shall\s+not|shall|must\s+not|must|may\s+not|may|forthwith|hereby\s+restrained|directed\s+to|bound\s+to)\b",
            re.IGNORECASE
        )

        self.corporate_parties_pattern = re.compile(
            r"\b([A-Z][A-Za-z0-9\s&]+(?:Private Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|LLP))\b"
        )

    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extracts structured legal entities from a text string.
        Returns a dictionary categorizing detected entities with text and span positions.
        """
        entities: Dict[str, List[Dict[str, Any]]] = {
            "statutes": [],
            "sections": [],
            "citations": [],
            "monetary_amounts": [],
            "dates_and_periods": [],
            "parties": [],
            "corporate_entities": [],
            "legal_modals": []
        }

        # Sections & Articles
        for m in self.section_pattern.finditer(text):
            entities["sections"].append({
                "text": m.group(0),
                "type": "section_or_article",
                "start": m.start(),
                "end": m.end()
            })

        # Statutes
        for m in self.statute_pattern.finditer(text):
            entities["statutes"].append({
                "text": m.group(0),
                "type": "statute",
                "start": m.start(),
                "end": m.end()
            })

        # Case Citations & FIRs
        for m in self.citation_pattern.finditer(text):
            entities["citations"].append({
                "text": m.group(0),
                "type": "case_citation",
                "start": m.start(),
                "end": m.end()
            })

        # Monetary Amounts
        for m in self.monetary_pattern.finditer(text):
            entities["monetary_amounts"].append({
                "text": m.group(0).strip(),
                "type": "monetary_amount",
                "start": m.start(),
                "end": m.end()
            })

        # Dates & Timeframes
        for m in self.date_pattern.finditer(text):
            entities["dates_and_periods"].append({
                "text": m.group(0).strip(),
                "type": "temporal_entity",
                "start": m.start(),
                "end": m.end()
            })

        # Party Roles
        for m in self.party_roles_pattern.finditer(text):
            val = m.group(0).strip()
            # Avoid duplicate overlapping
            if not any(e["text"].lower() == val.lower() for e in entities["parties"]):
                entities["parties"].append({
                    "text": val,
                    "type": "legal_party_role",
                    "start": m.start(),
                    "end": m.end()
                })

        # Corporate entities
        for m in self.corporate_parties_pattern.finditer(text):
            val = m.group(0).strip()
            if not any(e["text"] == val for e in entities["corporate_entities"]):
                entities["corporate_entities"].append({
                    "text": val,
                    "type": "corporate_party_name",
                    "start": m.start(),
                    "end": m.end()
                })

        # Legal Modals
        for m in self.modal_pattern.finditer(text):
            entities["legal_modals"].append({
                "text": m.group(0).lower(),
                "type": "modal_obligation",
                "start": m.start(),
                "end": m.end()
            })

        return entities

    def get_critical_entity_strings(self, text: str) -> List[str]:
        """
        Extracts a flat list of critical string values (numbers, amounts, citations, sections)
        that MUST be rigorously preserved during translation and validation.
        """
        extracted = self.extract_entities(text)
        critical = []
        for cat in ["sections", "statutes", "citations", "monetary_amounts", "dates_and_periods"]:
            for item in extracted[cat]:
                critical.append(item["text"])
        return sorted(list(set(critical)))
