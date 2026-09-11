# -*- coding: utf-8 -*-
"""
DEPRECATED / UNSAFE — DO NOT RUN.

This script matches images to products by raw product_id (member_id) alone.
product_id is only stable *within* a single generation of master_consolidated.json —
after any consolidate.py re-run that adds/removes a source file, a numeric id
can end up belonging to a completely different product. Running this script
in that situation silently pastes one product's photo onto an unrelated
product with the same old numeric id (this happened for real: it overwrote
correct Noise product images with Skyline kettle / Sujata / pressure-cooker
photos scraped for other brands, because the ids coincided across runs).

Use recover_enrichment.py instead — it does the same "keep the deploy small
by linking to the external source URL" job, but resolves every match through
(brand, product_name) via the *_curation_*.json snapshots first, so an id
collision can never mix up two different products.
"""
raise SystemExit(
    "switch_web_images_to_url.py is deprecated and unsafe (matches by raw "
    "product_id, which can silently swap images between unrelated products "
    "after a consolidate.py re-run). Use recover_enrichment.py instead."
)

import json, os, glob

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")

def main():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    by_id = {r["product_id"]: r for r in recs}

    url_map = {}  # member_id -> (url, domain, confidence)
    patterns = [
        "image_results_chunk_*.json", "image_results_wave2_chunk_*.json",
        "image_results_wave3_chunk_*.json", "image_results_haier.json",
        "image_results_samsung2.json", "image_results_newbatch.json",
        "image_gap_results_*.json",
    ]
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(OUT_DIR, p)))
    for f in files:
        try:
            data = json.load(open(f))
        except Exception as e:
            print(f"  SKIP (bad json) {os.path.basename(f)}: {e}")
            continue
        for item in data:
            if not item.get("image_source_url"):
                continue
            for pid in item.get("member_ids", []):
                if pid not in url_map:
                    url_map[pid] = (item["image_source_url"], item.get("image_source_domain", ""), item.get("confidence", "?"))
    # final_pricing_results.json uses a different shape (product_id, not member_ids)
    fp = os.path.join(OUT_DIR, "final_pricing_results.json")
    if os.path.exists(fp):
        for item in json.load(open(fp)):
            pid = item.get("product_id")
            if pid and item.get("image_source_url") and pid not in url_map:
                url_map[pid] = (item["image_source_url"], item.get("image_source_domain", ""), item.get("confidence", "?"))

    switched = 0
    for pid, (url, domain, conf) in url_map.items():
        r = by_id.get(pid)
        if r and (r.get("image_file") or "").startswith("web/"):
            r["image_file"] = url
            r["image_source"] = f"Web-verified ({conf} confidence): {domain}"
            switched += 1

    json.dump(recs, open(os.path.join(OUT_DIR, "master_consolidated.json"), "w"), indent=1, ensure_ascii=False)
    print(f"Switched {switched} web-scraped image references from local copies to direct external URLs")

if __name__ == "__main__":
    main()
