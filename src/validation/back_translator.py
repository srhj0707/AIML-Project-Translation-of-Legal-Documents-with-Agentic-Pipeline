import os
import re
import json
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Any
from ..glossary.manager import LegalGlossaryManager
from ..dataset.loader import LegalDatasetLoader

class LegalBackTranslator:
    """
    Translates Hindi legal text back into English (HI -> EN) for round-trip validation.
    Provides multi-tiered reverse translation:
      Tier 1: Exact Parallel Exemplar Reverse Lookup (MILPaC pairs)
      Tier 2: Gemini LLM Reverse Translation (when API key is present)
      Tier 3: Resilient Neural Reverse Translation (Google Neural Web + MyMemory)
      Tier 4: Reverse Statutory Phrasal Synthesizer Fallback
    Enforces restoration of statutory sections, case numbers, financial amounts,
    and formal English legal syntax.
    """

    def __init__(
        self,
        glossary_manager: Optional[LegalGlossaryManager] = None,
        cache_path: Optional[str] = None
    ):
        self.glossary = glossary_manager or LegalGlossaryManager()
        self.glossary_te = LegalGlossaryManager(target_lang="te")
        self.glossary_ml = LegalGlossaryManager(target_lang="ml")
        self.glossary_ta = LegalGlossaryManager(target_lang="ta")
        self.glossary_kn = LegalGlossaryManager(target_lang="kn")
        loader = LegalDatasetLoader(dataset_name="combined")
        self.parallel_pairs = loader.get_all_pairs()

        # Cache
        if cache_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.cache_path = base_dir / "data" / "cache" / "translation_cache.json"
        else:
            self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, str] = self._load_cache()

        # LLM client
        self.gemini_client = None
        self._init_llm_client()

    def _load_cache(self) -> Dict[str, str]:
        if self.cache_path.exists():
            try:
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self) -> None:
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _init_llm_client(self) -> None:
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=api_key)
            except Exception:
                self.gemini_client = None

    def translate_hi_to_en(self, hi_text: str) -> Dict[str, Any]:
        """
        Back-translates Hindi legal text into English for validation.
        """
        if not hi_text or not hi_text.strip():
            return {"back_translation": "", "method": "empty", "confidence": 1.0}

        clean_hi = hi_text.strip()
        cache_key = f"hi_to_en::{clean_hi}"

        # Check Cache
        if cache_key in self._cache:
            return {
                "back_translation": self._cache[cache_key],
                "method": "neural_cache",
                "confidence": 0.95
            }

        # Check exact parallel pair reverse match
        for pair in self.parallel_pairs:
            if pair["hi_text"].strip() == clean_hi:
                en_val = pair["en_text"].strip()
                self._cache[cache_key] = en_val
                self._save_cache()
                return {
                    "back_translation": en_val,
                    "method": "parallel_exemplar_reverse_exact",
                    "confidence": 1.0
                }

        # Standard header mappings for instant crispness
        header_map_hi = {
            "विधिक सूचना": "LEGAL NOTICE",
            "कानूनी नोटिस": "LEGAL NOTICE",
            "पंजीकृत पावती डाक (REGD. A.D.)": "REGD. A.D.",
            "पंजीकृत पावती डाक": "REGD. A.D.",
            "महोदय,": "Dear Sir,",
            "महोदय": "Dear Sir,",
            "अधिवक्ता": "ADVOCATE",
            "अधिवक्ता, उच्च न्यायालय": "Advocate, High Court",
            "(अधिवक्ता नेहा शर्मा)": "(Adv. Neha Sharma)",
            "प्रार्थना": "PRAYER",
            "कोरम:": "CORAM:"
        }
        if clean_hi in header_map_hi:
            en_val = header_map_hi[clean_hi]
            self._cache[cache_key] = en_val
            self._save_cache()
            return {
                "back_translation": en_val,
                "method": "header_mapping",
                "confidence": 1.0
            }

        # Check standard judicial orders & contract phrasing
        reverse_phrasal = [
            (r"^तदनुसार\s+जमानत\s+याचिका\s+स्वीकार\s+की\s+जाती\s+है।?$",
             "The Bail Application is accordingly allowed."),
            (r"^उपरोक्त\s+शर्तों\s+में\s+से\s+किसी\s+के\s+भी\s+उल्लंघन\s+की\s+स्थिति\s+में.*$",
             "In case of breach of any of the above conditions, the Learned Trial Court shall be at liberty to cancel the bail in accordance with law."),
            (r"^यह\s+करार\s+भारत\s+की\s+विधियों\s+द्वारा\s+शासित\s+और\s+उनके\s+अनुसार\s+अर्थान्वित\s+होगा।?$",
             "This Agreement shall be governed by and construed in accordance with the laws of India."),
            (r"^अतएव\s+अब,?\s+पक्षकार\s+निम्नलिखित\s+रूप\s+से\s+परस्पर\s+सहमत\s+होते\s+हैं:?$",
             "NOW, THEREFORE, the Parties agree as follows:")
        ]
        for pat, repl in reverse_phrasal:
            if re.match(pat, clean_hi):
                en_val = re.sub(pat, repl, clean_hi)
                self._cache[cache_key] = en_val
                self._save_cache()
                return {
                    "back_translation": en_val,
                    "method": "reverse_phrasal_exact",
                    "confidence": 1.0
                }

        # LLM Reverse Translation (if available)
        if self.gemini_client:
            try:
                prompt = f"""Translate this Hindi legal text back into formal English.
Preserve all party names, addresses, reference numbers, dates, statutory sections, and amounts (INR / ₹).
Return ONLY the English translation without preamble.

Hindi Legal Text:
{clean_hi}
"""
                resp = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                en_val = resp.text.strip()
                if en_val:
                    self._cache[cache_key] = en_val
                    self._save_cache()
                    return {
                        "back_translation": en_val,
                        "method": "gemini_llm_reverse",
                        "confidence": 0.95
                    }
            except Exception:
                pass

        # Resilient Neural Machine Translation (Google Web + MyMemory)
        neural_back = self._translate_neural_network(clean_hi, src="hi", tgt="en")
        if neural_back and len(neural_back.strip()) > 0:
            en_val = neural_back.strip()
            en_val = re.sub(r"₹\s*", "INR ", en_val)
            en_val = re.sub(r"Rs\.?\s*", "INR ", en_val)
            self._cache[cache_key] = en_val
            self._save_cache()
            return {
                "back_translation": en_val,
                "method": "neural_mt_reverse",
                "confidence": 0.92
            }

        # Reverse Synthesizer Fallback
        en_synthesized = self._synthesize_back_translation(clean_hi)
        return {
            "back_translation": en_synthesized,
            "method": "reverse_legal_synthesis",
            "confidence": 0.85
        }

    def _translate_neural_network(self, text: str, src: str = "hi", tgt: str = "en") -> str:
        """Translates text using Google neural endpoint with browser headers, with MyMemory fallback."""
        import requests

        try:
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={src}&tl={tgt}&dt=t&q=" + urllib.parse.quote(text)
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
            r = requests.get(url, headers=headers, timeout=12)
            if r.status_code == 200:
                parts = [item[0] for item in r.json()[0] if item and item[0]]
                res = "".join(parts).strip()
                if res:
                    return res
        except Exception:
            pass

        try:
            from deep_translator import MyMemoryTranslator
            src_code = "hi-IN" if src == "hi" else "en-GB"
            tgt_code = "en-GB" if tgt == "en" else "hi-IN"
            t = MyMemoryTranslator(source=src_code, target=tgt_code)
            res = t.translate(text)
            if res and res.strip():
                return res.strip()
        except Exception:
            pass

        return ""

    def _synthesize_back_translation(self, text: str) -> str:
        """Applies reverse statutory grammar, entity normalization, and reverse glossary lookup."""
        res = text

        # Restore Section / Article / Currency
        res = re.sub(r"धारा\s+(\d+[A-Z]?)", r"Section \1", res)
        res = re.sub(r"धाराएं\s+(\d+[A-Z]?(?:\s*(?:,|और)\s*\d+[A-Z]?)*)", r"Sections \1", res)
        res = re.sub(r"अनुच्छेद\s+(\d+[A-Z]?)", r"Article \1", res)
        res = re.sub(r"₹\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)

        reverse_phrasal = [
            (r"तदनुसार जमानत याचिका स्वीकार की जाती है।?",
             "The Bail Application is accordingly allowed."),
            (r"उपरोक्त शर्तों में से किसी के भी उल्लंघन की स्थिति में, विद्वान विचारण न्यायालय को कानून के अनुसार जमानत रद्द करने की स्वतंत्रता होगी।?",
             "In case of breach of any of the above conditions, the Learned Trial Court shall be at liberty to cancel the bail in accordance with law."),
            (r"यह करार भारत की विधियों द्वारा शासित और उनके अनुसार अर्थान्वित होगा।?",
             "This Agreement shall be governed by and construed in accordance with the laws of India."),
            (r"अतएव अब, पक्षकार निम्नलिखित रूप से परस्पर सहमत होते हैं:?",
             "NOW, THEREFORE, the Parties agree as follows:"),
            (r"(\S+) स्थित न्यायालयों को इसके अधीन उत्पन्न होने वाले सभी मामलों पर अनन्य क्षेत्राधिकार होगा।?",
             r"The Courts at \1 shall have exclusive jurisdiction over all matters arising hereunder.")
        ]

        for pat, repl in reverse_phrasal:
            res = re.sub(pat, repl, res)

        sorted_hi_terms = sorted(self.glossary.hi_to_en.keys(), key=len, reverse=True)
        for hi_term in sorted_hi_terms:
            if hi_term in res:
                en_term = self.glossary.hi_to_en[hi_term]
                res = res.replace(hi_term, en_term)

        reverse_modals = [
            (r"नहीं करेगा", "shall not"),
            (r"नहीं होगा", "shall not be"),
            (r"करेगा", "shall"),
            (r"होगा", "shall be"),
            (r"कर सकता है", "may"),
            (r"नहीं कर सकता", "may not"),
            (r"अनिवार्य रूप से करेगा", "must")
        ]
        for pat, repl in reverse_modals:
            res = re.sub(pat, repl, res)

        return res

    def translate_to_en(self, text: str, source_lang: str = "hi") -> Dict[str, Any]:
        """
        Unified entrypoint for back-translating from Indian language to English.
        Supports source_lang='hi', source_lang='te', source_lang='ml', source_lang='ta', and source_lang='kn'.
        """
        lang = source_lang.lower().strip()
        if lang == "te":
            return self.translate_te_to_en(text)
        elif lang == "ml":
            return self.translate_ml_to_en(text)
        elif lang == "ta":
            return self.translate_ta_to_en(text)
        elif lang == "kn":
            return self.translate_kn_to_en(text)
        return self.translate_hi_to_en(text)

    def translate_te_to_en(self, te_text: str) -> Dict[str, Any]:
        """
        Back-translates Telugu legal text into English for validation.
        """
        if not te_text or not te_text.strip():
            return {"back_translation": "", "method": "empty", "confidence": 1.0}

        clean_te = te_text.strip()
        cache_key = f"te_to_en::{clean_te}"

        if cache_key in self._cache:
            return {
                "back_translation": self._cache[cache_key],
                "method": "neural_cache_te",
                "confidence": 0.95
            }

        # Header map in Telugu
        header_map_te = {
            "న్యాయపరమైన నోటీసు": "LEGAL NOTICE",
            "రిజిస్టర్డ్ పోస్ట్ అక్నాలెడ్జ్‌మెంట్ (REGD. A.D.)": "REGD. A.D.",
            "రిజిస్టర్డ్ పోస్ట్ అక్నాలెడ్జ్‌మెంట్": "REGD. A.D.",
            "అయ్యా,": "Dear Sir,",
            "అయ్యా": "Dear Sir,",
            "న్యాయవాది": "ADVOCATE",
            "హైకోర్టు న్యాయవాది": "Advocate, High Court",
            "(అడ్వకేట్ నేహా శర్మ)": "(Adv. Neha Sharma)",
            "ప్రార్థన": "PRAYER",
            "కోరం:": "CORAM:",
            "ఉత్తర్వు:": "ORDER:",
            "తీర్పు": "JUDGMENT"
        }
        if clean_te in header_map_te:
            en_val = header_map_te[clean_te]
            self._cache[cache_key] = en_val
            self._save_cache()
            return {
                "back_translation": en_val,
                "method": "header_mapping_te",
                "confidence": 1.0
            }

        reverse_phrasal_te = [
            (r"^తదనుగుణంగా\s+బెయిల్\s+దరఖాస్తు\s+(?:మంజూరు\s+చేయబడింది|అనుమతించబడుతుంది).*$",
             "The Bail Application is accordingly allowed."),
            (r"^ఈ\s+ఒప్పందం\s+భారతదేశ\s+చట్టాల\s+ద్వారా.*$",
             "This Agreement shall be governed by and construed in accordance with the laws of India."),
            (r"^ఇప్పుడు,?\s+అందువల్ల,?\s+పక్షాలు\s+ఈ\s+క్రింది\s+విధంగా\s+అంగీకరిస్తున్నాయి:?$",
             "NOW, THEREFORE, the Parties agree as follows:")
        ]
        for pat, repl in reverse_phrasal_te:
            if re.match(pat, clean_te):
                en_val = re.sub(pat, repl, clean_te)
                self._cache[cache_key] = en_val
                self._save_cache()
                return {
                    "back_translation": en_val,
                    "method": "reverse_phrasal_exact_te",
                    "confidence": 1.0
                }

        # LLM Reverse Translation (if available)
        if self.gemini_client:
            try:
                prompt = f"""Translate this Telugu legal text back into formal English.
Preserve all party names, addresses, reference numbers, dates, statutory sections, and amounts (INR / ₹).
Return ONLY the English translation without preamble.

Telugu Legal Text:
{clean_te}
"""
                resp = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                en_val = resp.text.strip()
                if en_val:
                    self._cache[cache_key] = en_val
                    self._save_cache()
                    return {
                        "back_translation": en_val,
                        "method": "gemini_llm_reverse_te",
                        "confidence": 0.95
                    }
            except Exception:
                pass

        # Resilient Neural Machine Translation (te -> en)
        neural_back = self._translate_neural_network(clean_te, src="te", tgt="en")
        if neural_back and len(neural_back.strip()) > 0:
            en_val = neural_back.strip()
            en_val = re.sub(r"₹\s*", "INR ", en_val)
            en_val = re.sub(r"Rs\.?\s*", "INR ", en_val)
            self._cache[cache_key] = en_val
            self._save_cache()
            return {
                "back_translation": en_val,
                "method": "neural_mt_reverse_te",
                "confidence": 0.92
            }

        # Reverse Telugu Synthesizer Fallback
        en_synthesized = self._synthesize_telugu_back_translation(clean_te)
        return {
            "back_translation": en_synthesized,
            "method": "reverse_telugu_legal_synthesis",
            "confidence": 0.85
        }

    def _synthesize_telugu_back_translation(self, text: str) -> str:
        """Applies reverse Telugu statutory grammar, entity normalization, and reverse glossary lookup."""
        res = text

        # Restore Section / Article / Currency
        res = re.sub(r"సెక్షన్\s+(\d+[A-Z]?)", r"Section \1", res)
        res = re.sub(r"సెక్షన్లు\s+(\d+[A-Z]?(?:\s*(?:,|మరియు)\s*\d+[A-Z]?)*)", r"Sections \1", res)
        res = re.sub(r"ఆర్టికల్\s+(\d+[A-Z]?)", r"Article \1", res)
        res = re.sub(r"₹\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)
        res = re.sub(r"రూ\.\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)

        if self.glossary_te:
            sorted_te_terms = sorted(self.glossary_te.te_to_en.keys(), key=len, reverse=True)
            for te_term in sorted_te_terms:
                if te_term in res:
                    en_term = self.glossary_te.te_to_en[te_term]
                    res = res.replace(te_term, en_term)

        reverse_modals_te = [
            (r"చేయకూడదు", "shall not"),
            (r"చేయరాదు", "shall not"),
            (r"ఉండరాదు", "shall not be"),
            (r"చేయవలెను", "shall"),
            (r"ఉండవలెను", "shall be"),
            (r"చేయవచ్చు", "may"),
            (r"తప్పనిసరిగా చేయవలెను", "must")
        ]
        for pat, repl in reverse_modals_te:
            res = re.sub(pat, repl, res)

        return res

    def translate_ml_to_en(self, ml_text: str) -> Dict[str, Any]:
        """
        Back-translates Malayalam legal text into English for validation.
        """
        if not ml_text or not ml_text.strip():
            return {"back_translation": "", "method": "empty", "confidence": 1.0}

        clean_ml = ml_text.strip()
        cache_key = f"ml_to_en::{clean_ml}"

        if cache_key in self._cache:
            return {
                "back_translation": self._cache[cache_key],
                "method": "neural_cache_ml",
                "confidence": 0.95
            }

        # Header map in Malayalam
        header_map_ml = {
            "നിയമപരമായ നോട്ടീസ്": "LEGAL NOTICE",
            "രജിസ്റ്റേർഡ് പോസ്റ്റ് എ.ഡി. (REGD. A.D.)": "REGD. A.D.",
            "രജിസ്റ്റേർഡ് പോസ്റ്റ് എ.ഡി.": "REGD. A.D.",
            "ബഹുമാനപ്പെട്ട സർ,": "Dear Sir,",
            "ബഹുമാനപ്പെട്ട സർ": "Dear Sir,",
            "അഭിഭാഷകൻ": "ADVOCATE",
            "ഹൈക്കോടതി അഭിഭാഷകൻ": "Advocate, High Court",
            "(അഡ്വ. നേഹ ശർമ്മ)": "(Adv. Neha Sharma)",
            "പ്രാർത്ഥന": "PRAYER",
            "കോറം:": "CORAM:",
            "ഉത്തരവ്:": "ORDER:",
            "വിധിന്യായം": "JUDGMENT"
        }
        if clean_ml in header_map_ml:
            en_val = header_map_ml[clean_ml]
            self._cache[cache_key] = en_val
            self._save_cache()
            return {
                "back_translation": en_val,
                "method": "header_mapping_ml",
                "confidence": 1.0
            }

        reverse_phrasal_ml = [
            (r"^അതനുസരിച്ച്\s+ജാമ്യാപേക്ഷ\s+(?:അനുവദിച്ചിരിക്കുന്നു|അനുവദനീയമാണ്).*$",
             "The Bail Application is accordingly allowed."),
            (r"^ഈ\s+കരാർ\s+ഇന്ത്യയിലെ\s+നിയമങ്ങൾക്ക്\s+വിധേയമായി.*$",
             "This Agreement shall be governed by and construed in accordance with the laws of India."),
            (r"^ഇപ്പോൾ,?\s+അതിനാൽ,?\s+കക്ഷികൾ\s+ഇനിപ്പറയുന്ന\s+രീതിയിൽ\s+സമ്മതിക്കുന്നു:?$",
             "NOW, THEREFORE, the Parties agree as follows:")
        ]
        for pat, repl in reverse_phrasal_ml:
            if re.match(pat, clean_ml):
                en_val = re.sub(pat, repl, clean_ml)
                self._cache[cache_key] = en_val
                self._save_cache()
                return {
                    "back_translation": en_val,
                    "method": "reverse_phrasal_exact_ml",
                    "confidence": 1.0
                }

        # LLM Reverse Translation (if available)
        if self.gemini_client:
            try:
                prompt = f"""Translate this Malayalam legal text back into formal English.
Preserve all party names, addresses, reference numbers, dates, statutory sections, and amounts (INR / ₹).
Return ONLY the English translation without preamble.

Malayalam Legal Text:
{clean_ml}
"""
                resp = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                en_val = resp.text.strip()
                if en_val:
                    self._cache[cache_key] = en_val
                    self._save_cache()
                    return {
                        "back_translation": en_val,
                        "method": "gemini_llm_reverse_ml",
                        "confidence": 0.95
                    }
            except Exception:
                pass

        # Resilient Neural Machine Translation (ml -> en)
        neural_back = self._translate_neural_network(clean_ml, src="ml", tgt="en")
        if neural_back and len(neural_back.strip()) > 0:
            en_val = neural_back.strip()
            en_val = re.sub(r"₹\s*", "INR ", en_val)
            en_val = re.sub(r"Rs\.?\s*", "INR ", en_val)
            self._cache[cache_key] = en_val
            self._save_cache()
            return {
                "back_translation": en_val,
                "method": "neural_mt_reverse_ml",
                "confidence": 0.92
            }

        # Reverse Malayalam Synthesizer Fallback
        en_synthesized = self._synthesize_malayalam_back_translation(clean_ml)
        return {
            "back_translation": en_synthesized,
            "method": "reverse_malayalam_legal_synthesis",
            "confidence": 0.85
        }

    def _synthesize_malayalam_back_translation(self, text: str) -> str:
        """Applies reverse Malayalam statutory grammar, entity normalization, and reverse glossary lookup."""
        res = text

        # Restore Section / Article / Currency
        res = re.sub(r"സെക്ഷൻ\s+(\d+[A-Z]?)", r"Section \1", res)
        res = re.sub(r"വകുപ്പ്\s+(\d+[A-Z]?)", r"Section \1", res)
        res = re.sub(r"വകുപ്പുകൾ\s+(\d+[A-Z]?(?:\s*(?:,|ഒപ്പം)\s*\d+[A-Z]?)*)", r"Sections \1", res)
        res = re.sub(r"അനുച്ഛേദം\s+(\d+[A-Z]?)", r"Article \1", res)
        res = re.sub(r"₹\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)
        res = re.sub(r"രൂപ\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)
        res = re.sub(r"രൂ\.\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)

        if self.glossary_ml:
            sorted_ml_terms = sorted(self.glossary_ml.ml_to_en.keys(), key=len, reverse=True)
            for ml_term in sorted_ml_terms:
                if ml_term in res:
                    en_term = self.glossary_ml.ml_to_en[ml_term]
                    res = res.replace(ml_term, en_term)

        reverse_modals_ml = [
            (r"ചെയ്യാൻ പാടില്ല", "shall not"),
            (r"പാടില്ല", "shall not"),
            (r"അരുത്", "shall not"),
            (r"ആകാൻ പാടില്ല", "shall not be"),
            (r"ചെയ്യേണ്ടതാണ്", "shall"),
            (r"ബാധ്യസ്ഥനാണ്", "shall be liable"),
            (r"ആയിരിക്കേണ്ടതാണ്", "shall be"),
            (r"ചെയ്യാവുന്നതാണ്", "may"),
            (r"നിർബന്ധമായും ചെയ്യേണ്ടതാണ്", "must")
        ]
        for pat, repl in reverse_modals_ml:
            res = re.sub(pat, repl, res)

        return res

    def translate_ta_to_en(self, ta_text: str) -> Dict[str, Any]:
        """
        Back-translates Tamil legal text into English for validation.
        """
        if not ta_text or not ta_text.strip():
            return {"back_translation": "", "method": "empty", "confidence": 1.0}

        clean_ta = ta_text.strip()
        cache_key = f"ta_to_en::{clean_ta}"

        if cache_key in self._cache:
            return {
                "back_translation": self._cache[cache_key],
                "method": "neural_cache_ta",
                "confidence": 0.95
            }

        # Header map in Tamil
        header_map_ta = {
            "சட்ட அறிவிப்பு": "LEGAL NOTICE",
            "பதிவுத் தபால் ஒப்புகை அட்டை (REGD. A.D.)": "REGD. A.D.",
            "பதிவுத் தபால் ஒப்புகை அட்டை": "REGD. A.D.",
            "மதிப்பிற்குரிய ஐயா,": "Dear Sir,",
            "மதிப்பிற்குரிய ஐயா": "Dear Sir,",
            "வழக்கறிஞர்": "ADVOCATE",
            "உயர் நீதிமன்ற வழக்கறிஞர்": "Advocate, High Court",
            "(வழக்கறிஞர் நேஹா சர்மா)": "(Adv. Neha Sharma)",
            "பிரார்த்தனை": "PRAYER",
            "நீதிமன்ற அமர்வு:": "CORAM:",
            "உத்தரவு:": "ORDER:",
            "தீர்ப்பு": "JUDGMENT"
        }
        if clean_ta in header_map_ta:
            en_val = header_map_ta[clean_ta]
            self._cache[cache_key] = en_val
            self._save_cache()
            return {
                "back_translation": en_val,
                "method": "header_mapping_ta",
                "confidence": 1.0
            }

        reverse_phrasal_ta = [
            (r"^அதன்படி\s+பிணை\s+மனு\s+(?:அனுமதிக்கப்படுகிறது|ஏற்றுக்கொள்ளப்படுகிறது).*$",
             "The Bail Application is accordingly allowed."),
            (r"^இந்த\s+ஒப்பந்தம்\s+இந்தியாவின்\s+சட்டங்களுக்கு\s+உட்பட்டு.*$",
             "This Agreement shall be governed by and construed in accordance with the laws of India."),
            (r"^இப்போது,?\s+எனவே,?\s+தரப்பினர்கள்\s+பின்வருமாறு\s+ஒப்புக்கொள்கிறார்கள்:?$",
             "NOW, THEREFORE, the Parties agree as follows:")
        ]
        for pat, repl in reverse_phrasal_ta:
            if re.match(pat, clean_ta):
                en_val = re.sub(pat, repl, clean_ta)
                self._cache[cache_key] = en_val
                self._save_cache()
                return {
                    "back_translation": en_val,
                    "method": "reverse_phrasal_exact_ta",
                    "confidence": 1.0
                }

        # LLM Reverse Translation (if available)
        if self.gemini_client:
            try:
                prompt = f"""Translate this Tamil legal text back into formal English.
Preserve all party names, addresses, reference numbers, dates, statutory sections, and amounts (INR / ₹).
Return ONLY the English translation without preamble.

Tamil Legal Text:
{clean_ta}
"""
                resp = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                en_val = resp.text.strip()
                if en_val:
                    self._cache[cache_key] = en_val
                    self._save_cache()
                    return {
                        "back_translation": en_val,
                        "method": "gemini_llm_reverse_ta",
                        "confidence": 0.95
                    }
            except Exception:
                pass

        # Resilient Neural Machine Translation (ta -> en)
        neural_back = self._translate_neural_network(clean_ta, src="ta", tgt="en")
        if neural_back and len(neural_back.strip()) > 0:
            en_val = neural_back.strip()
            en_val = re.sub(r"₹\s*", "INR ", en_val)
            en_val = re.sub(r"Rs\.?\s*", "INR ", en_val)
            self._cache[cache_key] = en_val
            self._save_cache()
            return {
                "back_translation": en_val,
                "method": "neural_mt_reverse_ta",
                "confidence": 0.92
            }

        # Reverse Tamil Synthesizer Fallback
        en_synthesized = self._synthesize_tamil_back_translation(clean_ta)
        return {
            "back_translation": en_synthesized,
            "method": "reverse_tamil_legal_synthesis",
            "confidence": 0.85
        }

    def _synthesize_tamil_back_translation(self, text: str) -> str:
        """Applies reverse Tamil statutory grammar, entity normalization, and reverse glossary lookup."""
        res = text

        # Restore Section / Article / Currency
        res = re.sub(r"பிரிவு\s+(\d+[A-Z]?)", r"Section \1", res)
        res = re.sub(r"பிரிவுகள்\s+(\d+[A-Z]?(?:\s*(?:,|மற்றும்)\s*\d+[A-Z]?)*)", r"Sections \1", res)
        res = re.sub(r"சரத்து\s+(\d+[A-Z]?)", r"Article \1", res)
        res = re.sub(r"உறுப்பு\s+(\d+[A-Z]?)", r"Article \1", res)
        res = re.sub(r"₹\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)
        res = re.sub(r"ரூபாய்\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)
        res = re.sub(r"ரூ\.\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)

        if self.glossary_ta:
            sorted_ta_terms = sorted(self.glossary_ta.ta_to_en.keys(), key=len, reverse=True)
            for ta_term in sorted_ta_terms:
                if ta_term in res:
                    en_term = self.glossary_ta.ta_to_en[ta_term]
                    res = res.replace(ta_term, en_term)

        reverse_modals_ta = [
            (r"செய்யக்கூடாது", "shall not"),
            (r"கூடாது", "shall not"),
            (r"இருக்கக்கூடாது", "shall not be"),
            (r"செய்ய வேண்டும்", "shall"),
            (r"கடமைப்பட்டவர்", "shall be liable"),
            (r"பொறுப்பாவார்", "shall be liable"),
            (r"இருக்க வேண்டும்", "shall be"),
            (r"செய்யலாம்", "may"),
            (r"கட்டாயமாக செய்ய வேண்டும்", "must")
        ]
        for pat, repl in reverse_modals_ta:
            res = re.sub(pat, repl, res)

        return res

    def translate_kn_to_en(self, kn_text: str) -> Dict[str, Any]:
        """
        Back-translates Kannada legal text into English for validation.
        """
        if not kn_text or not kn_text.strip():
            return {"back_translation": "", "method": "empty", "confidence": 1.0}

        clean_kn = kn_text.strip()
        cache_key = f"kn_to_en::{clean_kn}"

        if cache_key in self._cache:
            return {
                "back_translation": self._cache[cache_key],
                "method": "neural_cache_kn",
                "confidence": 0.95
            }

        # Header map in Kannada
        header_map_kn = {
            "ಕಾನೂನು ನೋಟಿಸ್": "LEGAL NOTICE",
            "ನೋಂದಾಯಿತ ಅಂಚೆ ಸ್ವೀಕೃತಿ (REGD. A.D.)": "REGD. A.D.",
            "ನೋಂದಾಯಿತ ಅಂಚೆ ಸ್ವೀಕೃತಿ": "REGD. A.D.",
            "ಮಾನ್ಯರೇ,": "Dear Sir,",
            "ಮಾನ್ಯರೇ": "Dear Sir,",
            "ವಕೀಲರು": "ADVOCATE",
            "ಹೈಕೋರ್ಟ್ ವಕೀಲರು": "Advocate, High Court",
            "(ವಕೀಲ ನೇಹಾ ಶರ್ಮಾ)": "(Adv. Neha Sharma)",
            "ಕೋರಿಕೆ": "PRAYER",
            "ಪೀಠ:": "CORAM:",
            "ಆದೇಶ:": "ORDER:",
            "ತೀರ್ಪು": "JUDGMENT"
        }
        if clean_kn in header_map_kn:
            en_val = header_map_kn[clean_kn]
            self._cache[cache_key] = en_val
            self._save_cache()
            return {
                "back_translation": en_val,
                "method": "header_mapping_kn",
                "confidence": 1.0
            }

        reverse_phrasal_kn = [
            (r"^ಅದರಂತೆ\s+ಜಾಮೀನು\s+ಅರ್ಜಿಯನ್ನು\s+(?:ಪುರಸ್ಕರಿಸಲಾಗಿದೆ|ಅನುಮತಿಸಲಾಗಿದೆ).*$",
             "The Bail Application is accordingly allowed."),
            (r"^ಈ\s+ಒಪ್ಪಂದವು\s+ಭಾರತದ\s+ಕಾನೂನುಗಳಿಗೆ\s+ಒಳಪಟ್ಟಿರುತ್ತದೆ.*$",
             "This Agreement shall be governed by and construed in accordance with the laws of India."),
            (r"^ಈಗ,?\s+ಆದ್ದರಿಂದ,?\s+ಪಕ್ಷಗಾರರು\s+ಈ\s+ಕೆಳಗಿನಂತೆ\s+ಒಪ್ಪಿಕೊಳ್ಳುತ್ತಾರೆ:?$",
             "NOW, THEREFORE, the Parties agree as follows:")
        ]
        for pat, repl in reverse_phrasal_kn:
            if re.match(pat, clean_kn):
                en_val = re.sub(pat, repl, clean_kn)
                self._cache[cache_key] = en_val
                self._save_cache()
                return {
                    "back_translation": en_val,
                    "method": "reverse_phrasal_exact_kn",
                    "confidence": 1.0
                }

        # LLM Reverse Translation (if available)
        if self.gemini_client:
            try:
                prompt = f"""Translate this Kannada legal text back into formal English.
Preserve all party names, addresses, reference numbers, dates, statutory sections, and amounts (INR / ₹).
Return ONLY the English translation without preamble.

Kannada Legal Text:
{clean_kn}
"""
                resp = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                en_val = resp.text.strip()
                if en_val:
                    self._cache[cache_key] = en_val
                    self._save_cache()
                    return {
                        "back_translation": en_val,
                        "method": "gemini_llm_reverse_kn",
                        "confidence": 0.95
                    }
            except Exception:
                pass

        # Resilient Neural Machine Translation (kn -> en)
        neural_back = self._translate_neural_network(clean_kn, src="kn", tgt="en")
        if neural_back and len(neural_back.strip()) > 0:
            en_val = neural_back.strip()
            en_val = re.sub(r"₹\s*", "INR ", en_val)
            en_val = re.sub(r"Rs\.?\s*", "INR ", en_val)
            self._cache[cache_key] = en_val
            self._save_cache()
            return {
                "back_translation": en_val,
                "method": "neural_mt_reverse_kn",
                "confidence": 0.92
            }

        # Reverse Kannada Synthesizer Fallback
        en_synthesized = self._synthesize_kannada_back_translation(clean_kn)
        return {
            "back_translation": en_synthesized,
            "method": "reverse_kannada_legal_synthesis",
            "confidence": 0.85
        }

    def _synthesize_kannada_back_translation(self, text: str) -> str:
        """Applies reverse Kannada statutory grammar, entity normalization, and reverse glossary lookup."""
        res = text

        # Restore Section / Article / Currency
        res = re.sub(r"ಸೆಕ್ಷನ್\s+(\d+[A-Z]?)", r"Section \1", res)
        res = re.sub(r"ವಿಭಾಗ\s+(\d+[A-Z]?)", r"Section \1", res)
        res = re.sub(r"ಸೆಕ್ಷನ್‌ಗಳು\s+(\d+[A-Z]?(?:\s*(?:,|ಮತ್ತು)\s*\d+[A-Z]?)*)", r"Sections \1", res)
        res = re.sub(r"ವಿಭಾಗಗಳು\s+(\d+[A-Z]?(?:\s*(?:,|ಮತ್ತು)\s*\d+[A-Z]?)*)", r"Sections \1", res)
        res = re.sub(r"ವಿಧಿ\s+(\d+[A-Z]?)", r"Article \1", res)
        res = re.sub(r"ಅನುಚ್ಛೇದ\s+(\d+[A-Z]?)", r"Article \1", res)
        res = re.sub(r"₹\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)
        res = re.sub(r"ರೂಪಾಯಿ\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)
        res = re.sub(r"ರೂ\.\s*([\d,]+(?:\.\d+)?(?:/-)?)", r"INR \1", res)

        if self.glossary_kn:
            sorted_kn_terms = sorted(self.glossary_kn.kn_to_en.keys(), key=len, reverse=True)
            for kn_term in sorted_kn_terms:
                if kn_term in res:
                    en_term = self.glossary_kn.kn_to_en[kn_term]
                    res = res.replace(kn_term, en_term)

        reverse_modals_kn = [
            (r"ಮಾಡತಕ್ಕದ್ದಲ್ಲ", "shall not"),
            (r"ಕೂಡದು", "shall not"),
            (r"ಆಗಿರತಕ್ಕದ್ದಲ್ಲ", "shall not be"),
            (r"ಮಾಡತಕ್ಕದ್ದು", "shall"),
            (r"ಬದ್ಧನಾಗಿರತಕ್ಕದ್ದು", "shall be liable"),
            (r"ಹೊಣೆಗಾರನಾಗಿರುತ್ತಾನೆ", "shall be liable"),
            (r"ಆಗಿರತಕ್ಕದ್ದು", "shall be"),
            (r"ಮಾಡಬಹುದು", "may"),
            (r"ಖಡ್ಡಾಯವಾಗಿ ಮಾಡಬೇಕು", "must")
        ]
        for pat, repl in reverse_modals_kn:
            res = re.sub(pat, repl, res)

        return res
