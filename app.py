"""
Full-Stack Web Application for Legal Translation Agent (NyayaTrans AI).
Equipped with:
  - Role-based Authentication & Rate Limiting (SecurityAuthManager)
  - Tamper-Evident Audit Logging & Digital Certification (LegalAuditLogger)
  - Statutory Legal Disclaimers (Advocates Act 1961, Section 79 IT Act 2000, DPDPA 2023)
  - Real PyTorch Trained Model & Authenticated API Status Inspection
  - Reference-Based Evaluation vs. Human Gold Standard (MILPaC Benchmark)
  - Unseen Real-World Legal Document Presets (FIR, Writ Petition, Lok Adalat Award)
"""

import os
import io
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, Response

from src.pipeline.legal_agent_orchestrator import LegalAgentOrchestrator
from src.reporting.reporter import LegalTranslationReporter
from src.security.auth import SecurityAuthManager
from src.security.audit_logger import LegalAuditLogger
from src.validation.reference_evaluator import LegalReferenceEvaluator
from src.utils.document_parser import parse_legal_document

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

# Initialize Core Services
orchestrator = LegalAgentOrchestrator()
reporter = LegalTranslationReporter()
auth_manager = SecurityAuthManager()
audit_logger = LegalAuditLogger()
reference_evaluator = LegalReferenceEvaluator()

SAMPLE_DIR = Path(__file__).resolve().parent / "data" / "raw"

def get_client_ip():
    """Extracts client IP address safely."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "eng2bharat-legal-agent",
        "app_title": "Eng2भारत",
        "version": "3.0.0-enterprise",
        "compliance": ["DPDPA-2023", "IT-Act-Sec79", "BCI-Advocates-Act-1961"]
    })

@app.route("/api/parse-document", methods=["POST"])
def parse_uploaded_document():
    """Extracts text from uploaded .txt, .pdf, .docx, or image file for live client preview."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"error": "No file selected."}), 400
    try:
        file_bytes = uploaded_file.read()
        text, doc_format = parse_legal_document(file_bytes, uploaded_file.filename)
        return jsonify({
            "success": True,
            "filename": uploaded_file.filename,
            "format": doc_format,
            "text": text,
            "character_count": len(text),
            "word_count": len(text.split())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/model/status", methods=["GET"])
def model_status():
    """Returns runtime status of local PyTorch checkpoint and authenticated API backends."""
    ckpt_path = Path(__file__).resolve().parent / "checkpoints" / "legal_pytorch_model" / "best_legal_model.pt"
    summary_path = Path(__file__).resolve().parent / "checkpoints" / "legal_pytorch_model" / "training_summary.json"
    
    training_summary = {}
    if summary_path.exists():
        try:
            import json
            with open(summary_path, "r", encoding="utf-8") as f:
                training_summary = json.load(f)
        except Exception:
            pass

    indictrans2_status = orchestrator.nlp_engine.indictrans2.get_status() if (hasattr(orchestrator.nlp_engine, "indictrans2") and orchestrator.nlp_engine.indictrans2) else None

    return jsonify({
        "trained_pytorch_model": {
            "is_deployed": ckpt_path.exists(),
            "checkpoint_path": str(ckpt_path) if ckpt_path.exists() else None,
            "training_summary": training_summary
        },
        "indictrans2_engine": indictrans2_status,
        "supported_languages": {
            "hi": "Hindi (हिंदी - Devanagari)",
            "te": "Telugu (తెలుగు - Dravidian)",
            "ml": "Malayalam (മലയാളം - Dravidian)",
            "ta": "Tamil (தமிழ் - Dravidian)",
            "kn": "Kannada (ಕನ್ನಡ - Dravidian)"
        },
        "authenticated_backends": {
            "gemini_api_configured": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")),
            "google_cloud_translate_configured": bool(os.environ.get("GOOGLE_TRANSLATE_API_KEY")),
            "deepl_configured": bool(os.environ.get("DEEPL_API_KEY"))
        },
        "cache_entries_count": len(orchestrator.nlp_engine._cache),
        "dataset_benchmark": "MILPaC (1,185 pairs across Acts, CCI FAQs, IP)"
    })

@app.route("/api/auth/register-key", methods=["POST"])
def register_key():
    """Issues a new production API key for authorized legal entities."""
    data = request.get_json() or {}
    user_name = data.get("name", "Legal Practitioner")
    role = data.get("role", "ADVOCATE")
    new_key = auth_manager.register_api_key(user_name, role)
    return jsonify({
        "success": True,
        "api_key": new_key,
        "assigned_role": role,
        "rate_limit_per_minute": 60,
        "notice": "Store this key securely. Include via header: 'X-API-Key: <key>'"
    })

@app.route("/api/sample/<sample_type>", methods=["GET"])
def get_sample(sample_type):
    """Provides preset test legal documents across criminal, civil, corporate, and statutory sectors."""
    sample_files = {
        "legal_notice": SAMPLE_DIR / "legal_notice_sample.txt",
        "bail_order": SAMPLE_DIR / "bail_order_sample.txt",
        "commercial_contract": SAMPLE_DIR / "commercial_contract_sample.txt",
        "fir": SAMPLE_DIR / "unseen_fir_sample.txt",
        "writ_petition": SAMPLE_DIR / "unseen_writ_petition_sample.txt",
        "lok_adalat": SAMPLE_DIR / "unseen_lok_adalat_award_sample.txt",
        "statutory_act": None
    }

    if sample_type == "statutory_act":
        sample_text = (
            "1. Short title and commencement.\n"
            "(1) This Act may be called the Right to Information Act, 2005.\n"
            "(2) It extends to the whole of India.\n"
            "(3) The provisions of sub-section (1) of section 4, sub-sections (1) and (2) of section 5, "
            "sections 12, 13, 15, 16, 24, 27 and 28 shall come into force at once.\n\n"
            "2. Obligations of public authorities.\n"
            "(1) Every public authority shall maintain all its records duly catalogued and indexed.\n"
            "(2) No public authority shall refuse access to information except as exempted under Section 8 of this Act."
        )
        return jsonify({"title": "Right to Information Act Sample", "text": sample_text})

    target_file = sample_files.get(sample_type)
    if target_file and target_file.exists():
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({
            "title": sample_type.replace("_", " ").title(),
            "text": content
        })

    return jsonify({"error": f"Sample type '{sample_type}' not found"}), 404

@app.route("/api/translate", methods=["POST"])
def translate_document():
    """Translates legal document with authentication, audit logging, and compliance certification."""
    start_time = time.time()
    client_ip = get_client_ip()

    # 1. Authentication & Rate-Limiting Check
    api_key = request.headers.get("X-API-Key")
    session_token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    is_auth_ok, auth_msg, user_ctx = auth_manager.authenticate_request(
        api_key=api_key,
        session_token=session_token,
        client_ip=client_ip
    )
    if not is_auth_ok:
        return jsonify({"error": auth_msg}), 429 if "rate limit" in auth_msg.lower() else 401

    # 2. Extract Document Content & Target Language
    doc_text = ""
    target_lang = request.args.get("target_lang") or "hi"
    doc_format_label = None

    if "file" in request.files:
        uploaded_file = request.files["file"]
        if uploaded_file.filename != "":
            try:
                file_bytes = uploaded_file.read()
                doc_text, doc_format_label = parse_legal_document(file_bytes, uploaded_file.filename)
            except Exception as parse_err:
                return jsonify({"error": f"Failed to parse uploaded document ({uploaded_file.filename}): {str(parse_err)}"}), 400
        target_lang = request.form.get("target_lang") or target_lang
    elif request.is_json:
        data = request.get_json()
        doc_text = data.get("text", "")
        target_lang = data.get("target_lang") or target_lang
    else:
        doc_text = request.form.get("text", "")
        target_lang = request.form.get("target_lang") or target_lang

    target_lang = target_lang.lower().strip()
    if target_lang not in ["hi", "te", "ml", "ta", "kn"]:
        target_lang = "hi"

    if not doc_text or not doc_text.strip():
        return jsonify({"error": "No document text or file provided for translation."}), 400

    # 3. Execute End-to-End Multi-Level Pipeline
    try:
        result = orchestrator.process_document(doc_text, target_lang=target_lang)
        elapsed = time.time() - start_time
        
        # 4. Record Audit Log & Generate Verifiable Certificate
        summary = result["document_summary"]
        overall_status = result["overall_status"]
        audit_entry = audit_logger.record_transaction(
            user_context=user_ctx,
            source_text=doc_text,
            translated_text=result.get("translated_document", result.get("translated_document_hindi", "")),
            clauses_count=summary["total_clauses"],
            execution_time_seconds=elapsed,
            overall_status=overall_status,
            audit_metrics=summary,
            client_ip=client_ip
        )
        certificate_text = audit_logger.generate_certificate(audit_entry)

        return jsonify({
            "success": True,
            "result": result,
            "audit": {
                "transaction_id": audit_entry["transaction_id"],
                "execution_time_seconds": audit_entry["execution_time_seconds"],
                "certificate_url": f"/api/certificate/{audit_entry['transaction_id']}",
                "certificate_text": certificate_text
            },
            "disclaimer": audit_logger.STATUTORY_DISCLAIMER
        })

    except Exception as e:
        return jsonify({"error": f"Pipeline processing failed: {str(e)}"}), 500

@app.route("/api/certificate/<tx_id>", methods=["GET"])
def get_certificate(tx_id):
    """Retrieves the official Digital Translation Certificate for a transaction."""
    import json
    if not audit_logger.audit_file.exists():
        return jsonify({"error": "No audit trail records found."}), 404

    target_record = None
    with open(audit_logger.audit_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                if rec.get("transaction_id") == tx_id:
                    target_record = rec
                    break

    if not target_record:
        return jsonify({"error": f"Transaction ID '{tx_id}' not found in audit logs."}), 404

    cert_text = audit_logger.generate_certificate(target_record)
    if request.args.get("format") == "json":
        return jsonify(target_record)

    return Response(cert_text, mimetype="text/plain; charset=utf-8")

@app.route("/api/benchmark/reference", methods=["GET", "POST"])
def benchmark_reference():
    """Runs gold-standard evaluation on held-out MILPaC test split."""
    count = int(request.args.get("count", 10))
    res = reference_evaluator.benchmark_on_test_split(orchestrator.nlp_engine, max_samples=count)
    return jsonify(res)

@app.route("/api/download/text", methods=["POST"])
def download_translated_text():
    data = request.get_json() or {}
    translated_text = data.get("text", "")
    filename = data.get("filename", "translated_document_hindi.txt")

    if not translated_text:
        return jsonify({"error": "No text provided to download"}), 400

    buffer = io.BytesIO()
    buffer.write(translated_text.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="text/plain; charset=utf-8"
    )

@app.route("/api/visualizations/<path:filename>", methods=["GET"])
def get_visualization(filename):
    viz_dir = Path(__file__).resolve().parent / "visualizations"
    target = (viz_dir / filename).resolve()
    if target.exists() and target.is_file() and str(target).startswith(str(viz_dir.resolve())):
        return send_file(target, mimetype="image/png")
    return jsonify({"error": f"Visualization '{filename}' not found"}), 404

@app.route("/api/visualizations", methods=["GET"])
def list_visualizations():
    viz_dir = Path(__file__).resolve().parent / "visualizations"
    files = [f.name for f in sorted(viz_dir.glob("*.png"))]
    return jsonify({"visualizations": files, "count": len(files)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n==========================================================")
    print(f" Eng2भारत Enterprise Legal Translation Server Running!")
    print(f" Access URL: http://localhost:{port}")
    print(f"==========================================================\n")
    app.run(host="127.0.0.1", port=port, debug=False)
