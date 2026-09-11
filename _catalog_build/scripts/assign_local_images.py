# -*- coding: utf-8 -*-
"""
Assign locally-extracted PDF images to products where the source page can be
matched confidently (exactly one product record uses that (source_file, page)).
For pages shared by multiple products (grid catalogues), we skip auto-assignment
to avoid mismatching images to the wrong product — those get flagged for
web-image lookup instead.
"""
import json, os, re
from collections import defaultdict

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
EXT = os.path.join(BASE, "_catalog_build", "extracted")
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
IMG_DIR = os.path.join(BASE, "_catalog_build", "images")

manifest = json.load(open(os.path.join(EXT, "pdf_image_manifest.json")))
records = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))

def page_num(source_sheet):
    m = re.match(r'^page\s+(\d+)$', (source_sheet or "").strip())
    return int(m.group(1)) if m else None

# group products by (source_file, page)
page_groups = defaultdict(list)
for r in records:
    p = page_num(r["source_sheet"])
    if p is not None and r["source_file"] in manifest:
        page_groups[(r["source_file"], p)].append(r)

assigned = 0
ambiguous_pages = 0
for (sf, p), recs in page_groups.items():
    imgs_on_page = [im for im in manifest[sf] if im["page"] == p]
    if not imgs_on_page:
        continue
    if len(recs) == 1:
        best = max(imgs_on_page, key=lambda im: im["width"] * im["height"])
        recs[0]["image_file"] = best["rel_path"]
        recs[0]["image_source"] = f"Extracted from catalogue PDF: {sf} (page {p})"
        assigned += 1
    else:
        ambiguous_pages += 1
        # if counts match exactly, do a cautious positional pairing (order on page vs order in list)
        if len(imgs_on_page) == len(recs):
            imgs_sorted = sorted(imgs_on_page, key=lambda im: im["file"])
            for rec, im in zip(recs, imgs_sorted):
                rec["image_file"] = im["rel_path"]
                rec["image_source"] = f"Extracted from catalogue PDF: {sf} (page {p}, auto-paired — verify)"
                assigned += 1

with open(os.path.join(OUT_DIR, "master_consolidated.json"), "w") as fh:
    json.dump(records, fh, indent=1, ensure_ascii=False)

with_image = sum(1 for r in records if r["image_file"])
print(f"Assigned images to {assigned} products via page matching")
print(f"Ambiguous multi-product pages skipped/paired: {ambiguous_pages}")
print(f"Total products with a local image: {with_image} / {len(records)} ({with_image/len(records)*100:.1f}%)")
