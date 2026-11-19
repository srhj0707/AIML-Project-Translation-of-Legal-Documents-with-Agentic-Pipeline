import re
from typing import Dict, Any

class LegalLanguageDetector:
    """
    Detects language, script purity, and code-mixing in legal documents.
    Distinguishes between English (Latin script) and Hindi (Devanagari script),
    flagging mixed or transliterated legal passages.
    """

    DEVANAGARI_REGEX = re.compile(r"[\u0900-\u097F]")
    LATIN_REGEX = re.compile(r"[a-zA-Z]")

    def detect(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {
                "primary_language": "unknown",
                "script": "unknown",
                "confidence": 0.0,
                "is_english": False,
                "is_hindi": False,
                "is_mixed": False,
                "devanagari_ratio": 0.0,
                "latin_ratio": 0.0
            }

        devanagari_chars = len(self.DEVANAGARI_REGEX.findall(text))
        latin_chars = len(self.LATIN_REGEX.findall(text))
        total_letters = devanagari_chars + latin_chars

        if total_letters == 0:
            # Only punctuation or numbers
            return {
                "primary_language": "neutral",
                "script": "neutral",
                "confidence": 1.0,
                "is_english": True,
                "is_hindi": False,
                "is_mixed": False,
                "devanagari_ratio": 0.0,
                "latin_ratio": 0.0
            }

        dev_ratio = devanagari_chars / total_letters
        latin_ratio = latin_chars / total_letters

        is_mixed = (dev_ratio > 0.15 and latin_ratio > 0.15)

        if dev_ratio > latin_ratio:
            primary_lang = "hi"
            script = "Devanagari"
            confidence = round(dev_ratio, 4)
            is_hindi = True
            is_english = False
        else:
            primary_lang = "en"
            script = "Latin"
            confidence = round(latin_ratio, 4)
            is_hindi = False
            is_english = True

        return {
            "primary_language": primary_lang,
            "script": script,
            "confidence": confidence,
            "is_english": is_english,
            "is_hindi": is_hindi,
            "is_mixed": is_mixed,
            "devanagari_ratio": round(dev_ratio, 4),
            "latin_ratio": round(latin_ratio, 4),
            "devanagari_char_count": devanagari_chars,
            "latin_char_count": latin_chars
        }
