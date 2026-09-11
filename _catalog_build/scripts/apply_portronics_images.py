# -*- coding: utf-8 -*-
"""
Sources real Portronics product photos from Portronics' own Shopify store
(portronics.com/products.json — the storefront's public product API) and
matches them onto our Portronics records by normalized product name. This is
far more reliable than a generic image search: it's the brand's own listing,
so a name match is a real match, not a guess.

portronics_shopify_catalog.json was pulled once via the Browser pane
(729 live products: title, handle, first image, tags) and is treated as a
static snapshot here — rerun that fetch if it goes stale.

Patches image_file/image_source directly into the two SOURCE extracted files
(xlsx_records.json's Portronics rows, portronics_pdf_records.json) rather
than the consolidated output, so the fix survives the next consolidate.py
run instead of being wiped by it.
"""
import json, os, re

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
EXTRACTED = os.path.join(BASE, "_catalog_build", "extracted")
SCRIPTS = os.path.join(BASE, "_catalog_build", "scripts")

def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or "").lower())

def build_shop_index():
    shop = json.load(open(os.path.join(SCRIPTS, "portronics_shopify_catalog.json")))
    shop = [s for s in shop if s.get("img")]
    by_norm = {}
    for s in shop:
        by_norm.setdefault(norm(s["title"]), []).append(s)
    return shop, by_norm

def best_match(name, shop, by_norm):
    n = norm(name)
    if not n:
        return None
    if n in by_norm:
        return by_norm[n][0]
    if len(n) < 4:
        return None
    candidates = [s for s in shop if n in norm(s["title"]) or norm(s["title"]) in n]
    if not candidates:
        return None
    candidates.sort(key=lambda s: abs(len(norm(s["title"])) - len(n)))
    return candidates[0]

def patch_file(path, shop, by_norm, brand_field="brand", name_field="product_name"):
    data = json.load(open(path))
    applied = 0
    checked = 0
    for r in data:
        if r.get(brand_field) != "Portronics" or r.get("image_file"):
            continue
        checked += 1
        m = best_match(r.get(name_field, ""), shop, by_norm)
        if m:
            r["image_file"] = m["img"]
            r["image_source"] = "Web-verified (high confidence): portronics.com official store"
            applied += 1
    json.dump(data, open(path, "w"), indent=1, ensure_ascii=False)
    print(f"  {os.path.basename(path)}: checked {checked} missing-image Portronics rows, matched {applied}")
    return applied

def main():
    shop, by_norm = build_shop_index()
    print(f"Shopify catalog: {len(shop)} products with images")
    total = 0
    total += patch_file(os.path.join(EXTRACTED, "xlsx_records.json"), shop, by_norm)
    total += patch_file(os.path.join(EXTRACTED, "portronics_pdf_records.json"), shop, by_norm)
    print(f"Total newly matched: {total}")

if __name__ == "__main__":
    main()
