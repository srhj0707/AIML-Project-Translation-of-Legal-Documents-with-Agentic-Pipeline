import sys
from pptx import Presentation

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

prs = Presentation("C:/Users/jsair/Downloads/Project Template.pptx")
print(f"Total slides: {len(prs.slides)}")

for idx, slide in enumerate(prs.slides, 1):
    print(f"\n==========================================")
    print(f"SLIDE {idx}")
    print(f"==========================================")
    for s_idx, shape in enumerate(slide.shapes):
        t = ""
        if shape.has_text_frame:
            t = shape.text.replace("\n", " // ")[:80]
        elif shape.has_table:
            t = f"TABLE with {len(shape.table.rows)} rows, {len(shape.table.columns)} cols"
        print(f"Shape {s_idx}: [{shape.shape_type}] Left={shape.left.inches:.2f}\", Top={shape.top.inches:.2f}\", Width={shape.width.inches:.2f}\", Height={shape.height.inches:.2f}\" | Content: {t}")
