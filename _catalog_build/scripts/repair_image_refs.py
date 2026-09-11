# -*- coding: utf-8 -*-
"""Fix image_file references that were mistakenly renamed to .jpg when the
actual file in the master image pool still has its original extension."""
import json, os

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
IMG_DIR = os.path.join(BASE, "_catalog_build", "images")
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")

recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
fixed = cleared = ok = 0

for r in recs:
    rel = r.get("image_file")
    if not rel:
        continue
    full = os.path.join(IMG_DIR, rel)
    if os.path.exists(full):
        ok += 1
        continue
    base, ext = os.path.splitext(rel)
    found = None
    for cand_ext in (".png", ".jpeg", ".jpg", ".webp", ".PNG", ".JPG"):
        cand = os.path.join(IMG_DIR, base + cand_ext)
        if os.path.exists(cand):
            found = base + cand_ext
            break
    if found:
        r["image_file"] = found
        fixed += 1
    else:
        r["image_file"] = ""
        r["image_source"] = ""
        cleared += 1

json.dump(recs, open(os.path.join(OUT_DIR, "master_consolidated.json"), "w"), indent=1, ensure_ascii=False)
print(f"OK (already valid): {ok}, Fixed (extension corrected): {fixed}, Cleared (truly missing): {cleared}")
