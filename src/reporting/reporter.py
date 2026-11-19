import json
from pathlib import Path
from typing import Dict, List, Any

class LegalTranslationReporter:
    """
    Generates comprehensive audit reports and dashboards for legal translation pipeline runs.
    Outputs JSON logs, Markdown summaries, and responsive visual HTML dashboards.
    """

    def generate_markdown_report(
        self, result: Dict[str, Any], title: str = "Legal Translation & Validation Audit Report"
    ) -> str:
        summary = result["document_summary"]
        status = result["overall_status"]
        clauses = result["clauses"]

        status_emoji = "✅" if status == "VERIFIED_READY" else "⚠️"

        lines = [
            f"# {title}",
            "",
            f"**Pipeline Verdict**: {status_emoji} `{status}`  ",
            f"**Total Clauses**: `{summary['total_clauses']}` | **Verified**: `{summary['verified_clauses_count']}` | **Flagged for Human Review**: `{summary['flagged_clauses_count']}`",
            "",
            "## 1. Executive Metric Summary",
            "",
            "| Evaluation Metric | Score | Benchmark Target | Interpretation |",
            "| :--- | :--- | :--- | :--- |",
            f"| **Legal Meaning Fidelity Score** | **{summary['avg_legal_fidelity_score']}%** | >= 90.0% | Evaluates preservation of legal duty, negation & meaning |",
            f"| **Entity Exact Match Rate** | **{summary['avg_entity_preservation_pct']}%** | 100.0% | Measures statutory sections, case numbers, dates & currency |",
            f"| **Back-Translation chrF** | **{summary['avg_back_trans_chrf']}** | >= 65.0 | Character-level n-gram morphological similarity |",
            f"| **Back-Translation BLEU** | **{summary['avg_back_trans_bleu']}** | >= 30.0 | Surface n-gram lexical overlap |",
            "",
            "## 2. Clause-by-Clause Translation & Audit Trace",
            ""
        ]

        for c in clauses:
            review_flag = "⚠️ **FLAGGED FOR HUMAN LEGAL REVIEW**" if c["requires_human_review"] else "✅ **VERIFIED**"
            risk_badge = f"`Risk: {c['risk_level'].upper()}`"

            lines.extend([
                f"### Clause {c['clause_id']} ({c['clause_type']}) - {risk_badge} {review_flag}",
                "",
                f"- **Source (EN)**: {c['source_en']}",
                f"- **Draft Hindi (NLP)**: {c['draft_hi']}",
                f"- **Verified Hindi (Agentic AI)**: {c['verified_hi']}",
                f"- **Back-Translated (EN)**: {c['back_translated_en']}",
                f"- **Validation Metrics**: BLEU: `{c['metrics']['bleu']}`, chrF: `{c['metrics']['chrf']}`, Entity Match: `{int(c['metrics']['entity_exact_match_ratio']*100)}%`",
                f"- **Judge Score**: `{c['judge_evaluation']['overall_fidelity_score']}%` ({c['judge_evaluation']['verdict']})",
                ""
            ])

            if c["agent_review"]["audit_log"]:
                lines.append("**Agentic Rectifications Applied:**")
                for entry in c["agent_review"]["audit_log"]:
                    lines.append(f"- *{entry['action']}*: {entry['details']}")
                lines.append("")

            if c["requires_human_review"]:
                lines.append("**Human Review Directives:**")
                for flag in c["agent_review"]["human_review_flags"]:
                    lines.append(f"- ⚠️ {flag}")
                for v in c["judge_evaluation"].get("violations", []):
                    lines.append(f"- ⚠️ [{v['dimension']}] {v['details']}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def generate_html_dashboard(
        self, result: Dict[str, Any], title: str = "Legal Translation Audit Dashboard"
    ) -> str:
        summary = result["document_summary"]
        status = result["overall_status"]
        clauses = result["clauses"]

        status_class = "status-verified" if status == "VERIFIED_READY" else "status-flagged"
        status_text = "VERIFIED READY" if status == "VERIFIED_READY" else "HUMAN REVIEW REQUIRED"

        clause_rows_html = []
        for c in clauses:
            badge_class = "badge-danger" if c["requires_human_review"] else "badge-success"
            badge_text = "NEEDS REVIEW" if c["requires_human_review"] else "VERIFIED"
            risk_class = "risk-" + c["risk_level"].lower()

            flags_html = ""
            if c["requires_human_review"]:
                flags_list = []
                for f in c["agent_review"]["human_review_flags"]:
                    flags_list.append(f"<li>{f}</li>")
                for v in c["judge_evaluation"].get("violations", []):
                    flags_list.append(f"<li><b>[{v['dimension']}]</b> {v['details']}</li>")
                flags_html = f"<div class='flag-box'><ul>{''.join(flags_list)}</ul></div>"

            repairs_html = ""
            if c["agent_review"]["audit_log"]:
                rep_list = []
                for r in c["agent_review"]["audit_log"]:
                    rep_list.append(f"<li><span class='action-pill'>{r['action']}</span> {r['details']}</li>")
                repairs_html = f"<div class='repairs-box'><small><b>Agentic AI Repairs:</b></small><ul>{''.join(rep_list)}</ul></div>"

            row = f"""
            <div class="clause-card {risk_class}">
                <div class="clause-header">
                    <div>
                        <span class="clause-id">{c['clause_id']}</span>
                        <span class="clause-type">[{c['clause_type'].replace('_', ' ').upper()}]</span>
                        <span class="risk-badge {risk_class}">RISK: {c['risk_level'].upper()}</span>
                    </div>
                    <div>
                        <span class="badge {badge_class}">{badge_text}</span>
                        <span class="fidelity-pill">Fidelity: {c['judge_evaluation']['overall_fidelity_score']}%</span>
                    </div>
                </div>

                <div class="clause-grid">
                    <div class="col-box">
                        <label>English Source (Input)</label>
                        <p class="text-source">{c['source_en']}</p>
                    </div>
                    <div class="col-box">
                        <label>Verified Hindi Translation (Agentic Output)</label>
                        <p class="text-hindi">{c['verified_hi']}</p>
                    </div>
                    <div class="col-box">
                        <label>Back-Translated English (Stage 3 Round-Trip)</label>
                        <p class="text-back">{c['back_translated_en']}</p>
                    </div>
                </div>

                <div class="metrics-row">
                    <span><b>BLEU:</b> {c['metrics']['bleu']}</span>
                    <span><b>chrF:</b> {c['metrics']['chrf']}</span>
                    <span><b>Token F1:</b> {c['metrics']['token_f1']}</span>
                    <span><b>Entity Match:</b> {int(c['metrics']['entity_exact_match_ratio']*100)}%</span>
                    <span><b>Confidence:</b> {int(c['agent_review']['confidence_score']*100)}%</span>
                </div>

                {repairs_html}
                {flags_html}
            </div>
            """
            clause_rows_html.append(row)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
    :root {{
        --primary: #1e3a8a;
        --primary-light: #3b82f6;
        --success: #15803d;
        --warning: #b45309;
        --danger: #b91c1c;
        --bg: #f8fafc;
        --card-bg: #ffffff;
        --border: #e2e8f0;
        --text: #0f172a;
        --text-muted: #64748b;
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: var(--bg);
        color: var(--text);
        margin: 0;
        padding: 24px;
        line-height: 1.5;
    }}
    .container {{
        max-width: 1280px;
        margin: 0 auto;
    }}
    header {{
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        color: white;
        padding: 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    header h1 {{ margin: 0 0 8px 0; font-size: 26px; }}
    header p {{ margin: 0; opacity: 0.9; }}
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }}
    .kpi-card {{
        background: var(--card-bg);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid var(--border);
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .kpi-card h3 {{
        margin: 0 0 6px 0;
        font-size: 13px;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .kpi-card .value {{
        font-size: 28px;
        font-weight: 700;
        color: var(--primary);
    }}
    .clause-card {{
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .clause-card.risk-critical {{ border-left: 6px solid var(--danger); }}
    .clause-card.risk-elevated {{ border-left: 6px solid var(--warning); }}
    .clause-card.risk-standard {{ border-left: 6px solid var(--primary-light); }}
    .clause-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--border);
        padding-bottom: 12px;
        margin-bottom: 16px;
    }}
    .clause-id {{ font-weight: 800; font-size: 16px; margin-right: 8px; }}
    .clause-type {{ color: var(--text-muted); font-size: 13px; margin-right: 8px; }}
    .risk-badge {{
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
    }}
    .risk-badge.risk-critical {{ background: #fee2e2; color: #991b1b; }}
    .risk-badge.risk-elevated {{ background: #fef3c7; color: #92400e; }}
    .risk-badge.risk-standard {{ background: #e0f2fe; color: #075985; }}
    .badge {{
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
    }}
    .badge-success {{ background: #dcfce7; color: #166534; }}
    .badge-danger {{ background: #fee2e2; color: #991b1b; }}
    .fidelity-pill {{
        background: #f1f5f9;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }}
    .clause-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 16px;
        margin-bottom: 16px;
    }}
    @media (max-width: 900px) {{
        .clause-grid {{ grid-template-columns: 1fr; }}
    }}
    .col-box {{
        background: #f8fafc;
        padding: 12px 14px;
        border-radius: 6px;
        border: 1px solid var(--border);
    }}
    .col-box label {{
        display: block;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 6px;
    }}
    .text-source {{ color: #1e293b; font-size: 14px; margin: 0; }}
    .text-hindi {{ color: #0f172a; font-size: 15px; font-weight: 500; margin: 0; line-height: 1.6; }}
    .text-back {{ color: #334155; font-size: 14px; margin: 0; }}
    .metrics-row {{
        display: flex;
        gap: 16px;
        font-size: 13px;
        background: #f1f5f9;
        padding: 8px 14px;
        border-radius: 6px;
        margin-bottom: 12px;
        flex-wrap: wrap;
    }}
    .repairs-box {{
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 10px;
        font-size: 13px;
    }}
    .repairs-box ul {{ margin: 4px 0 0 0; padding-left: 20px; }}
    .action-pill {{
        background: #dbeafe;
        color: #1e40af;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
    }}
    .flag-box {{
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 13px;
        color: #991b1b;
    }}
    .flag-box ul {{ margin: 4px 0 0 0; padding-left: 20px; }}
</style>
</head>
<body>
<div class="container">
    <header>
        <h1>{title}</h1>
        <p>Agentic AI + NLP Legal Document Translation Pipeline | English to Hindi with Back-Translation Validation</p>
    </header>

    <div class="kpi-grid">
        <div class="kpi-card">
            <h3>Overall Status</h3>
            <div class="value" style="font-size: 20px; color: {'#15803d' if status == 'VERIFIED_READY' else '#b45309'};">{status_text}</div>
        </div>
        <div class="kpi-card">
            <h3>Total Clauses</h3>
            <div class="value">{summary['total_clauses']}</div>
        </div>
        <div class="kpi-card">
            <h3>Human Review Flags</h3>
            <div class="value" style="color: {'#b91c1c' if summary['flagged_clauses_count'] > 0 else '#15803d'};">{summary['flagged_clauses_count']}</div>
        </div>
        <div class="kpi-card">
            <h3>Legal Fidelity</h3>
            <div class="value">{summary['avg_legal_fidelity_score']}%</div>
        </div>
        <div class="kpi-card">
            <h3>Entity Exact Match</h3>
            <div class="value">{summary['avg_entity_preservation_pct']}%</div>
        </div>
        <div class="kpi-card">
            <h3>Back-Trans chrF</h3>
            <div class="value">{summary['avg_back_trans_chrf']}</div>
        </div>
    </div>

    <h2>Clause-by-Clause Translation & Audit Logs</h2>
    {''.join(clause_rows_html)}
</div>
</body>
</html>"""
        return html

    def save_reports(
        self, result: Dict[str, Any], output_prefix: str = "legal_translation_audit", output_dir: str = "./reports"
    ) -> Dict[str, str]:
        """Saves JSON, Markdown, and HTML reports to disk."""
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        json_file = out_path / f"{output_prefix}.json"
        md_file = out_path / f"{output_prefix}.md"
        html_file = out_path / f"{output_prefix}.html"

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        md_content = self.generate_markdown_report(result)
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        html_content = self.generate_html_dashboard(result)
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        return {
            "json_path": str(json_file),
            "markdown_path": str(md_file),
            "html_path": str(html_file)
        }
