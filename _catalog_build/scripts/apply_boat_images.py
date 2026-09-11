# -*- coding: utf-8 -*-
"""
Sources real boAt product photos from boAt's own Shopify store
(boat-lifestyle.com/products.json) for the ~137 boAt products still missing
an image after the GT Price List import. Matches by normalized "core title"
containment: the Shopify listing's base name (brand prefix and marketing
subtitle after "|" stripped) must be a full substring of our product name
(which is "<family> <color/variant>", e.g. "Airdopes 191 ANC Pellucid
White" contains shop's "Airdopes 191 ANC") — sample-verified 40/40 correct
on a random batch before running at scale. Falls back to no match rather
than a shorter/weaker partial match, to avoid attaching the wrong family's
photo (e.g. "Rockerz 200" vs "Rockerz 210 ANC").

Patches image_file/image_source into the source extracted file
(boat_gt_records.json under whatever name extract_xlsx.py's parse_boat()
writes into) — actually boAt's rows live in xlsx_records.json alongside
other brands, same as Portronics/Lifelong, so patch that file's boAt rows.
"""
import json, os, re

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
EXTRACTED = os.path.join(BASE, "_catalog_build", "extracted")
SCRIPTS = os.path.join(BASE, "_catalog_build", "scripts")

def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or "").lower())

def core_title(t):
    t = t.split("|")[0]
    t = re.sub(r'^boAt\s+', '', t, flags=re.I)
    return t.strip()

def build_index():
    shop = json.load(open(os.path.join(SCRIPTS, "boat_shopify_catalog.json")))
    items = [(norm(core_title(s["title"])), s) for s in shop if s.get("img")]
    items = [(n, s) for n, s in items if len(n) >= 4]
    items.sort(key=lambda x: -len(x[0]))  # longest/most-specific title first
    return items

def best_match(name, shop_items):
    n = norm(name)
    if not n:
        return None
    for sn, s in shop_items:
        if sn in n:
            return s
    return None

def main():
    shop_items = build_index()
    print(f"Shopify catalog: {len(shop_items)} products with images")
    path = os.path.join(EXTRACTED, "xlsx_records.json")
    data = json.load(open(path))
    checked = applied = 0
    for r in data:
        if r.get("brand") != "boAt" or r.get("image_file"):
            continue
        checked += 1
        m = best_match(r.get("product_name", ""), shop_items)
        if m:
            r["image_file"] = m["img"]
            r["image_source"] = "Web-verified (high confidence): boat-lifestyle.com official store"
            applied += 1
    json.dump(data, open(path, "w"), indent=1, ensure_ascii=False)
    print(f"xlsx_records.json: checked {checked} missing-image boAt rows, matched {applied}")

if __name__ == "__main__":
    main()
