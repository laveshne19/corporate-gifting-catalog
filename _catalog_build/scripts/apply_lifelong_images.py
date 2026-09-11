# -*- coding: utf-8 -*-
"""
Sources real Lifelong product photos from Lifelong's own Shopify store
(lifelongindiaonline.com/products.json) and matches them onto our Lifelong
records by exact SKU code (our model_code vs. the Shopify variant SKU).

Name-based fuzzy matching was tried first and rejected: Lifelong's B2B sheet
descriptions and the storefront's marketing titles are both generic/
templated ("PVC Hex Dumbbells", "Yoga Mat", "Thermosteel Flask") across many
different capacities/colours, so token-overlap matching produced confident-
looking but wrong matches (e.g. a 4-burner gas stove matched to a 2-burner
listing, a 900ml flask matched to a 1000ml one). SKU is the only field that
uniquely identifies the exact variant, so this only applies an image when
the SKU matches exactly — no fuzzy fallback, to avoid attaching a real photo
to the wrong product.

Patches image_file/image_source directly into xlsx_records.json's Lifelong
rows (the source extracted file), so the fix survives the next
consolidate.py run.
"""
import json, os

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
EXTRACTED = os.path.join(BASE, "_catalog_build", "extracted")
SCRIPTS = os.path.join(BASE, "_catalog_build", "scripts")

def build_sku_index():
    shop = json.load(open(os.path.join(SCRIPTS, "lifelong_shopify_catalog.json")))
    by_sku = {}
    for s in shop:
        if not s.get("img"):
            continue
        for sku in s.get("skus", []):
            by_sku.setdefault(sku.upper().strip(), s)
    return by_sku

def main():
    by_sku = build_sku_index()
    print(f"Shopify catalog: {len(by_sku)} unique SKUs with images")
    path = os.path.join(EXTRACTED, "xlsx_records.json")
    data = json.load(open(path))
    checked = applied = 0
    for r in data:
        if r.get("brand") != "Lifelong" or r.get("image_file"):
            continue
        checked += 1
        code = (r.get("model_code") or "").upper().strip()
        m = by_sku.get(code)
        if m:
            r["image_file"] = m["img"]
            r["image_source"] = "Web-verified (high confidence): lifelongindiaonline.com official store (exact SKU match)"
            applied += 1
    json.dump(data, open(path, "w"), indent=1, ensure_ascii=False)
    print(f"xlsx_records.json: checked {checked} missing-image Lifelong rows, matched {applied} by exact SKU")

if __name__ == "__main__":
    main()
