# -*- coding: utf-8 -*-
"""
Consolidates the per-product image matches found by the background search
agents (Whirlpool/Samsung/Haier/IFB — brands with no bulk-scrapable catalog,
so each product was searched and verified individually) and patches them
into whichever SOURCE extracted file actually holds that record, matched by
(brand, product_name) against the current master_consolidated.json snapshot
— the same content-matching principle recover_enrichment.py uses, since
extracted files don't carry product_id (that's assigned at consolidate time).
"""
import json, os, glob

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
EXTRACTED = os.path.join(BASE, "_catalog_build", "extracted")
PROGRESS = os.path.join(BASE, "_catalog_build", "scripts", "image_search_progress")
SCRATCHPAD = "/private/tmp/claude-503/-Users-laveshbansal-Downloads----Master-Folder-master-price-list/b3692fd6-d517-4c0a-9342-d40ac9724218/scratchpad"

def load_results():
    merged = {}
    # Main per-brand result files
    for f in glob.glob(os.path.join(PROGRESS, "*_results.json")):
        d = json.load(open(f))
        merged.update(d)
    # IFB scratchpad chunks
    for f in glob.glob(os.path.join(SCRATCHPAD, "ifb_results_chunk*.json")):
        d = json.load(open(f))
        merged.update(d)
    return merged

def main():
    results = load_results()
    print(f"Total confirmed matches loaded: {len(results)}")

    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    pid_to_key = {}
    for r in recs:
        pid_to_key[r["product_id"]] = (r["brand"], r["product_name"])

    # (brand, product_name) -> image data, only for products we have a match for
    target = {}
    unresolved_pid = []
    for pid, data in results.items():
        key = pid_to_key.get(pid)
        if not key:
            unresolved_pid.append(pid)
            continue
        target[key] = data

    print(f"Resolved to (brand,name) keys: {len(target)}; product_ids not found in current snapshot: {len(unresolved_pid)}")

    applied = 0
    touched_files = []
    for path in glob.glob(os.path.join(EXTRACTED, "*.json")):
        base = os.path.basename(path)
        if base in ("pdf_classification.json", "pdf_image_manifest.json"):
            continue
        try:
            data = json.load(open(path))
        except Exception:
            continue
        if not isinstance(data, list):
            continue
        changed = False
        for r in data:
            if not isinstance(r, dict) or "brand" not in r or "product_name" not in r:
                continue
            key = (r["brand"], r["product_name"])
            if key in target and not r.get("image_file"):
                m = target[key]
                r["image_file"] = m["image_url"]
                r["image_source"] = f"Web-verified (high confidence, individually searched): {m.get('domain','')}"
                applied += 1
                changed = True
        if changed:
            json.dump(data, open(path, "w"), indent=1, ensure_ascii=False)
            touched_files.append(base)

    print(f"Applied {applied} images across {len(touched_files)} files: {touched_files}")

if __name__ == "__main__":
    main()
