# Legal Translation & Validation Audit Report

**Pipeline Verdict**: ⚠️ `REVIEW_REQUIRED`  
**Total Clauses**: `26` | **Verified**: `22` | **Flagged for Human Review**: `4`

## 1. Executive Metric Summary

| Evaluation Metric | Score | Benchmark Target | Interpretation |
| :--- | :--- | :--- | :--- |
| **Legal Meaning Fidelity Score** | **98.39%** | >= 90.0% | Evaluates preservation of legal duty, negation & meaning |
| **Entity Exact Match Rate** | **100.0%** | 100.0% | Measures statutory sections, case numbers, dates & currency |
| **Back-Translation chrF** | **85.0** | >= 65.0 | Character-level n-gram morphological similarity |
| **Back-Translation BLEU** | **82.77** | >= 30.0 | Surface n-gram lexical overlap |

## 2. Clause-by-Clause Translation & Audit Trace

### Clause C_001 (document_header) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: MASTER SERVICES AGREEMENT
- **Draft Hindi (NLP)**: MASTER SERVICES करार
- **Verified Hindi (Agentic AI)**: MASTER SERVICES करार
- **Back-Translated (EN)**: MASTER SERVICES Agreement
- **Validation Metrics**: BLEU: `55.03`, chrF: `60.7`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_002 (document_header) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: This Master Services Agreement ("Agreement") is made and entered into on this 15th day of November, 2023, by and between:
- **Draft Hindi (NLP)**: यह मास्टर सेवा करार (\"करार\") इस 15th day of November, 2023 को निम्नलिखित पक्षकारों के मध्य निष्पादित और प्रविष्ट किया गया है:
- **Verified Hindi (Agentic AI)**: यह मास्टर सेवा करार (\"करार\") इस 15th day of November, 2023 को निम्नलिखित पक्षकारों के मध्य निष्पादित और प्रविष्ट किया गया है:
- **Back-Translated (EN)**: यह मास्टर सेवा Agreement (\"Agreement\") इस 15th day of November, 2023 को निम्नलिखित पक्षकारों के मध्य निष्पादित और प्रविष्ट किया गया है:
- **Validation Metrics**: BLEU: `20.87`, chrF: `34.29`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_003 (operative) - `Risk: ELEVATED` ⚠️ **FLAGGED FOR HUMAN LEGAL REVIEW**

- **Source (EN)**: ALPHA LEGAL TECH PRIVATE LIMITED, a company incorporated under the Companies Act, 2013, having its registered office at Nariman Point, Mumbai - 400021 (hereinafter referred to as the "Service Provider", which expression shall include its successors and permitted assigns);
- **Draft Hindi (NLP)**: ALPHA LEGAL TECH PRIVATE LIMITED, a company incorporated under the Companies Act, 2013, having its registered office at Nariman Point, Mumbai - 400021 (hereinafter referred to as the "Service Provider", which expression करेगा include its successors and permitted assigns);
- **Verified Hindi (Agentic AI)**: ALPHA LEGAL TECH PRIVATE LIMITED, a company incorporated under the Companies Act, 2013, having its registered office at Nariman Point, Mumbai - 400021 (hereinafter referred to as the "Service Provider", which expression करेगा include its successors and permitted assigns);
- **Back-Translated (EN)**: ALPHA LEGAL TECH PRIVATE LIMITED, a company incorporated under the Companies Act, 2013, having its registered office at Nariman Point, Mumbai - 400021 (hereinafter referred to as the "Service Provider", which expression shall include its successors and permitted assigns);
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `92.5%` (PASSED)

**Human Review Directives:**
- ⚠️ Low translation confidence (82%) - human legal verification recommended.
- ⚠️ [terminology_fidelity] Term drift: 'Companies Act' was not translated to expected statutory term 'कंपनी अधिनियम'

---

### Clause C_004 (operative) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: AND
- **Draft Hindi (NLP)**: AND
- **Verified Hindi (Agentic AI)**: AND
- **Back-Translated (EN)**: AND
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_005 (operative) - `Risk: ELEVATED` ⚠️ **FLAGGED FOR HUMAN LEGAL REVIEW**

- **Source (EN)**: BHARAT COMMERCIAL ENTERPRISES LIMITED, a company incorporated under the Companies Act, 2013, having its registered office at Connaught Place, New Delhi - 110001 (hereinafter referred to as the "Client", which expression shall include its successors and permitted assigns).
- **Draft Hindi (NLP)**: BHARAT COMMERCIAL ENTERPRISES LIMITED, a company incorporated under the Companies Act, 2013, having its registered office at Connaught Place, New Delhi - 110001 (hereinafter referred to as the "Client", which expression करेगा include its successors and permitted assigns).
- **Verified Hindi (Agentic AI)**: BHARAT COMMERCIAL ENTERPRISES LIMITED, a company incorporated under the Companies Act, 2013, having its registered office at Connaught Place, New Delhi - 110001 (hereinafter referred to as the "Client", which expression करेगा include its successors and permitted assigns).
- **Back-Translated (EN)**: BHARAT COMMERCIAL ENTERPRISES LIMITED, a company incorporated under the Companies Act, 2013, having its registered office at Connaught Place, New Delhi - 110001 (hereinafter referred to as the "Client", which expression shall include its successors and permitted assigns).
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `92.5%` (PASSED)

**Human Review Directives:**
- ⚠️ Low translation confidence (82%) - human legal verification recommended.
- ⚠️ [terminology_fidelity] Term drift: 'Companies Act' was not translated to expected statutory term 'कंपनी अधिनियम'

---

### Clause C_006 (recital) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: WHEREAS: A. The Service Provider is engaged in the business of providing enterprise software and legal analytics solutions. B. The Client desires to retain the Service Provider, and the Service Provider agrees to render such services on the terms and conditions set forth herein.
- **Draft Hindi (NLP)**: चूंकि: A. The Service Provider is engaged in the business of providing enterprise software and legal analytics solutions. B. The Client desires to retain the Service Provider, and the Service Provider agrees to render such services on the terms and conditions set forth herein.
- **Verified Hindi (Agentic AI)**: चूंकि: A. The Service Provider is engaged in the business of providing enterprise software and legal analytics solutions. B. The Client desires to retain the Service Provider, and the Service Provider agrees to render such services on the terms and conditions set forth herein.
- **Back-Translated (EN)**: Whereas: A. The Service Provider is engaged in the business of providing enterprise software and legal analytics solutions. B. The Client desires to retain the Service Provider, and the Service Provider agrees to render such services on the terms and conditions set forth herein.
- **Validation Metrics**: BLEU: `97.94`, chrF: `97.07`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_007 (transition_recital) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: NOW, THEREFORE, the Parties agree as follows:
- **Draft Hindi (NLP)**: अतएव अब, पक्षकार निम्नलिखित रूप से परस्पर सहमत होते हैं:
- **Verified Hindi (Agentic AI)**: अतएव अब, पक्षकार निम्नलिखित रूप से परस्पर सहमत होते हैं:
- **Back-Translated (EN)**: NOW, THEREFORE, the Parties agree as follows:
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_008 (definitions) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: 1. DEFINITIONS AND INTERPRETATION
- **Draft Hindi (NLP)**: 1. DEFINITIONS AND INTERPRETATION
- **Verified Hindi (Agentic AI)**: 1. DEFINITIONS AND INTERPRETATION
- **Back-Translated (EN)**: 1. DEFINITIONS AND INTERPRETATION
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_009 (judicial_heading) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 1.1 "Applicable Law" shall mean any statute, law, regulation, ordinance, rule, judgment, order, decree, or directive having the force of law in the Republic of India.
- **Draft Hindi (NLP)**: 1.1 "Applicable Law" करेगा mean any statute, law, regulation, ordinance, rule, judgment, order, डिक्री, or directive having the force of law in the Republic of India.
- **Verified Hindi (Agentic AI)**: 1.1 "Applicable Law" करेगा mean any statute, law, regulation, ordinance, rule, judgment, order, डिक्री, or directive having the force of law in the Republic of India.
- **Back-Translated (EN)**: 1.1 "Applicable Law" shall mean any statute, law, regulation, ordinance, rule, judgment, order, Decree, or directive having the force of law in the Republic of India.
- **Validation Metrics**: BLEU: `92.79`, chrF: `97.46`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_010 (operative) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 1.2 "Confidential Information" shall mean all proprietary information disclosed by one Party to the other Party, whether orally or in writing.
- **Draft Hindi (NLP)**: 1.2 "Confidential Information" करेगा mean all proprietary information disclosed by one Party to the other Party, whether orally or in writing.
- **Verified Hindi (Agentic AI)**: 1.2 "Confidential Information" करेगा mean all proprietary information disclosed by one Party to the other Party, whether orally or in writing.
- **Back-Translated (EN)**: 1.2 "Confidential Information" shall mean all proprietary information disclosed by one Party to the other Party, whether orally or in writing.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_011 (operative) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: 2. OBLIGATIONS OF THE SERVICE PROVIDER
- **Draft Hindi (NLP)**: 2. OBLIGATIONS OF THE SERVICE PROVIDER
- **Verified Hindi (Agentic AI)**: 2. OBLIGATIONS OF THE SERVICE PROVIDER
- **Back-Translated (EN)**: 2. OBLIGATIONS OF THE SERVICE PROVIDER
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_012 (operative) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 2.1 The Service Provider shall perform the Services with reasonable skill, care, and diligence in accordance with the specifications set forth in Schedule A.
- **Draft Hindi (NLP)**: 2.1 The Service Provider करेगा perform the Services with reasonable skill, care, and diligence in accordance with the specifications set forth in Schedule A.
- **Verified Hindi (Agentic AI)**: 2.1 The Service Provider करेगा perform the Services with reasonable skill, care, and diligence in accordance with the specifications set forth in Schedule A.
- **Back-Translated (EN)**: 2.1 The Service Provider shall perform the Services with reasonable skill, care, and diligence in accordance with the specifications set forth in Schedule A.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_013 (operative) - `Risk: CRITICAL` ✅ **VERIFIED**

- **Source (EN)**: 2.2 The Service Provider shall not assign or sub-contract any of its obligations without the prior written consent of the Client.
- **Draft Hindi (NLP)**: 2.2 The Service Provider नहीं करेगा assign or sub-संविदा any of its obligations without the prior written consent of the Client.
- **Verified Hindi (Agentic AI)**: 2.2 The Service Provider नहीं करेगा assign or sub-संविदा any of its obligations without the prior written consent of the Client.
- **Back-Translated (EN)**: 2.2 The Service Provider shall not assign or sub-Contract any of its obligations without the prior written consent of the Client.
- **Validation Metrics**: BLEU: `87.25`, chrF: `96.69`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_014 (operative) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: 3. FEES AND PAYMENT TERMS
- **Draft Hindi (NLP)**: 3. FEES AND PAYMENT TERMS
- **Verified Hindi (Agentic AI)**: 3. FEES AND PAYMENT TERMS
- **Back-Translated (EN)**: 3. FEES AND PAYMENT TERMS
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_015 (operative) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 3.1 The Client shall pay the Service Provider a total consideration of INR 15,00,000/- (Indian Rupees Fifteen Lakhs only) plus applicable Goods and Services Tax (GST) within thirty (30) days from the date of receipt of an undisputed invoice.
- **Draft Hindi (NLP)**: 3.1 The Client करेगा pay the Service Provider a total प्रतिफल of ₹15,00,000/- (Indian Rupees Fifteen Lakhs only) plus applicable Goods and Services Tax (GST) within thirty (30) days from the date of receipt of an undisputed invoice.
- **Verified Hindi (Agentic AI)**: 3.1 The Client करेगा pay the Service Provider a total प्रतिफल of ₹15,00,000/- (Indian Rupees Fifteen Lakhs only) plus applicable Goods and Services Tax (GST) within thirty (30) days from the date of receipt of an undisputed invoice.
- **Back-Translated (EN)**: 3.1 The Client shall pay the Service Provider a total Consideration of INR 15,00,000/- (Indian Rupees Fifteen Lakhs only) plus applicable Goods and Services Tax (GST) within thirty (30) days from the date of receipt of an undisputed invoice.
- **Validation Metrics**: BLEU: `94.53`, chrF: `98.25`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_016 (operative) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 3.2 Any delayed payment shall attract interest at the rate of 9% per annum from the due date until the date of actual payment.
- **Draft Hindi (NLP)**: 3.2 Any delayed payment करेगा attract interest at the rate of 9% per annum from the due date until the date of actual payment.
- **Verified Hindi (Agentic AI)**: 3.2 Any delayed payment करेगा attract interest at the rate of 9% per annum from the due date until the date of actual payment.
- **Back-Translated (EN)**: 3.2 Any delayed payment shall attract interest at the rate of 9% per annum from the due date until the date of actual payment.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_017 (indemnity) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: 4. INDEMNIFICATION AND LIABILITY
- **Draft Hindi (NLP)**: 4. INDEMNIFICATION AND LIABILITY
- **Verified Hindi (Agentic AI)**: 4. INDEMNIFICATION AND LIABILITY
- **Back-Translated (EN)**: 4. INDEMNIFICATION AND LIABILITY
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_018 (indemnity) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 4.1 The Service Provider shall indemnify, defend, and hold harmless the Client, its directors, officers, and employees against any third-party claims, liabilities, losses, damages, and expenses arising directly out of any willful misconduct or breach of confidentiality by the Service Provider.
- **Draft Hindi (NLP)**: 4.1 The Service Provider करेगा indemnify, defend, and hold harmless the Client, its directo₹, office₹, and employees against any third-party claims, liabilities, losses, damages, and expenses arising directly out of any willful misconduct or breach of गोपनीयता by the Service Provider.
- **Verified Hindi (Agentic AI)**: 4.1 The Service Provider करेगा indemnify, defend, and hold harmless the Client, its directo₹, office₹, and employees against any third-party claims, liabilities, losses, damages, and expenses arising directly out of any willful misconduct or breach of गोपनीयता by the Service Provider. (rs,)
- **Back-Translated (EN)**: 4.1 The Service Provider shall indemnify, defend, and hold harmless the Client, its directoINR , officeINR , and employees against any third-party claims, liabilities, losses, damages, and expenses arising directly out of any willful misconduct or breach of Confidentiality by the Service Provider. (rs,)
- **Validation Metrics**: BLEU: `79.63`, chrF: `94.82`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

**Agentic Rectifications Applied:**
- *RESTORE_ENTITY*: Restored critical entity 'rs,' into translation

---

### Clause C_019 (operative) - `Risk: ELEVATED` ⚠️ **FLAGGED FOR HUMAN LEGAL REVIEW**

- **Source (EN)**: 4.2 In no event shall the total aggregate liability of either Party under this Agreement exceed INR 30,00,000/- (Indian Rupees Thirty Lakhs only).
- **Draft Hindi (NLP)**: 4.2 In no event करेगा the total aggregate liability of either Party under this करार exceed ₹30,00,000/- (Indian Rupees Thirty Lakhs only).
- **Verified Hindi (Agentic AI)**: 4.2 In no event नहीं करेगा the total aggregate liability of either Party under this करार exceed ₹30,00,000/- (Indian Rupees Thirty Lakhs only).
- **Back-Translated (EN)**: 4.2 In no event shall not the total aggregate liability of either Party under this Agreement exceed INR 30,00,000/- (Indian Rupees Thirty Lakhs only).
- **Validation Metrics**: BLEU: `90.62`, chrF: `97.44`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

**Agentic Rectifications Applied:**
- *FLAG_CRITICAL_LEGAL_RISK*: CRITICAL: English source contains strict legal negation/prohibition, but no negation was detected in Hindi translation!

**Human Review Directives:**
- ⚠️ CRITICAL: English source contains strict legal negation/prohibition, but no negation was detected in Hindi translation!

---

### Clause C_020 (termination) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: 5. TERMINATION
- **Draft Hindi (NLP)**: 5. समाप्ति
- **Verified Hindi (Agentic AI)**: 5. समाप्ति
- **Back-Translated (EN)**: 5. Termination
- **Validation Metrics**: BLEU: `55.03`, chrF: `8.14`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_021 (termination) - `Risk: ELEVATED` ⚠️ **FLAGGED FOR HUMAN LEGAL REVIEW**

- **Source (EN)**: 5.1 Either Party may terminate this Agreement forthwith by giving written notice of thirty (30) days in the event of a material breach by the other Party which remains uncured for fifteen (15) days after receipt of notice.
- **Draft Hindi (NLP)**: 5.1 Either Party कर सकता है terminate this करार तत्काल by giving written सूचना of thirty (30) days in the event of a material breach by the other Party which remains uncured for fifteen (15) days after receipt of सूचना.
- **Verified Hindi (Agentic AI)**: 5.1 Either Party कर सकता है terminate this करार तत्काल by giving written सूचना of thirty (30) days in the event of a material breach by the other Party which remains uncured for fifteen (15) days after receipt of सूचना.
- **Back-Translated (EN)**: 5.1 Either Party may terminate this Agreement forthwith by giving written Notice of thirty (30) days in the event of a material breach by the other Party which remains uncured for fifteen (15) days after receipt of Notice.
- **Validation Metrics**: BLEU: `89.58`, chrF: `96.15`, Entity Match: `100%`
- **Judge Score**: `75.0%` (FAILED_CRITICAL_DISCREPANCY)

**Human Review Directives:**
- ⚠️ [negation_fidelity] CRITICAL: Negation or prohibition present in English source was lost in translation!

---

### Clause C_022 (termination) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 5.2 Upon termination, the Client shall forthwith pay all outstanding fees accrued up to the effective date of termination.
- **Draft Hindi (NLP)**: 5.2 Upon समाप्ति, the Client करेगा तत्काल pay all outstanding fees accrued up to the effective date of समाप्ति.
- **Verified Hindi (Agentic AI)**: 5.2 Upon समाप्ति, the Client करेगा तत्काल pay all outstanding fees accrued up to the effective date of समाप्ति.
- **Back-Translated (EN)**: 5.2 Upon Termination, the Client shall forthwith pay all outstanding fees accrued up to the effective date of Termination.
- **Validation Metrics**: BLEU: `78.78`, chrF: `93.04`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_023 (dispute_resolution) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: 6. GOVERNING LAW AND DISPUTE RESOLUTION
- **Draft Hindi (NLP)**: 6. शासी विधि AND विवाद समाधान
- **Verified Hindi (Agentic AI)**: 6. शासी विधि AND विवाद समाधान
- **Back-Translated (EN)**: 6. Governing Law AND Dispute Resolution
- **Validation Metrics**: BLEU: `14.54`, chrF: `9.04`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_024 (operative) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 6.1 This Agreement shall be governed by and construed in accordance with the laws of India.
- **Draft Hindi (NLP)**: 6.1 यह करार भारत की विधियों द्वारा शासित और उनके अनुसार अर्थान्वित होगा।
- **Verified Hindi (Agentic AI)**: 6.1 यह करार भारत की विधियों द्वारा शासित और उनके अनुसार अर्थान्वित होगा।
- **Back-Translated (EN)**: 6.1 This Agreement shall be governed by and construed in accordance with the laws of India.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_025 (dispute_resolution) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 6.2 Any dispute arising out of or in connection with this Agreement shall be referred to arbitration in accordance with the Arbitration and Conciliation Act, 1996. The seat and venue of arbitration shall be New Delhi, and the proceedings shall be conducted in the English language before a Sole Arbitrator.
- **Draft Hindi (NLP)**: 6.2 इस करार से उत्पन्न या इसके संबंध में होने वाले किसी भी विवाद को the Arbitration and Conciliation Act, 1996 के अनुसार मध्यस्थता के लिए संदर्भित किया जाएगा। मध्यस्थता का स्थान और विचार-स्थल New Delhi होगा, तथा कार्यवाही एकल मध्यस्थ के समक्ष अंग्रेजी भाषा में संचालित की जाएगी।
- **Verified Hindi (Agentic AI)**: 6.2 इस करार से उत्पन्न या इसके संबंध में होने वाले किसी भी विवाद को the Arbitration and Conciliation Act, 1996 के अनुसार मध्यस्थता के लिए संदर्भित किया जाएगा। मध्यस्थता का स्थान और विचार-स्थल New Delhi होगा, तथा कार्यवाही एकल मध्यस्थ के समक्ष अंग्रेजी भाषा में संचालित की जाएगी।
- **Back-Translated (EN)**: 6.2 इस Agreement से उत्पन्न या इसके संबंध में होने वाले किसी भी विवाद को the Arbitration and Conciliation Act, 1996 के अनुसार Arbitration के लिए संदर्भित किया जाएगा। Arbitration का स्थान और विचार-स्थल New Delhi shall be, तथा कार्यवाही Sole Arbitrator के समक्ष अंग्रेजी भाषा में संचालित की जाएगी।
- **Validation Metrics**: BLEU: `13.96`, chrF: `31.41`, Entity Match: `100%`
- **Judge Score**: `98.12%` (PASSED)

---

### Clause C_026 (operative) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 6.3 The Courts at New Delhi shall have exclusive jurisdiction over all matters arising hereunder.
- **Draft Hindi (NLP)**: 6.3 The Courts at New Delhi करेगा have exclusive क्षेत्राधिकार over all matters arising hereunder.
- **Verified Hindi (Agentic AI)**: 6.3 The Courts at New Delhi करेगा have exclusive क्षेत्राधिकार over all matters arising hereunder.
- **Back-Translated (EN)**: 6.3 The Courts at New Delhi shall have exclusive Jurisdiction over all matters arising hereunder.
- **Validation Metrics**: BLEU: `81.54`, chrF: `95.61`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---
