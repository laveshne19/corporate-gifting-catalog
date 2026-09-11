# -*- coding: utf-8 -*-
"""
Detect and clear image assignments that are actually flat decorative shapes
(design backgrounds) rather than real product photos, using pixel colour
variance as a heuristic: genuine product photography has much higher
variance than a solid/near-solid design shape.
"""
import json, os
from PIL import Image
import numpy as np

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
IMG_DIR = os.path.join(BASE, "_catalog_build", "images")
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")

STD_THRESHOLD = 22  # below this, treat as a flat/decorative shape, not a product photo

def is_flat(path):
    try:
        with Image.open(path) as im:
            im = im.convert("RGB").resize((80, 80))
            arr = np.asarray(im).astype(float)
            std = arr.std()
            return std < STD_THRESHOLD, std
    except Exception:
        return False, None

def main():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    checked = flagged = 0
    flagged_examples = []
    for r in recs:
        rel = r.get("image_file")
        src = r.get("image_source") or ""
        if not rel or "catalogue PDF" not in src and "catalog PDF" not in src:
            continue  # only audit locally-extracted (non-web-scraped) images
        # image_file may already have been renamed to .jpg for the site copy;
        # the master pool keeps the original extension, so try both.
        candidates = [os.path.join(IMG_DIR, rel)]
        base, _ = os.path.splitext(rel)
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            candidates.append(os.path.join(IMG_DIR, base + ext))
        path = next((c for c in candidates if os.path.exists(c)), None)
        if not path:
            continue
        checked += 1
        flat, std = is_flat(path)
        if flat:
            flagged += 1
            if len(flagged_examples) < 15:
                flagged_examples.append((r["product_id"], r["brand"], r["product_name"], rel, round(std, 1)))
            r["image_file"] = ""
            r["image_source"] = ""

    json.dump(recs, open(os.path.join(OUT_DIR, "master_consolidated.json"), "w"), indent=1, ensure_ascii=False)
    print(f"Checked {checked} locally-extracted image assignments, flagged & cleared {flagged} as flat/decorative")
    for ex in flagged_examples:
        print(" ", ex)

if __name__ == "__main__":
    main()
