"""
Generates a publication-grade system architecture diagram for the legal translation presentation.
Saves to visualizations/0_system_architecture.png.
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

OUTPUT_PATH = Path("visualizations/0_system_architecture.png")

fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis("off")

# Colors
navy = "#1e3a8a"
blue = "#2563eb"
green = "#059669"
amber = "#d97706"
purple = "#7c3aed"
slate = "#334155"
bg_light = "#f8fafc"

# Title banner
fig.text(0.5, 0.94, "NyayaTrans AI: Resilient Multi-Agent Hybrid NLP Architecture",
         ha="center", fontsize=15, fontweight="bold", color="#0f172a")
fig.text(0.5, 0.90, "End-to-End English-to-Indian Regional Languages Legal Translation Pipeline",
         ha="center", fontsize=10, fontstyle="italic", color="#475569")

def draw_box(x, y, w, h, title, subtitle, color, text_color="white"):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.15",
        ec=color, fc=color,
        mutation_aspect=1.0, lw=1.5
    )
    ax.add_patch(rect)
    ax.text(x + w/2, y + h*0.65, title, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=text_color)
    ax.text(x + w/2, y + h*0.30, subtitle, ha="center", va="center",
            fontsize=8.0, color="#f1f5f9" if text_color == "white" else "#334155")

def draw_arrow(x1, y1, x2, y2, label=""):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color="#0f172a", lw=2.0, mutation_scale=15)
    )
    if label:
        ax.text((x1 + x2)/2, (y1 + y2)/2 + 0.18, label, ha="center", fontsize=8, fontweight="bold", color="#0f172a")

# Top Row
# Box 1: Input Document
draw_box(0.5, 4.8, 3.0, 1.2, "1. Legal Document Input", "Notices, Bail Orders, MSAs, Acts\n(Authentic Pleadings & Averments)", navy)

# Box 2: 6-Tier Segmenter
draw_box(4.5, 4.8, 3.0, 1.2, "2. 6-Tier Clause Segmenter", "Hyphenated Points (1-), Decimals (1.1),\nRecitals (WHEREAS) & Entity Tagging", blue)

# Box 3: Translation Pool
draw_box(8.5, 4.8, 3.0, 1.2, "3. Resilient Neural Pool", "PyTorch Legal Seq2Seq + IndicTrans2\nMulti-Provider Pool & SHA-256 Cache", green)

draw_arrow(3.5, 5.4, 4.5, 5.4, "Raw Text")
draw_arrow(7.5, 5.4, 8.5, 5.4, "Numbered Clauses")

# Vertical Arrow down from Box 3 to Box 4
draw_arrow(10.0, 4.8, 10.0, 3.4, "Draft Translations")

# Bottom Row
# Box 4: Agentic Reviewer
draw_box(8.5, 2.0, 3.0, 1.2, "4. Agentic Legal Reviewer", "Devanagari/Telugu Glossaries (200+)\nHigh-Register Terms & Entity Alignment", purple)

# Box 5: Meaning Judge
draw_box(4.5, 2.0, 3.0, 1.2, "5. Legal Meaning Judge", "Round-Trip Back-Translation Audit\nEPR (100%), MIR (100%), Negation Check", amber)

# Box 6: Output / UI
draw_box(0.5, 2.0, 3.0, 1.2, "6. Certified Court Delivery", "Dual-Pane Web UI, Audit Certificate,\nBCI/DPDPA 2023 Statutory Disclaimers", slate)

draw_arrow(8.5, 2.6, 7.5, 2.6, "Refined Text")
draw_arrow(4.5, 2.6, 3.5, 2.6, "VERIFIED_READY (LFS ≥ 90%)")

# Add Guardrail Badge at Center
center_box = patches.FancyBboxPatch(
    (4.6, 0.4), 2.8, 0.9,
    boxstyle="round,pad=0.1",
    ec="#dc2626", fc="#fef2f2", lw=1.5
)
ax.add_patch(center_box)
ax.text(6.0, 0.95, "English-Leakage Guard (<20% Latin)", ha="center", fontsize=8.5, fontweight="bold", color="#991b1b")
ax.text(6.0, 0.65, "Automatic fallback if translation leaks English", ha="center", fontsize=7.5, color="#b91c1c")

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=300)
plt.close()
print(f"[+] Successfully generated architecture diagram: {OUTPUT_PATH}")
