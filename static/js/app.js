let currentResult = null;
let currentAudit = null;
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', () => {
    setupFileInput();
    setupTextareaCounters();
});

// Sync Radio Buttons with Hidden Target Language Select
function onLangChange(langCode) {
    const sel = document.getElementById('targetLangSelect');
    if (sel) {
        sel.value = langCode;
    }
}

// Setup Multi-format File Drag & Drop (.txt, .pdf, .docx, images)
function setupFileInput() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const extractionStatus = document.getElementById('extractionStatus');
    const extractionMessage = document.getElementById('extractionMessage');
    const docTypeBadge = document.getElementById('docTypeBadge');
    const documentInput = document.getElementById('documentInput');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    async function handleFile(file) {
        const allowedExts = ['.txt', '.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.webp'];
        const fileName = file.name.toLowerCase();
        const isAllowed = allowedExts.some(ext => fileName.endsWith(ext));

        if (!isAllowed) {
            alert(`Unsupported file format. Please upload a .pdf, .docx, .txt, or scanned image (.png, .jpg, .webp).`);
            return;
        }

        // Show extraction loading indicator
        if (extractionStatus) {
            extractionStatus.style.display = 'inline-flex';
            const isImage = ['.png', '.jpg', '.jpeg', '.webp'].some(ext => fileName.endsWith(ext));
            extractionMessage.textContent = isImage
                ? `Running EasyOCR on scanned document (${file.name})...`
                : `Extracting legal text from ${file.name}...`;
        }
        if (docTypeBadge) {
            docTypeBadge.textContent = 'Extracting...';
        }
        if (fileNameDisplay) {
            fileNameDisplay.style.display = 'none';
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const resp = await fetch('/api/parse-document', {
                method: 'POST',
                body: formData
            });

            if (!resp.ok) {
                const errData = await resp.json();
                throw new Error(errData.error || 'Failed to extract text from file.');
            }

            const data = await resp.json();
            documentInput.value = data.text;
            updateCounters();

            if (docTypeBadge) {
                docTypeBadge.textContent = data.format || 'Document Loaded';
            }

            if (fileNameDisplay) {
                fileNameDisplay.style.display = 'inline-block';
                fileNameDisplay.textContent = `✓ Extracted from: ${file.name} (${data.format}) • ${data.word_count.toLocaleString()} words`;
            }

        } catch (err) {
            alert(`File Extraction Error: ${err.message}`);
            if (docTypeBadge) {
                docTypeBadge.textContent = 'Extraction Failed';
            }
        } finally {
            if (extractionStatus) {
                extractionStatus.style.display = 'none';
            }
        }
    }
}

// Textarea Character & Word Counters
function setupTextareaCounters() {
    const docInput = document.getElementById('documentInput');
    docInput.addEventListener('input', updateCounters);
}

function updateCounters() {
    const text = document.getElementById('documentInput').value.trim();
    const chars = text.length;
    const words = text ? text.split(/\s+/).length : 0;
    document.getElementById('charCount').textContent = `${chars.toLocaleString()} characters | ${words.toLocaleString()} words`;
    
    const docTypeBadge = document.getElementById('docTypeBadge');
    if (docTypeBadge && text.length > 0 && docTypeBadge.textContent === 'Awaiting Input') {
        docTypeBadge.textContent = 'Manual Text Entry';
    }
}

function clearInput() {
    document.getElementById('documentInput').value = '';
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    if (fileNameDisplay) {
        fileNameDisplay.textContent = '';
        fileNameDisplay.style.display = 'none';
    }
    const fileInput = document.getElementById('fileInput');
    if (fileInput) fileInput.value = '';
    const docTypeBadge = document.getElementById('docTypeBadge');
    if (docTypeBadge) docTypeBadge.textContent = 'Awaiting Input';
    updateCounters();
}

// Load Pre-configured Samples
async function loadSample(sampleType) {
    try {
        const resp = await fetch(`/api/sample/${sampleType}`);
        if (!resp.ok) throw new Error('Sample not found');
        const data = await resp.json();
        document.getElementById('documentInput').value = data.text;
        
        const fileNameDisplay = document.getElementById('fileNameDisplay');
        if (fileNameDisplay) {
            fileNameDisplay.style.display = 'inline-block';
            fileNameDisplay.textContent = `Loaded Benchmark Preset: ${data.title}`;
        }
        const docTypeBadge = document.getElementById('docTypeBadge');
        if (docTypeBadge) {
            docTypeBadge.textContent = `Preset: ${data.title}`;
        }

        updateCounters();
        document.getElementById('documentInput').scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
        alert(`Failed to load sample: ${err.message}`);
    }
}

// Start Multi-Stage Translation
async function startTranslation() {
    const text = document.getElementById('documentInput').value.trim();
    if (!text) {
        alert('Please enter or upload an English legal document first (.pdf, .docx, .txt, or image).');
        return;
    }

    const progressSection = document.getElementById('progressSection');
    const resultsSection = document.getElementById('resultsSection');
    const translateBtn = document.getElementById('translateBtn');

    // UI state
    translateBtn.disabled = true;
    progressSection.style.display = 'block';
    resultsSection.style.display = 'none';
    progressSection.scrollIntoView({ behavior: 'smooth' });

    // Simulate pipeline stage progression visually
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const step4 = document.getElementById('step4');

    step1.className = 'step active';
    step2.className = 'step';
    step3.className = 'step';
    step4.className = 'step';

    const t1 = setTimeout(() => { step1.className = 'step completed'; step2.className = 'step active'; }, 600);
    const t2 = setTimeout(() => { step2.className = 'step completed'; step3.className = 'step active'; }, 1300);
    const t3 = setTimeout(() => { step3.className = 'step completed'; step4.className = 'step active'; }, 2000);

    try {
        const targetLang = document.getElementById('targetLangSelect') ? document.getElementById('targetLangSelect').value : 'hi';
        const resp = await fetch('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, target_lang: targetLang })
        });

        if (!resp.ok) {
            const errData = await resp.json();
            throw new Error(errData.error || 'Translation failed');
        }

        const data = await resp.json();
        currentResult = data.result;
        currentAudit = data.audit || null;

        const certBtn = document.getElementById('btnDownloadCert');
        if (certBtn) {
            certBtn.style.display = currentAudit ? 'inline-flex' : 'none';
        }

        clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
        step1.className = 'step completed';
        step2.className = 'step completed';
        step3.className = 'step completed';
        step4.className = 'step completed';

        setTimeout(() => {
            progressSection.style.display = 'none';
            renderResults(currentResult);
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            translateBtn.disabled = false;
        }, 500);

    } catch (err) {
        clearTimeout(t1); clearTimeout(t2); clearTimeout(t3);
        progressSection.style.display = 'none';
        translateBtn.disabled = false;
        alert(`Error: ${err.message}`);
    }
}

// Render Results View
function renderResults(res) {
    const summary = res.document_summary;
    const status = res.overall_status;
    const clauses = res.clauses;
    const targetLangCode = res.target_lang_code || 'hi';
    const targetLangName = res.target_language || 'Target';

    // Status Pill
    const pill = document.getElementById('overallStatusPill');
    if (status === 'VERIFIED_READY') {
        pill.textContent = 'VERIFIED READY';
        pill.className = 'status-pill status-verified';
    } else {
        pill.textContent = 'HUMAN REVIEW REQUIRED';
        pill.className = 'status-pill status-review';
    }

    // Title & Badge
    const resultLangBadge = document.getElementById('resultLangBadge');
    if (resultLangBadge) {
        resultLangBadge.textContent = `Language: ${targetLangName}`;
    }
    const translatedPaneTitle = document.getElementById('translatedPaneTitle');
    if (translatedPaneTitle) {
        translatedPaneTitle.textContent = `Verified Legal Translation (${targetLangName})`;
    }

    // KPIs
    document.getElementById('kpiFidelity').textContent = `${summary.avg_legal_fidelity_score}%`;
    document.getElementById('kpiEntityMatch').textContent = `${summary.avg_entity_preservation_pct}%`;
    document.getElementById('kpiChrf').textContent = summary.avg_back_trans_chrf;
    document.getElementById('kpiBleu').textContent = summary.avg_back_trans_bleu;
    document.getElementById('kpiClausesCount').textContent = `${summary.verified_clauses_count} / ${summary.total_clauses}`;

    // Panes
    const sourceFull = clauses.map(c => c.source_en).join('\n\n');
    document.getElementById('sourceDocDisplay').textContent = sourceFull;
    
    const transText = res.translated_document || res.translated_document_kannada || res.translated_document_tamil || res.translated_document_malayalam || res.translated_document_telugu || res.translated_document_hindi || '';
    const hindiDisplay = document.getElementById('hindiDocDisplay');
    hindiDisplay.textContent = transText;

    // Apply native script class to display pane
    hindiDisplay.className = `pane-content font-indic font-${targetLangCode}`;

    // Filter counts
    const flaggedCount = clauses.filter(c => c.requires_human_review).length;
    const criticalCount = clauses.filter(c => c.risk_level === 'critical').length;
    document.getElementById('countAll').textContent = clauses.length;
    document.getElementById('countFlagged').textContent = flaggedCount;
    document.getElementById('countCritical').textContent = criticalCount;

    // Render Clause Cards
    renderClauseCards(clauses, targetLangName, targetLangCode);
}

// Render Clause-by-Clause Cards
function renderClauseCards(clauses, targetLangName, targetLangCode) {
    const container = document.getElementById('clausesContainer');
    container.innerHTML = '';

    const langName = targetLangName || (currentResult ? currentResult.target_language : 'Target');
    const langCode = targetLangCode || (currentResult ? currentResult.target_lang_code : 'hi');

    const filtered = clauses.filter(c => {
        if (currentFilter === 'flagged') return c.requires_human_review;
        if (currentFilter === 'critical') return c.risk_level === 'critical';
        return true;
    });

    if (filtered.length === 0) {
        container.innerHTML = '<div style="padding: 24px; text-align: center; color: #64748b;">No clauses matching the selected filter.</div>';
        return;
    }

    filtered.forEach(c => {
        const item = document.createElement('div');
        item.className = `clause-item risk-${c.risk_level.toLowerCase()}`;

        const isVerified = !c.requires_human_review;
        const badgeClass = isVerified ? 'cbadge cbadge-verified' : 'cbadge cbadge-flagged';
        const badgeText = isVerified ? 'VERIFIED' : 'NEEDS REVIEW';

        // Repairs HTML
        let repairsHtml = '';
        if (c.agent_review.audit_log && c.agent_review.audit_log.length > 0) {
            const listItems = c.agent_review.audit_log.map(a => `<li><b>${escapeHtml(a.action)}:</b> ${escapeHtml(a.details)}</li>`).join('');
            repairsHtml = `<div class="repairs-alert"><strong>🛡️ Agentic AI Safeguards Applied:</strong><ul>${listItems}</ul></div>`;
        }

        // Warnings HTML
        let warningsHtml = '';
        if (c.requires_human_review) {
            const warnings = [];
            c.agent_review.human_review_flags.forEach(f => warnings.push(`<li>${escapeHtml(f)}</li>`));
            if (c.judge_evaluation.violations) {
                c.judge_evaluation.violations.forEach(v => warnings.push(`<li><b>[${escapeHtml(v.dimension)}]</b> ${escapeHtml(v.details)}</li>`));
            }
            warningsHtml = `<div class="warning-alert"><strong>⚠️ Legal Meaning Review Alerts:</strong><ul>${warnings.join('')}</ul></div>`;
        }

        const transText = c.verified_translation || c.verified_hi;

        item.innerHTML = `
            <div class="clause-header">
                <div class="clause-badges">
                    <span class="clause-id">${escapeHtml(c.clause_id)}</span>
                    <span class="cbadge" style="background: #e2e8f0; color: #334155;">[${escapeHtml(c.clause_type.replace('_', ' '))}]</span>
                    <span class="cbadge" style="background: #fee2e2; color: #991b1b;">RISK: ${escapeHtml(c.risk_level.toUpperCase())}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="${badgeClass}">${badgeText}</span>
                    <span style="font-size: 11.5px; font-weight: 700; color: #1e3a8a;">Fidelity: ${c.judge_evaluation.overall_fidelity_score}%</span>
                </div>
            </div>
            <div class="clause-body">
                <div class="c-box c-source">
                    <strong style="display:block; margin-bottom: 6px; font-size: 12px; color: #475569;">English Source Clause:</strong>
                    <p>${escapeHtml(c.source_en)}</p>
                </div>
                <div class="c-box c-trans font-${langCode}">
                    <strong style="display:block; margin-bottom: 6px; font-size: 12px; color: #1e40af;">Verified ${escapeHtml(langName)} Translation:</strong>
                    <p>${escapeHtml(transText)}</p>
                </div>
            </div>
            <div style="background: #fdfdfd; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; font-size: 12px; display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 8px;">
                <span><b>BLEU:</b> ${c.metrics.bleu}</span>
                <span><b>chrF:</b> ${c.metrics.chrf}</span>
                <span><b>Token F1:</b> ${c.metrics.token_f1}</span>
                <span><b>Entity Match:</b> ${Math.round(c.metrics.entity_exact_match_ratio * 100)}%</span>
                <span><b>Confidence:</b> ${Math.round(c.agent_review.confidence_score * 100)}%</span>
            </div>
            <div style="font-size: 12px; color: #64748b; margin-bottom: 6px;">
                <strong>Round-Trip Back-Translation:</strong> <em>"${escapeHtml(c.back_translated_en)}"</em>
            </div>
            ${repairsHtml}
            ${warningsHtml}
        `;
        container.appendChild(item);
    });
}

// Filter clauses
function filterClauses(type) {
    currentFilter = type;
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    const btn = document.getElementById(`btnFilter${type.charAt(0).toUpperCase() + type.slice(1)}`);
    if (btn) btn.classList.add('active');
    if (currentResult) {
        renderClauseCards(currentResult.clauses, currentResult.target_language, currentResult.target_lang_code);
    }
}

// Switch View (Split / Translated Only / English Only)
function switchView(mode) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    
    const tabSplit = document.getElementById('tabSplit');
    const tabTrans = document.getElementById('tabTrans');
    const tabSource = document.getElementById('tabSource');
    const paneEn = document.getElementById('paneEnglish');
    const paneHi = document.getElementById('paneHindi');
    const dualPanes = document.getElementById('dualPanes');

    if (mode === 'split') {
        if (tabSplit) tabSplit.classList.add('active');
        paneEn.style.display = 'flex';
        paneHi.style.display = 'flex';
        dualPanes.style.gridTemplateColumns = '1fr 1fr';
    } else if (mode === 'hindi_only') {
        if (tabTrans) tabTrans.classList.add('active');
        paneEn.style.display = 'none';
        paneHi.style.display = 'flex';
        dualPanes.style.gridTemplateColumns = '1fr';
    } else if (mode === 'source_only') {
        if (tabSource) tabSource.classList.add('active');
        paneEn.style.display = 'flex';
        paneHi.style.display = 'none';
        dualPanes.style.gridTemplateColumns = '1fr';
    }
}

// Copy & Download Utilities
function copyHindiText() {
    if (!currentResult) return;
    const transText = currentResult.translated_document || currentResult.translated_document_kannada || currentResult.translated_document_tamil || currentResult.translated_document_malayalam || currentResult.translated_document_telugu || currentResult.translated_document_hindi || '';
    const langName = currentResult.target_language || 'Target';
    navigator.clipboard.writeText(transText)
        .then(() => alert(`✓ Verified ${langName} translation copied to clipboard!`))
        .catch(() => alert('Failed to copy to clipboard.'));
}

function copySourceText() {
    if (!currentResult) return;
    const sourceFull = currentResult.clauses.map(c => c.source_en).join('\n\n');
    navigator.clipboard.writeText(sourceFull)
        .then(() => alert('✓ English source text copied to clipboard!'))
        .catch(() => alert('Failed to copy to clipboard.'));
}

async function downloadTranslatedDoc() {
    if (!currentResult) return;
    const transText = currentResult.translated_document || currentResult.translated_document_kannada || currentResult.translated_document_tamil || currentResult.translated_document_malayalam || currentResult.translated_document_telugu || currentResult.translated_document_hindi || '';
    const langCode = currentResult.target_lang_code || 'hi';
    const filename = `Eng2Bharat_${langCode}_legal_translation.txt`;
    try {
        const resp = await fetch('/api/download/text', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: transText,
                filename: filename
            })
        });
        if (!resp.ok) throw new Error('Download failed');
        const blob = await resp.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (err) {
        alert(`Download failed: ${err.message}`);
    }
}

function downloadCertificate() {
    if (currentAudit && currentAudit.certificate_url) {
        window.open(currentAudit.certificate_url, '_blank');
    } else {
        alert('No audit certificate available for this document.');
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}
