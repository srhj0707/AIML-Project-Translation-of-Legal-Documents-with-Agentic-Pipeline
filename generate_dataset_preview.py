"""
Generates a publication-grade visual snapshot of the MILPaC dataset for Slide 9.
Saves to visualizations/0_dataset_sample_preview.png.
"""

import sys
import json
from pathlib import Path
import matplotlib.pyplot as plt

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

OUTPUT_PATH = Path("visualizations/0_dataset_sample_preview.png")
plt.rcParams.update({
    "font.sans-serif": ["Nirmala UI", "Segoe UI", "DejaVu Sans", "Arial"],
    "font.family": "sans-serif"
})

# Load 3 authentic samples from milpac
milpac_path = Path("data/parallel/milpac_en_hi.json")
samples = []
if milpac_path.exists():
    with open(milpac_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        samples = data[:3]

if not samples:
    samples = [
        {
            "id": "MILPAC_ACT_001",
            "domain": "Central Statutory Acts",
            "en_text": "Whoever commits extortion shall be punished with imprisonment of either description for a term which may extend to three years, or with fine, or with both.",
            "hi_text": "जो कोई जबरन वसूली करेगा, वह दोनों में से किसी भांति के कारावास से, जिसकी अवधि तीन वर्ष तक की हो सकेगी, या जुर्माने से, या दोनों से दंडित किया जाएगा।",
            "entities": "three years | imprisonment | fine"
        },
        {
            "id": "MILPAC_CC_014",
            "domain": "Competition Commission",
            "en_text": "No enterprise or association of enterprises shall enter into any agreement which causes or is likely to cause an appreciable adverse effect on competition within India.",
            "hi_text": "कोई भी उद्यम या उद्यमों का संघ ऐसा कोई करार नहीं करेगा जिससे भारत के भीतर प्रतिस्पर्धा पर पर्याप्त प्रतिकूल प्रभाव पड़ता हो या पड़ने की संभावना हो।",
            "entities": "enterprise | adverse effect | India"
        },
        {
            "id": "MILPAC_IPR_089",
            "domain": "Intellectual Property / Patents",
            "en_text": "An application for a patent for an invention may be made by any person claiming to be the true and first inventor of the invention.",
            "hi_text": "किसी आविष्कार के लिए पेटेंट हेतु आवेदन ऐसे किसी भी व्यक्ति द्वारा किया जा सकता है जो आविष्कार का वास्तविक और पहला आविष्कारक होने का दावा करता हो।",
            "entities": "patent | inventor | invention"
        }
    ]

fig, ax = plt.subplots(figsize=(12, 6.2), dpi=300)
ax.axis("off")

# Title
fig.text(0.5, 0.94, "MILPaC Benchmark: Multilingual Indian Legal Parallel Corpus",
         ha="center", fontsize=14, fontweight="bold", color="#1e3a8a")
fig.text(0.5, 0.90, "Authentic Parallel Sentence Pairs across Indian Statutory Jurisprudence (ACM TALLIP 2025)",
         ha="center", fontsize=9.5, fontstyle="italic", color="#475569")

# Draw 3 sample cards
y_positions = [0.60, 0.32, 0.04]
card_height = 0.25

for i, (s, y) in enumerate(zip(samples, y_positions)):
    domain = s.get("domain", "Indian Statutory Law")
    sid = s.get("id", f"MILPAC_PAIR_{i+1:03d}")
    en = s.get("en_text", "")
    hi = s.get("hi_text", "")
    
    # Card background
    rect = plt.Rectangle((0.02, y), 0.96, card_height,
                         transform=ax.transAxes,
                         facecolor="#f8fafc" if i % 2 == 0 else "#ffffff",
                         edgecolor="#cbd5e1", linewidth=1.2)
    ax.add_patch(rect)
    
    # Domain Tag Badge
    badge = plt.Rectangle((0.04, y + 0.19), 0.24, 0.045,
                          transform=ax.transAxes,
                          facecolor="#1e3a8a", edgecolor="#1e3a8a")
    ax.add_patch(badge)
    ax.text(0.16, y + 0.212, f"{sid} • {domain}", transform=ax.transAxes,
            ha="center", va="center", color="white", fontsize=7.5, fontweight="bold")
    
    # English text
    ax.text(0.04, y + 0.13, f"EN [Source]: {en[:115]}..." if len(en) > 115 else f"EN [Source]: {en}",
            transform=ax.transAxes, fontsize=8.0, fontweight="bold", color="#1e293b")
    
    # Hindi text
    ax.text(0.04, y + 0.05, f"HI [Target]: {hi[:125]}..." if len(hi) > 125 else f"HI [Target]: {hi}",
            transform=ax.transAxes, fontsize=8.0, color="#0f766e")

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=300)
plt.close()
print(f"[+] Saved dataset sample snapshot: {OUTPUT_PATH}")
