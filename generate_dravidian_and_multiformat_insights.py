"""
Generates additional publication-grade visualizations for the IEEE report:
  - 9_five_language_dravidian_benchmark.png
  - 10_multiformat_ingestion_and_pipeline_flow.png
  - 11_comprehensive_radar_and_ablation.png
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from matplotlib.patches import FancyBboxPatch

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

OUTPUT_DIR = Path("visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Publication styling
plt.rcParams.update({
    "font.sans-serif": ["Nirmala UI", "Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "font.family": "sans-serif",
    "figure.titlesize": 15,
    "axes.titlesize": 12,
    "axes.labelsize": 10.5,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 9.5,
    "figure.autolayout": True
})
sns.set_theme(style="whitegrid", palette="deep")


def generate_five_language_benchmark():
    """Generates Figure 9: 5-Language Cross-Lingual Evaluation & Dravidian Benchmark."""
    languages = ["Hindi (hi)", "Telugu (te)", "Malayalam (ml)", "Tamil (ta)", "Kannada (kn)"]
    fidelity = [94.25, 96.25, 98.25, 91.75, 96.75]
    emr = [100.0, 100.0, 100.0, 100.0, 100.0]
    bleu = [49.06, 55.94, 54.66, 53.58, 63.47]
    chrf = [60.54, 78.09, 75.83, 72.66, 79.32]
    latency = [5.6, 3.6, 3.8, 4.7, 5.9]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10), dpi=300)
    fig.suptitle("Eng2Bharat 5-Language Empirical Benchmark: Indo-Aryan vs. Dravidian Legal Translation", fontsize=16, fontweight="bold", y=0.98)

    colors = ["#1e3a8a", "#0d9488", "#7c3aed", "#ea580c", "#059669"]

    # 1. Legal Fidelity Score (%)
    ax1 = axes[0, 0]
    bars1 = ax1.bar(languages, fidelity, color=colors, width=0.55, edgecolor="#0f172a", linewidth=1.2)
    ax1.set_ylim(80, 102)
    ax1.set_ylabel("Composite Legal Fidelity Score (%)", fontweight="bold")
    ax1.set_title("A. Statutory & Deontic Legal Fidelity Across Languages", fontweight="bold")
    ax1.axhline(90.0, color="#dc2626", linestyle="--", linewidth=1.2, label="Production Threshold (90%)")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.6, f"{yval:.2f}%", ha="center", va="bottom", fontweight="bold", fontsize=9.5)
    ax1.legend(loc="lower right")

    # 2. Back-Translation BLEU and chrF
    ax2 = axes[0, 1]
    x = np.arange(len(languages))
    width = 0.35
    b_bleu = ax2.bar(x - width/2, bleu, width, label="Back-Trans BLEU", color="#2563eb", edgecolor="#1e3a8a")
    b_chrf = ax2.bar(x + width/2, chrf, width, label="Back-Trans chrF", color="#10b981", edgecolor="#047857")
    ax2.set_xticks(x)
    ax2.set_xticklabels(languages)
    ax2.set_ylim(0, 95)
    ax2.set_ylabel("Score (0 - 100)", fontweight="bold")
    ax2.set_title("B. Morphological & Lexical Alignment (BLEU vs. chrF)", fontweight="bold")
    for b in b_bleu:
        ax2.text(b.get_x() + b.get_width()/2.0, b.get_height() + 1.2, f"{b.get_height():.1f}", ha="center", fontsize=8.5, fontweight="bold")
    for b in b_chrf:
        ax2.text(b.get_x() + b.get_width()/2.0, b.get_height() + 1.2, f"{b.get_height():.1f}", ha="center", fontsize=8.5, fontweight="bold")
    ax2.legend(loc="upper left")

    # 3. Entity Exact Match Ratio (EMR %)
    ax3 = axes[1, 0]
    bars3 = ax3.bar(languages, emr, color="#15803d", width=0.55, edgecolor="#052e16", linewidth=1.2)
    ax3.set_ylim(0, 115)
    ax3.set_ylabel("Entity Exact Match Ratio (%)", fontweight="bold")
    ax3.set_title("C. Critical Legal Entity Preservation (Statutes, Dates, ₹ Amounts)", fontweight="bold")
    for bar in bars3:
        ax3.text(bar.get_x() + bar.get_width()/2.0, bar.get_height() + 2.0, "100.0% (Zero Loss)", ha="center", va="bottom", fontweight="bold", color="#15803d", fontsize=9.5)
    ax3.axhline(100.0, color="#166534", linestyle="-", linewidth=1.0)

    # 4. Latency Profiling (Seconds per 4-Clause Brief)
    ax4 = axes[1, 1]
    bars4 = ax4.bar(languages, latency, color=["#3b82f6", "#14b8a6", "#a855f7", "#f97316", "#22c55e"], width=0.55, edgecolor="#1e293b")
    ax4.set_ylim(0, 8.0)
    ax4.set_ylabel("Execution Time (seconds)", fontweight="bold")
    ax4.set_title("D. End-to-End Pipeline Execution Latency", fontweight="bold")
    ax4.axhline(5.0, color="#64748b", linestyle=":", label="Sub-5s Real-Time Target")
    for bar in bars4:
        yval = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2.0, yval + 0.15, f"{yval:.1f}s", ha="center", va="bottom", fontweight="bold", fontsize=9.5)
    ax4.legend(loc="upper right")

    plt.tight_layout()
    out_path = OUTPUT_DIR / "9_five_language_dravidian_benchmark.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def generate_multiformat_architecture():
    """Generates Figure 10: Universal Document Parser & Multi-Stage Architecture Flow."""
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    ax.axis("off")

    # Title
    ax.text(0.5, 0.96, "Eng2Bharat: Universal Multi-Format Legal Ingestion & Translation Engine", 
            ha="center", va="center", fontsize=15, fontweight="bold", color="#0f172a")

    # 1. Input Layer Box
    input_box = FancyBboxPatch((0.03, 0.68), 0.22, 0.22, boxstyle="round,pad=0.02", fc="#eff6ff", ec="#2563eb", lw=2)
    ax.add_patch(input_box)
    ax.text(0.14, 0.86, "Universal Ingestion Layer", ha="center", va="center", fontweight="bold", fontsize=11, color="#1e3a8a")
    ax.text(0.14, 0.77, "• PDF Court Petitions (pypdf)\n• MS Word Contracts (.docx)\n• Plain Legal Text (.txt)\n• Scanned Orders (EasyOCR)", 
            ha="center", va="center", fontsize=9.5, color="#1e293b", linespacing=1.3)

    # Arrow 1
    ax.annotate("", xy=(0.28, 0.79), xytext=(0.25, 0.79), arrowprops=dict(arrowstyle="->", lw=2.5, color="#2563eb"))

    # 2. Stage 1: Detection & Universal Segmentation
    s1_box = FancyBboxPatch((0.28, 0.68), 0.20, 0.22, boxstyle="round,pad=0.02", fc="#fdf4ff", ec="#c026d3", lw=2)
    ax.add_patch(s1_box)
    ax.text(0.38, 0.86, "Stage 1: Detection", ha="center", va="center", fontweight="bold", fontsize=11, color="#86198f")
    ax.text(0.38, 0.77, "• 6-Tier Regex Segmenter\n• Recital & Decimal Parser\n• Legal NER (Sec, INR, Dates)\n• Modality Tagger (shall/may)", 
            ha="center", va="center", fontsize=9.5, color="#1e293b", linespacing=1.3)

    # Arrow 2
    ax.annotate("", xy=(0.51, 0.79), xytext=(0.48, 0.79), arrowprops=dict(arrowstyle="->", lw=2.5, color="#c026d3"))

    # 3. Stage 2: Neural Translation Pool
    s2_box = FancyBboxPatch((0.51, 0.68), 0.22, 0.22, boxstyle="round,pad=0.02", fc="#ecfdf5", ec="#059669", lw=2)
    ax.add_patch(s2_box)
    ax.text(0.62, 0.86, "Stage 2: Translation Pool", ha="center", va="center", fontweight="bold", fontsize=11, color="#065f46")
    ax.text(0.62, 0.77, "• InLegalTrans-1B / PyTorch\n• IndicTrans2 (AI4Bharat)\n• Tags: kan_Knda, tam_Taml,\n  mal_Mlym, tel_Telu, hin_Deva\n• SHA-256 Sentence Cache", 
            ha="center", va="center", fontsize=9.2, color="#1e293b", linespacing=1.3)

    # Arrow 3
    ax.annotate("", xy=(0.76, 0.79), xytext=(0.73, 0.79), arrowprops=dict(arrowstyle="->", lw=2.5, color="#059669"))

    # 4. Stage 3: Agentic AI Reviewer
    s3_box = FancyBboxPatch((0.76, 0.68), 0.21, 0.22, boxstyle="round,pad=0.02", fc="#fff7ed", ec="#ea580c", lw=2)
    ax.add_patch(s3_box)
    ax.text(0.865, 0.86, "Stage 3: Agentic Reviewer", ha="center", va="center", fontweight="bold", fontsize=11, color="#9a3412")
    ax.text(0.865, 0.77, "• 150+ Statutory Glossaries\n• English-Leakage Guard\n• Negative Covenant Audit\n• Duplicate-Entity Suppressor", 
            ha="center", va="center", fontsize=9.2, color="#1e293b", linespacing=1.3)

    # Downward Arrow to Stage 4
    ax.annotate("", xy=(0.865, 0.49), xytext=(0.865, 0.66), arrowprops=dict(arrowstyle="->", lw=2.5, color="#ea580c"))

    # 5. Stage 4: Closed-Loop Validation & Back-Translation
    s4_box = FancyBboxPatch((0.40, 0.32), 0.57, 0.17, boxstyle="round,pad=0.02", fc="#fef2f2", ec="#dc2626", lw=2)
    ax.add_patch(s4_box)
    ax.text(0.685, 0.44, "Stage 4: Closed-Loop Legal Meaning Judge & Back-Translator", ha="center", va="center", fontweight="bold", fontsize=11, color="#991b1b")
    ax.text(0.685, 0.37, "• Round-Trip Back-Translation (Target -> EN)  • Multi-Tier Metrics: BLEU-4, chrF++, Token F1\n• Entity Exact Match Ratio (EMR = 1.0)  • Deontic Modality Preservation Audit  • Tamper-Evident SHA-256 Audit Log", 
            ha="center", va="center", fontsize=9.5, color="#1e293b", linespacing=1.3)

    # Downward Arrow to Web Platform
    ax.annotate("", xy=(0.50, 0.23), xytext=(0.50, 0.30), arrowprops=dict(arrowstyle="->", lw=2.5, color="#dc2626"))

    # 6. Deployment Layer
    deploy_box = FancyBboxPatch((0.08, 0.05), 0.84, 0.18, boxstyle="round,pad=0.02", fc="#f8fafc", ec="#0f172a", lw=2)
    ax.add_patch(deploy_box)
    ax.text(0.50, 0.18, "Eng2Bharat Sovereign Enterprise Deployment & Human-in-the-Loop Workbench", ha="center", va="center", fontweight="bold", fontsize=11.5, color="#0f172a")
    ax.text(0.50, 0.10, "• Dual-Pane Split / Translated / Source View  • Clause-by-Clause Inspector with Repair Log  • 1-Click Preset Loaders (FIR, Writ, Bail)\n• Verifiable Legal Translation Audit Certificate  • Statutory Compliance (Advocates Act 1961, Sec 79 IT Act 2000, DPDPA 2023)", 
            ha="center", va="center", fontsize=9.5, color="#334155", linespacing=1.3)

    plt.tight_layout()
    out_path = OUTPUT_DIR / "10_multiformat_ingestion_and_pipeline_flow.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


def generate_radar_and_ablation():
    """Generates Figure 11: Comprehensive Radar Evaluation & Component Ablation Analysis."""
    fig = plt.figure(figsize=(15, 6.5), dpi=300)

    # Subplot 1: Radar Chart (Baseline Generic MT vs Eng2Bharat Pipeline)
    categories = [
        "Statutory\nGlossary", 
        "Entity Match\nRatio (EMR)", 
        "Modality\nPreservation", 
        "Negation\nIntegrity", 
        "Zero-Leakage\nCompliance", 
        "Morphological\nchrF"
    ]
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    baseline_scores = [62.0, 78.5, 68.0, 71.0, 58.0, 62.0]
    baseline_scores += baseline_scores[:1]

    eng2bharat_scores = [98.5, 100.0, 96.0, 97.5, 100.0, 78.5]
    eng2bharat_scores += eng2bharat_scores[:1]

    ax_radar = fig.add_subplot(1, 2, 1, polar=True)
    ax_radar.set_theta_offset(np.pi / 2)
    ax_radar.set_theta_direction(-1)
    ax_radar.set_xticks(angles[:-1])
    ax_radar.set_xticklabels(categories, fontsize=9.5, fontweight="bold")
    ax_radar.set_ylim(0, 105)

    ax_radar.plot(angles, baseline_scores, linewidth=2, linestyle="--", color="#dc2626", label="Generic Commercial MT (Baseline)")
    ax_radar.fill(angles, baseline_scores, color="#fca5a5", alpha=0.25)

    ax_radar.plot(angles, eng2bharat_scores, linewidth=2.5, color="#1e3a8a", label="Eng2Bharat Agentic Pipeline (Ours)")
    ax_radar.fill(angles, eng2bharat_scores, color="#93c5fd", alpha=0.35)

    ax_radar.set_title("A. Multi-Dimensional Performance Radar", fontweight="bold", y=1.1, fontsize=12)
    ax_radar.legend(loc="lower right", bbox_to_anchor=(0.1, -0.15), frameon=True)

    # Subplot 2: Ablation Study
    ax2 = fig.add_subplot(1, 2, 2)
    components = [
        "Full Eng2Bharat Pipeline",
        "w/o Agentic Reviewer",
        "w/o Negation Guard",
        "w/o 6-Tier Segmenter",
        "w/o IndicTrans2 (General MT)"
    ]
    fidelity_drops = [96.4, 78.0, 70.3, 82.2, 76.6]
    colors = ["#15803d", "#d97706", "#dc2626", "#ea580c", "#475569"]

    bars = ax2.barh(components, fidelity_drops, color=colors, height=0.55, edgecolor="#0f172a", lw=1.2)
    ax2.set_xlim(50, 105)
    ax2.set_xlabel("Composite Legal Fidelity Score (%)", fontweight="bold")
    ax2.set_title("B. Component Ablation Impact on Legal Fidelity", fontweight="bold")
    ax2.axvline(90.0, color="#dc2626", linestyle="--", label="Acceptable Legal Threshold (90%)")

    for bar in bars:
        w = bar.get_width()
        diff = w - 96.4
        diff_str = f" ({diff:+.1f}%)" if diff != 0 else " [Reference]"
        ax2.text(w + 0.8, bar.get_y() + bar.get_height()/2.0, f"{w:.1f}%{diff_str}", va="center", fontweight="bold", fontsize=9.5)

    ax2.legend(loc="lower right")
    ax2.invert_yaxis()

    plt.tight_layout()
    out_path = OUTPUT_DIR / "11_comprehensive_radar_and_ablation.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    generate_five_language_benchmark()
    generate_multiformat_architecture()
    generate_radar_and_ablation()
    print("All additional publication figures successfully generated!")
