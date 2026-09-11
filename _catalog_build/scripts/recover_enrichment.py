# -*- coding: utf-8 -*-
"""
Safely re-applies all historical image/MRP scraping results onto the
current (stable-id) master_consolidated.json.

Old *_results_*.json files only carry stale member_ids (product_ids that
have since drifted). Instead of trusting those ids directly, we join
through the matching *_curation_*.json snapshot, which pairs each old id
with (brand, product_name) as they were at scrape time — then re-resolve
that (brand, product_name) against the CURRENT dataset via norm_key. This
avoids silently pasting an image onto the wrong product.
"""
import json, os, glob, re

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
IMG_DIR = os.path.join(BASE, "_catalog_build", "images")

def norm_key(name, brand):
    s = re.sub(r'[^a-z0-9]+', '', (name or "").lower())
    b = re.sub(r'[^a-z0-9]+', '', (brand or "").lower())
    return f"{b}|{s}"

def price_range(mrp):
    if mrp is None: return "Unpriced / Needs MRP"
    if mrp < 500: return "Budget (Under Rs.500)"
    if mrp < 1500: return "Everyday (Rs.500 - Rs.1,500)"
    if mrp < 5000: return "Mid-Range (Rs.1,500 - Rs.5,000)"
    if mrp < 15000: return "Premium (Rs.5,000 - Rs.15,000)"
    if mrp < 40000: return "Luxury (Rs.15,000 - Rs.40,000)"
    return "Ultra-Luxury (Above Rs.40,000)"

# (curation_file, results_file_glob_pattern) pairs — curation carries
# brand+product_name per old id, results carries the actual image/mrp find.
IMAGE_PAIRS = [
    ("image_curation_chunk_1.json", "image_results_chunk_1.json"),
    ("image_curation_chunk_2.json", "image_results_chunk_2.json"),
    ("image_curation_chunk_3.json", "image_results_chunk_3.json"),
    ("image_curation_chunk_4.json", "image_results_chunk_4.json"),
    ("image_curation_newbatch.json", "image_results_newbatch.json"),
    ("image_curation_samsung2.json", "image_results_samsung2.json"),
    ("image_curation_wave2_chunk_1.json", "image_results_wave2_chunk_1.json"),
    ("image_curation_wave2_chunk_2.json", "image_results_wave2_chunk_2.json"),
    ("image_curation_wave2_chunk_3.json", "image_results_wave2_chunk_3.json"),
    ("image_curation_wave2_chunk_4.json", "image_results_wave2_chunk_4.json"),
    ("image_curation_wave2_chunk_6.json", "image_results_wave2_chunk_6.json"),
    ("image_curation_wave2_chunk_7.json", "image_results_wave2_chunk_7.json"),
    ("image_curation_wave2_chunk_8.json", "image_results_wave2_chunk_8.json"),
    ("image_curation_wave2_chunk_10.json", "image_results_wave2_chunk_10.json"),
    ("image_curation_wave3_chunk_1.json", "image_results_wave3_chunk_1.json"),
    ("image_curation_wave3_chunk_2.json", "image_results_wave3_chunk_2.json"),
    ("image_curation_wave3_chunk_2.json", "image_results_wave3_chunk_2_new.json"),
    ("image_curation_wave3_chunk_3.json", "image_results_wave3_chunk_3.json"),
    ("image_curation_wave3_chunk_4.json", "image_results_wave3_chunk_4.json"),
    ("image_curation_wave3_chunk_5.json", "image_results_wave3_chunk_5.json"),
    ("image_curation_wave3_chunk_6.json", "image_results_wave3_chunk_6.json"),
    ("image_curation_wave3_chunk_6.json", "image_results_wave3_chunk_6_new.json"),
    ("image_curation_wave3_chunk_7.json", "image_results_wave3_chunk_7.json"),
    ("image_curation_haier.json", "image_results_haier.json"),
    ("image_curation_haier_remaining.json", "image_results_haier.json"),
    ("image_gap_chunk_1.json", "image_gap_results_1.json"),
    ("image_gap_chunk_2.json", "image_gap_results_2.json"),
    ("image_gap_chunk_3.json", "image_gap_results_3.json"),
    ("image_gap_chunk_4.json", "image_gap_results_4.json"),
    ("image_gap_chunk_5.json", "image_gap_results_5.json"),
    ("image_gap_chunk_6.json", "image_gap_results_6.json"),
]

MRP_PAIRS = [
    ("missing_mrp_chunk_1.json", "mrp_results_chunk_1.json"),
    ("missing_mrp_chunk_2.json", "mrp_results_chunk_2.json"),
]

def load_json(name):
    fp = os.path.join(OUT_DIR, name)
    if not os.path.exists(fp):
        return None
    try:
        return json.load(open(fp))
    except Exception as e:
        print(f"  SKIP (bad json) {name}: {e}")
        return None

def main():
    master_path = os.path.join(OUT_DIR, "master_consolidated.json")
    master = json.load(open(master_path))
    by_id = {r["product_id"]: r for r in master}
    current_key_to_id = {}
    # fallback index: model_code -> [(product_id, brand)], for when the
    # naming convention drifted between the old curation snapshot and the
    # current parser (e.g. "Air Conditioner HSA105LCH-W4NB-PI" vs
    # "Haier HSA105LCH-W4NB-PI" — same model code, different name shape).
    model_code_index = {}
    for r in master:
        current_key_to_id[norm_key(r["product_name"], r["brand"])] = r["product_id"]
        mc = (r.get("model_code") or "").strip()
        if len(mc) >= 5:
            model_code_index.setdefault(mc.upper(), []).append((r["product_id"], r["brand"]))

    def resolve(brand, pname):
        cur_id = current_key_to_id.get(norm_key(pname, brand))
        if cur_id:
            return cur_id
        # fallback: does a known model_code appear as a substring of the
        # old product_name, for the same brand?
        upname = (pname or "").upper()
        for mc, candidates in model_code_index.items():
            if mc in upname:
                for pid, cbrand in candidates:
                    if cbrand.lower() == (brand or "").lower():
                        return pid
        return None

    img_applied = 0
    img_unresolved = 0
    img_missing_file = 0
    img_already_set = 0

    for curation_name, results_name in IMAGE_PAIRS:
        curation = load_json(curation_name)
        results = load_json(results_name)
        if not curation or not results:
            continue
        old_id_to_bn = {}
        for item in curation:
            brand = item.get("brand")
            pname = item.get("product_name")
            if not brand or not pname:
                continue
            for oid in item.get("member_ids", []):
                old_id_to_bn[oid] = (brand, pname)
        for item in results:
            rel = item.get("image_local_path")
            url = item.get("image_source_url")
            if not rel or not url:
                continue
            full = os.path.join(IMG_DIR, rel)
            if not os.path.exists(full):
                img_missing_file += 1
                continue
            # NOTE: we store the external source URL, not the local `rel`
            # path — deliberately, so the site links straight to the
            # vendor's own hosted photo instead of bundling thousands of
            # scraped images into the Netlify deploy. This also sidesteps
            # the id-drift risk of a separate later "switch to URL" pass
            # keyed on a possibly-since-reassigned product_id.
            for oid in item.get("member_ids", []):
                bn = old_id_to_bn.get(oid)
                if not bn:
                    img_unresolved += 1
                    continue
                cur_id = resolve(bn[0], bn[1])
                if not cur_id:
                    img_unresolved += 1
                    continue
                r = by_id.get(cur_id)
                if not r:
                    img_unresolved += 1
                    continue
                if r.get("image_file"):
                    img_already_set += 1
                    continue
                r["image_file"] = url
                r["image_source"] = f"Web-verified ({item.get('confidence','?')} confidence): {item.get('image_source_domain','')}"
                img_applied += 1

    mrp_applied = 0
    mrp_unresolved = 0
    mrp_already_set = 0
    for curation_name, results_name in MRP_PAIRS:
        curation = load_json(curation_name)
        results = load_json(results_name)
        if not curation or not results:
            continue
        old_id_to_bn = {item["product_id"]: (item.get("brand"), item.get("product_name"))
                         for item in curation if item.get("product_id")}
        for item in results:
            oid = item.get("product_id")
            bn = old_id_to_bn.get(oid)
            if not bn or not bn[0] or not bn[1]:
                mrp_unresolved += 1
                continue
            cur_id = resolve(bn[0], bn[1])
            if not cur_id:
                mrp_unresolved += 1
                continue
            r = by_id.get(cur_id)
            if not r:
                mrp_unresolved += 1
                continue
            if r.get("mrp") is not None:
                mrp_already_set += 1
                continue
            mrp_val = item.get("mrp_found")
            if mrp_val is None:
                continue
            r["mrp"] = mrp_val
            r["price_range_category"] = price_range(mrp_val)
            r["mrp_source"] = f"Web-verified ({item.get('confidence','?')} confidence): {item.get('mrp_source_domain','')}"
            mrp_applied += 1

    # Noise enrichment — self-contained (record_id + product_name), brand=Noise
    noise = load_json("noise_enrichment.json")
    noise_img = 0
    noise_mrp = 0
    if noise:
        for item in noise:
            cur_id = resolve("Noise", item.get("product_name", ""))
            if not cur_id:
                continue
            r = by_id.get(cur_id)
            if not r:
                continue
            if item.get("mrp") is not None and r.get("mrp") is None:
                r["mrp"] = float(item["mrp"])
                r["price_range_category"] = price_range(r["mrp"])
                r["mrp_source"] = f"gonoise.com official storefront"
                noise_mrp += 1
            # NOTE: this agent's own image_local_path pointed into the
            # shared images/web/ pool, which later scraping waves proved
            # unsafe to trust (a Haier batch physically overwrote several
            # of these exact filenames with fridge photos). Real Noise
            # images now live in noise_images_v2.json / images/noise_official/
            # (see the block below) — this block only still applies MRP.
            pass

    # Noise images v2 — re-fetched directly from gonoise.com's Shopify JSON
    # into the dedicated images/noise_official/ folder (never shared with
    # other brands' scraping, so it can't be overwritten by a later wave).
    noise_v2 = load_json("noise_images_v2.json")
    noise_img_v2 = 0
    if noise_v2:
        for item in noise_v2:
            r = by_id.get(item["product_id"])
            if not r:
                r_id = resolve("Noise", item.get("product_name", ""))
                r = by_id.get(r_id) if r_id else None
            if not r:
                continue
            full = os.path.join(BASE, "_catalog_build", "images", item["image_local_path"])
            if os.path.exists(full):
                r["image_file"] = item["image_local_path"]
                r["image_source"] = "Official gonoise.com CDN photo"
                noise_img_v2 += 1

    json.dump(master, open(master_path, "w"), indent=1, ensure_ascii=False)

    total = len(master)
    with_mrp = sum(1 for r in master if r.get("mrp") is not None)
    with_img = sum(1 for r in master if r.get("image_file"))
    print(f"IMAGES  -> applied: {img_applied}, already set: {img_already_set}, unresolved (name shifted too far to re-match): {img_unresolved}, missing on disk: {img_missing_file}")
    print(f"MRP     -> applied: {mrp_applied}, already set: {mrp_already_set}, unresolved: {mrp_unresolved}")
    print(f"NOISE   -> mrp applied: {noise_mrp}, image applied (v2, dedicated folder): {noise_img_v2}")
    print(f"TOTALS  -> products: {total}, with MRP: {with_mrp} ({with_mrp/total*100:.1f}%), with image: {with_img} ({with_img/total*100:.1f}%)")

if __name__ == "__main__":
    main()
