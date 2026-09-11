# -*- coding: utf-8 -*-
"""
Select a curated subset of products for web-image enrichment (Apify Google Images)
and a full list of products missing MRP for web MRP verification.
Curation goal: broad, representative gift-catalog coverage across every brand and
category, not exhaustive coverage of every SKU/colour variant (which would require
tens of thousands of individual scrapes).
"""
import json, os, re
from collections import defaultdict

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")

TARGET_IMAGE_COUNT = 1800
MAX_PER_BRAND_FRACTION = 0.18  # no single brand can exceed 18% of the curated image batch

EXCLUDE_CATEGORY_KEYWORDS = ["air conditioner", "odu", "idu split"]

def base_variant_key(brand, name):
    n = name.lower()
    n = re.sub(r'\b(black|white|blue|red|green|grey|gray|silver|gold|pink|purple|yellow|'
               r'brown|beige|cream|orange|navy|maroon|teal|rose|mint|copper|bronze|midnight|'
               r'charcoal|onyx|denim|mocha|espresso|premium|classic)\b', '', n)
    n = re.sub(r'[^a-z0-9]+', '', n)
    return (brand.lower(), n[:24])

def main():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))

    missing_mrp = [r for r in recs if r["mrp"] is None]
    print(f"Products missing MRP: {len(missing_mrp)}")

    needs_image = [r for r in recs if not r.get("image_file")]
    print(f"Products without a local image: {len(needs_image)}")

    # group by base model so we scrape ~1 image per distinct product family, not per colour
    groups = defaultdict(list)
    for r in needs_image:
        cat_l = r["category"].lower()
        if any(k in cat_l for k in EXCLUDE_CATEGORY_KEYWORDS):
            continue
        key = base_variant_key(r["brand"], r["product_name"])
        groups[key].append(r)
    print(f"Distinct product-family groups needing an image: {len(groups)}")

    # priority: has MRP (real catalog item) first, then by brand round-robin for diversity
    by_brand_groups = defaultdict(list)
    for key, members in groups.items():
        # representative = the one with MRP if available, else first
        rep = next((m for m in members if m["mrp"] is not None), members[0])
        by_brand_groups[rep["brand"]].append((rep, members))

    max_per_brand = max(20, int(TARGET_IMAGE_COUNT * MAX_PER_BRAND_FRACTION))
    selected = []
    brand_list = list(by_brand_groups.keys())
    idx = {b: 0 for b in brand_list}
    # sort each brand's candidates: priced items first
    for b in brand_list:
        by_brand_groups[b].sort(key=lambda t: (t[0]["mrp"] is None, t[0]["product_name"]))

    while len(selected) < TARGET_IMAGE_COUNT:
        progressed = False
        for b in brand_list:
            lst = by_brand_groups[b]
            i = idx[b]
            if i >= len(lst) or i >= max_per_brand:
                continue
            selected.append(lst[i])
            idx[b] = i + 1
            progressed = True
            if len(selected) >= TARGET_IMAGE_COUNT:
                break
        if not progressed:
            break

    print(f"Curated for image scraping: {len(selected)} product families "
          f"(covering {sum(len(m) for _, m in selected)} total SKU rows once variants share the image)")

    curation = []
    for rep, members in selected:
        curation.append({
            "brand": rep["brand"],
            "product_name": rep["product_name"],
            "category": rep["category"],
            "mrp": rep["mrp"],
            "member_ids": [m["product_id"] for m in members],
        })

    with open(os.path.join(OUT_DIR, "image_curation_list.json"), "w") as fh:
        json.dump(curation, fh, indent=1, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "missing_mrp_list.json"), "w") as fh:
        json.dump([{"product_id": r["product_id"], "brand": r["brand"], "product_name": r["product_name"],
                    "category": r["category"], "source_file": r["source_file"]} for r in missing_mrp], fh, indent=1, ensure_ascii=False)
    print("Saved image_curation_list.json and missing_mrp_list.json")

if __name__ == "__main__":
    main()
