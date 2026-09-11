# -*- coding: utf-8 -*-
import json, os, glob
from datetime import date

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
IMG_DIR = os.path.join(BASE, "_catalog_build", "images")

def price_range(mrp):
    if mrp is None: return "Unpriced / Needs MRP"
    if mrp < 500: return "Budget (Under Rs.500)"
    if mrp < 1500: return "Everyday (Rs.500 - Rs.1,500)"
    if mrp < 5000: return "Mid-Range (Rs.1,500 - Rs.5,000)"
    if mrp < 15000: return "Premium (Rs.5,000 - Rs.15,000)"
    if mrp < 40000: return "Luxury (Rs.15,000 - Rs.40,000)"
    return "Ultra-Luxury (Above Rs.40,000)"

# Known parsing-artifact product_ids flagged by MRP agents (non-products)
JUNK_IDS = {"NE-05493", "NE-05494", "NE-05495", "NE-05518", "NE-05519", "NE-05520"}

def main():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    by_id = {r["product_id"]: r for r in recs}

    # ---- images ----
    img_applied = 0
    img_missing_file = 0
    for f in sorted(glob.glob(os.path.join(OUT_DIR, "image_results_chunk_*.json"))):
        for item in json.load(open(f)):
            rel = item["image_local_path"]
            full = os.path.join(IMG_DIR, rel)
            if not os.path.exists(full):
                img_missing_file += 1
                continue
            for pid in item["member_ids"]:
                r = by_id.get(pid)
                if r and not r.get("image_file"):
                    r["image_file"] = rel
                    r["image_source"] = f"Web-verified ({item.get('confidence','?')} confidence): {item.get('image_source_domain','')}"
                    img_applied += 1

    # ---- mrp ----
    mrp_applied = 0
    for f in sorted(glob.glob(os.path.join(OUT_DIR, "mrp_results_chunk_*.json"))):
        for item in json.load(open(f)):
            r = by_id.get(item["product_id"])
            if r and r.get("mrp") is None:
                r["mrp"] = item["mrp_found"]
                r["price_range_category"] = price_range(item["mrp_found"])
                r["mrp_source"] = f"Web-verified ({item.get('confidence','?')} confidence): {item.get('mrp_source_domain','')}"
                mrp_applied += 1

    # ---- drop known junk / non-product rows ----
    before = len(recs)
    recs = [r for r in recs if r["product_id"] not in JUNK_IDS]
    dropped = before - len(recs)

    today = date.today().isoformat()
    for r in recs:
        r["date_last_updated"] = today

    json.dump(recs, open(os.path.join(OUT_DIR, "master_consolidated.json"), "w"), indent=1, ensure_ascii=False)

    total = len(recs)
    with_mrp = sum(1 for r in recs if r["mrp"] is not None)
    with_img = sum(1 for r in recs if r.get("image_file"))
    print(f"Images applied: {img_applied} (missing files: {img_missing_file})")
    print(f"MRPs applied: {mrp_applied}")
    print(f"Dropped junk rows: {dropped}")
    print(f"TOTALS -> products: {total}, with MRP: {with_mrp} ({with_mrp/total*100:.1f}%), with image: {with_img} ({with_img/total*100:.1f}%)")

if __name__ == "__main__":
    main()
