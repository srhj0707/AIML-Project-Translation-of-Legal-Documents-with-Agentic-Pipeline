# Legal Translation & Validation Audit Report

**Pipeline Verdict**: ⚠️ `REVIEW_REQUIRED`  
**Total Clauses**: `16` | **Verified**: `12` | **Flagged for Human Review**: `4`

## 1. Executive Metric Summary

| Evaluation Metric | Score | Benchmark Target | Interpretation |
| :--- | :--- | :--- | :--- |
| **Legal Meaning Fidelity Score** | **97.19%** | >= 90.0% | Evaluates preservation of legal duty, negation & meaning |
| **Entity Exact Match Rate** | **100.0%** | 100.0% | Measures statutory sections, case numbers, dates & currency |
| **Back-Translation chrF** | **89.61** | >= 65.0 | Character-level n-gram morphological similarity |
| **Back-Translation BLEU** | **84.7** | >= 30.0 | Surface n-gram lexical overlap |

## 2. Clause-by-Clause Translation & Audit Trace

### Clause C_001 (document_header) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: IN THE HIGH COURT OF JUDICATURE AT ALLAHABAD
- **Draft Hindi (NLP)**: IN THE उच्च न्यायालय OF JUDICATURE AT ALLAHABAD
- **Verified Hindi (Agentic AI)**: IN THE उच्च न्यायालय OF JUDICATURE AT ALLAHABAD
- **Back-Translated (EN)**: IN THE High Court OF JUDICATURE AT ALLAHABAD
- **Validation Metrics**: BLEU: `41.11`, chrF: `69.69`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_002 (bail_condition) - `Risk: STANDARD` ⚠️ **FLAGGED FOR HUMAN LEGAL REVIEW**

- **Source (EN)**: CRIMINAL MISC. BAIL APPLICATION NO. 14205 OF 2023
- **Draft Hindi (NLP)**: CRIMINAL MISC. BAIL APPLICATION NO. 14205 OF 2023
- **Verified Hindi (Agentic AI)**: CRIMINAL MISC. BAIL APPLICATION NO. 14205 OF 2023
- **Back-Translated (EN)**: CRIMINAL MISC. BAIL APPLICATION NO. 14205 OF 2023
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `85.0%` (WARNING_REVIEW_RECOMMENDED)

**Human Review Directives:**
- ⚠️ Low translation confidence (65%) - human legal verification recommended.
- ⚠️ [terminology_fidelity] Term drift: 'BAIL APPLICATION' was not translated to expected statutory term 'जमानत याचिका'

---

### Clause C_003 (operative) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: Vikram Singh ... Applicant / Accused Versus State of Uttar Pradesh ... Respondent / Complainant
- **Draft Hindi (NLP)**: Vikram Singh ... आवेदक / अभियुक्त Versus State of Uttar Pradesh ... प्रत्यर्थी / शिकायतकर्ता
- **Verified Hindi (Agentic AI)**: Vikram Singh ... आवेदक / अभियुक्त Versus State of Uttar Pradesh ... प्रत्यर्थी / शिकायतकर्ता
- **Back-Translated (EN)**: Vikram Singh ... Applicant / Accused Versus State of Uttar Pradesh ... Respondent / Complainant
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_004 (judicial_heading) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: CORAM: HON'BLE MR. JUSTICE RAJESH KUMAR
- **Draft Hindi (NLP)**: CORAM: HON'BLE MR. JUSTICE RAJESH KUMAR
- **Verified Hindi (Agentic AI)**: CORAM: HON'BLE MR. JUSTICE RAJESH KUMAR
- **Back-Translated (EN)**: CORAM: HON'BLE MR. JUSTICE RAJESH KUMAR
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_005 (judicial_heading) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: ORDER:
- **Draft Hindi (NLP)**: ORDER:
- **Verified Hindi (Agentic AI)**: ORDER:
- **Back-Translated (EN)**: ORDER:
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_006 (operative) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: 1. Heard Sri Ramesh Chandra, Learned Counsel for the Applicant, and Sri A.K. Sharma, Learned Additional Government Advocate for the State of Uttar Pradesh.
- **Draft Hindi (NLP)**: 1. आवेदक के विद्वान अधिवक्ता श्री Ramesh Chandra तथा State of Uttar Pradesh के विद्वान अपर शासकीय अधिवक्ता श्री A.K. Sharma को सुना गया।
- **Verified Hindi (Agentic AI)**: 1. आवेदक के विद्वान अधिवक्ता श्री Ramesh Chandra तथा State of Uttar Pradesh के विद्वान अपर शासकीय अधिवक्ता श्री A.K. Sharma को सुना गया।
- **Back-Translated (EN)**: 1. Applicant के Learned Counsel श्री Ramesh Chandra तथा State of Uttar Pradesh के विद्वान अपर शासकीय अधिवक्ता श्री A.K. Sharma को सुना गया।
- **Validation Metrics**: BLEU: `22.92`, chrF: `41.87`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_007 (bail_condition) - `Risk: ELEVATED` ⚠️ **FLAGGED FOR HUMAN LEGAL REVIEW**

- **Source (EN)**: 2. This is an application under Section 439 of the Code of Criminal Procedure, 1973 for grant of regular bail to the Applicant in Case Crime No. 342 of 2023 under Sections 420, 467, 468, and 471 of the Indian Penal Code, 1860 registered at Police Station Gomti Nagar, Lucknow.
- **Draft Hindi (NLP)**: 2. This is an application under धारा 439 of the Code of Criminal Procedure, 1973 for grant of नियमित जमानत to the आवेदक in Case Crime No. 342 of 2023 under धाराएं 420, 467, 468, and 471 of the Indian Penal Code, 1860 registered at Police Station Gomti Nagar, Lucknow.
- **Verified Hindi (Agentic AI)**: 2. This is an application under धारा 439 of the Code of Criminal Procedure, 1973 for grant of नियमित जमानत to the आवेदक in Case Crime No. 342 of 2023 under धाराएं 420, 467, 468, and 471 of the Indian Penal Code, 1860 registered at Police Station Gomti Nagar, Lucknow.
- **Back-Translated (EN)**: 2. This is an application under Section 439 of the Code of Criminal Procedure, 1973 for grant of Regular Bail to the Applicant in Case Crime No. 342 of 2023 under Sections 420, 467, 468, and 471 of the Indian Penal Code, 1860 registered at Police Station Gomti Nagar, Lucknow.
- **Validation Metrics**: BLEU: `93.85`, chrF: `96.87`, Entity Match: `100%`
- **Judge Score**: `92.5%` (PASSED)

**Human Review Directives:**
- ⚠️ Low translation confidence (82%) - human legal verification recommended.
- ⚠️ [terminology_fidelity] Term drift: 'Code of Criminal Procedure' was not translated to expected statutory term 'दंड प्रक्रिया संहिता'
- ⚠️ [terminology_fidelity] Term drift: 'Indian Penal Code' was not translated to expected statutory term 'भारतीय दंड संहिता'

---

### Clause C_008 (operative) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: 3. Learned Counsel for the Applicant submits that the Applicant is innocent and has been falsely implicated in the present case due to business rivalry. It is submitted that the dispute is essentially of a civil nature and no prima facie case is made out against the Applicant. The Applicant has been languishing in jail since 12th August, 2023.
- **Draft Hindi (NLP)**: 3. विद्वान अधिवक्ता for the आवेदक submits that the आवेदक is innocent and has been falsely implicated in the present case due to business rivalry. It is submitted that the dispute is essentially of a civil nature and no प्रथम दृष्टया case is made out against the आवेदक. The आवेदक has been languishing in jail since 12th August, 2023.
- **Verified Hindi (Agentic AI)**: 3. विद्वान अधिवक्ता for the आवेदक submits that the आवेदक is innocent and has been falsely implicated in the present case due to business rivalry. It is submitted that the dispute is essentially of a civil nature and no प्रथम दृष्टया case is made out against the आवेदक. The आवेदक has been languishing in jail since 12th August, 2023.
- **Back-Translated (EN)**: 3. Learned Counsel for the Applicant submits that the Applicant is innocent and has been falsely implicated in the present case due to business rivalry. It is submitted that the dispute is essentially of a civil nature and no prima facie case is made out against the Applicant. The Applicant has been languishing in jail since 12th August, 2023.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_009 (bail_condition) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 4. Learned Additional Government Advocate vehemently opposed the bail application, contending that there are serious allegations of financial fraud involving Rs. 45,00,000/- (Rupees Forty Five Lakhs only) against the Applicant.
- **Draft Hindi (NLP)**: 4. Learned Additional Government Advocate vehemently opposed the जमानत याचिका, contending that there are serious allegations of financial fraud involving ₹45,00,000/- (Rupees Forty Five Lakhs only) against the आवेदक.
- **Verified Hindi (Agentic AI)**: 4. Learned Additional Government Advocate vehemently opposed the जमानत याचिका, contending that there are serious allegations of financial fraud involving ₹45,00,000/- (Rupees Forty Five Lakhs only) against the आवेदक. (Rs. 45,00,000/-)
- **Back-Translated (EN)**: 4. Learned Additional Government Advocate vehemently opposed the Bail Application, contending that there are serious allegations of financial fraud involving INR 45,00,000/- (Rupees Forty Five Lakhs only) against the Applicant. (Rs. 45,00,000/-)
- **Validation Metrics**: BLEU: `73.72`, chrF: `93.84`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

**Agentic Rectifications Applied:**
- *RESTORE_ENTITY*: Restored critical entity 'Rs. 45,00,000/-' into translation

---

### Clause C_010 (operative) - `Risk: STANDARD` ✅ **VERIFIED**

- **Source (EN)**: 5. Having heard the parties and perused the record, without expressing any opinion on the merits of the case, this Court finds that the charge-sheet has already been submitted and the trial is likely to take considerable time.
- **Draft Hindi (NLP)**: 5. Having heard the parties and perused the record, without expressing any opinion on the merits of the case, this Court finds that the charge-sheet has already been submitted and the trial is likely to take considerable time.
- **Verified Hindi (Agentic AI)**: 5. Having heard the parties and perused the record, without expressing any opinion on the merits of the case, this Court finds that the charge-sheet has already been submitted and the trial is likely to take considerable time.
- **Back-Translated (EN)**: 5. Having heard the parties and perused the record, without expressing any opinion on the merits of the case, this Court finds that the charge-sheet has already been submitted and the trial is likely to take considerable time.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_011 (bail_condition) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: 6. Let the Applicant, Vikram Singh, be released on bail on his furnishing a personal bond in the sum of Rs. 1,00,000/- (Rupees One Lakh) with two reliable sureties each in the like amount to the satisfaction of the Learned Chief Judicial Magistrate, Lucknow, subject to the following conditions:
- **Draft Hindi (NLP)**: 6. आवेदक Vikram Singh को विद्वान मुख्य न्यायिक मजिस्ट्रेट, Lucknow की संतुष्टि के अनुरूप समान राशि के दो विश्वसनीय प्रतिभुओं के साथ ₹1,00,000/- (Rupees One Lakh) की राशि का व्यक्तिगत बंधपत्र प्रस्तुत करने पर निम्नलिखित शर्तों के अधीन जमानत पर रिहा किया जाए:
- **Verified Hindi (Agentic AI)**: 6. आवेदक Vikram Singh को विद्वान मुख्य न्यायिक मजिस्ट्रेट, Lucknow की संतुष्टि के अनुरूप समान राशि के दो विश्वसनीय प्रतिभुओं के साथ ₹1,00,000/- (Rupees One Lakh) की राशि का व्यक्तिगत बंधपत्र प्रस्तुत करने पर निम्नलिखित शर्तों के अधीन जमानत पर रिहा किया जाए: (Rs. 1,00,000/-)
- **Back-Translated (EN)**: 6. Applicant Vikram Singh को विद्वान Chief Judicial Magistrate, Lucknow की संतुष्टि के अनुरूप समान राशि के दो विश्वसनीय प्रतिभुओं के साथ INR 1,00,000/- (Rupees One Lakh) की राशि का व्यक्तिगत बंधपत्र प्रस्तुत करने पर निम्नलिखित शर्तों subject to जमानत पर रिहा किया जाए: (Rs. 1,00,000/-)
- **Validation Metrics**: BLEU: `23.63`, chrF: `31.44`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

**Agentic Rectifications Applied:**
- *RESTORE_ENTITY*: Restored critical entity 'Rs. 1,00,000/-' into translation

---

### Clause C_012 (operative) - `Risk: CRITICAL` ✅ **VERIFIED**

- **Source (EN)**: (i) The Applicant shall not tamper with the prosecution witnesses or intimidate any person acquainted with the facts of the case.
- **Draft Hindi (NLP)**: (i) The आवेदक नहीं करेगा tamper with the prosecution witnesses or intimidate any person acquainted with the facts of the case.
- **Verified Hindi (Agentic AI)**: (i) The आवेदक नहीं करेगा tamper with the prosecution witnesses or intimidate any person acquainted with the facts of the case.
- **Back-Translated (EN)**: (i) The Applicant shall not tamper with the prosecution witnesses or intimidate any person acquainted with the facts of the case.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_013 (operative) - `Risk: ELEVATED` ✅ **VERIFIED**

- **Source (EN)**: (ii) The Applicant shall cooperate with the trial and shall attend the Learned Trial Court on each date fixed unless exempted.
- **Draft Hindi (NLP)**: (ii) The आवेदक करेगा cooperate with the trial and करेगा attend the Learned Trial Court on each date fixed unless exempted.
- **Verified Hindi (Agentic AI)**: (ii) The आवेदक करेगा cooperate with the trial and करेगा attend the Learned Trial Court on each date fixed unless exempted.
- **Back-Translated (EN)**: (ii) The Applicant shall cooperate with the trial and shall attend the Learned Trial Court on each date fixed unless exempted.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_014 (operative) - `Risk: CRITICAL` ✅ **VERIFIED**

- **Source (EN)**: (iii) The Applicant shall not leave the territory of India without prior permission of the Trial Court.
- **Draft Hindi (NLP)**: (iii) The आवेदक नहीं करेगा leave the territory of India without prior permission of the Trial Court.
- **Verified Hindi (Agentic AI)**: (iii) The आवेदक नहीं करेगा leave the territory of India without prior permission of the Trial Court.
- **Back-Translated (EN)**: (iii) The Applicant shall not leave the territory of India without prior permission of the Trial Court.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `100.0%` (PASSED)

---

### Clause C_015 (bail_condition) - `Risk: ELEVATED` ⚠️ **FLAGGED FOR HUMAN LEGAL REVIEW**

- **Source (EN)**: 7. In case of breach of any of the above conditions, the Learned Trial Court shall be at liberty to cancel the bail in accordance with law.
- **Draft Hindi (NLP)**: 7. उपरोक्त शर्तों में से किसी के भी उल्लंघन की स्थिति में, विद्वान विचारण न्यायालय को कानून के अनुसार जमानत रद्द करने की स्वतंत्रता होगी।
- **Verified Hindi (Agentic AI)**: 7. उपरोक्त शर्तों में से किसी के भी उल्लंघन की स्थिति में, विद्वान विचारण न्यायालय को कानून के अनुसार जमानत रद्द करने की स्वतंत्रता होगी।
- **Back-Translated (EN)**: 7. In case of breach of any of the above conditions, the Learned Trial Court shall be at liberty to cancel the bail in accordance with law.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `85.0%` (WARNING_REVIEW_RECOMMENDED)

**Human Review Directives:**
- ⚠️ Low translation confidence (65%) - human legal verification recommended.
- ⚠️ [terminology_fidelity] Term drift: 'shall' was not translated to expected statutory term 'करेगा / बाध्य होगा / होगा'

---

### Clause C_016 (bail_condition) - `Risk: STANDARD` ⚠️ **FLAGGED FOR HUMAN LEGAL REVIEW**

- **Source (EN)**: 8. The Bail Application is accordingly allowed.
- **Draft Hindi (NLP)**: 8. तदनुसार जमानत याचिका स्वीकार की जाती है।
- **Verified Hindi (Agentic AI)**: 8. तदनुसार जमानत याचिका स्वीकार की जाती है।
- **Back-Translated (EN)**: 8. The Bail Application is accordingly allowed.
- **Validation Metrics**: BLEU: `100.0`, chrF: `100.0`, Entity Match: `100%`
- **Judge Score**: `92.5%` (PASSED)

**Human Review Directives:**
- ⚠️ Low translation confidence (82%) - human legal verification recommended.
- ⚠️ [terminology_fidelity] Term drift: 'allowed' was not translated to expected statutory term 'स्वीकार किया गया'

---
