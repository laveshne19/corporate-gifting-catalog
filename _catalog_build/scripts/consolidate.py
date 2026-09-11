# -*- coding: utf-8 -*-
"""
Consolidate all extracted JSON record files into one master dataset.
Assigns Product ID, dedupes near-identical rows, computes price range category.
"""
import json, os, glob, re, hashlib
from datetime import date

BASE = "/Users/laveshbardal" if False else "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
EXT = os.path.join(BASE, "_catalog_build", "extracted")
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")

SCHEMA_FILES_EXCLUDE = {"xlsx_preview.txt", "pdf_classification.json", "pdf_image_manifest.json"}

def load_id_hints():
    """
    product_id used to be assigned purely by enumeration order over sorted
    extracted/*.json files, which silently reshuffled every existing
    product's ID whenever a new source file was added or removed (its
    alphabetical position shifts everything after it). Every historical
    output/*_curation*.json and output/missing_mrp*.json file is a snapshot
    of {brand, product_name, member_ids|product_id} taken at some earlier,
    self-consistent moment — so scanning all of them and keeping the
    first-seen id per (brand, product_name) gives a best-effort STABLE id
    to carry forward, so previously-scraped images/MRP (keyed by that old
    id) remain valid instead of drifting onto a different product.
    """
    hints = {}
    conflicts = 0
    for fp in sorted(glob.glob(os.path.join(OUT_DIR, "*.json"))):
        name = os.path.basename(fp)
        if "curation" not in name and "missing_mrp" not in name:
            continue
        try:
            data = json.load(open(fp))
        except Exception:
            continue
        if not isinstance(data, list) or not data or not isinstance(data[0], dict):
            continue
        for item in data:
            brand = item.get("brand")
            pname = item.get("product_name")
            if not brand or not pname:
                continue
            ids = item.get("member_ids") or ([item["product_id"]] if item.get("product_id") else [])
            if not ids:
                continue
            key = norm_key(pname, brand)
            for pid in ids:
                if key in hints and hints[key] != pid:
                    conflicts += 1
                else:
                    hints[key] = pid
    print(f"ID stability hints loaded: {len(hints)} unique products, {conflicts} conflicting duplicate sightings ignored")
    return hints

def load_all_records():
    all_recs = []
    for fp in sorted(glob.glob(os.path.join(EXT, "*.json"))):
        name = os.path.basename(fp)
        if name in SCHEMA_FILES_EXCLUDE:
            continue
        try:
            data = json.load(open(fp))
        except Exception as e:
            print("SKIP (bad json)", name, e)
            continue
        if not isinstance(data, list) or not data:
            continue
        if not isinstance(data[0], dict) or "brand" not in data[0] or "product_name" not in data[0]:
            continue
        for r in data:
            r["_origin_file"] = name
        all_recs.extend(data)
        print(f"{name}: {len(data)}")
    return all_recs

def norm_key(name, brand):
    s = re.sub(r'[^a-z0-9]+', '', (name or "").lower())
    b = re.sub(r'[^a-z0-9]+', '', (brand or "").lower())
    return f"{b}|{s}"

BRAND_CANONICAL = {
    "swiss military audio": "Swiss Military",
    "swiss military": "Swiss Military",
    "boult": "boUlt",
    "boult audio": "boUlt",
    "qubo (a hero group venture)": "Qubo",
    "qubo (trust of hero group)": "Qubo",
    "qubo a hero group venture": "Qubo",
    "amazon (echo/fire tv)": "Amazon",
    "amazon devices": "Amazon",
}

def clean_record(r):
    brand = (r.get("brand") or "").strip()
    if brand.lower() in BRAND_CANONICAL:
        brand = BRAND_CANONICAL[brand.lower()]
    name = (r.get("product_name") or "").strip()
    # drop obvious junk
    if not brand or not name or len(name) < 2:
        return None
    if name.lower() in ("mrp", "price", "category", "model name/", "list price (lp)"):
        return None
    mrp = r.get("mrp")
    landing = r.get("landing_price")
    try:
        mrp = float(mrp) if mrp not in (None, "") else None
    except (TypeError, ValueError):
        mrp = None
    try:
        landing = float(landing) if landing not in (None, "") else None
    except (TypeError, ValueError):
        landing = None
    if mrp is not None and mrp <= 0:
        mrp = None
    if landing is not None and landing <= 0:
        landing = None
    # sanity: landing_price should not exceed mrp significantly (data error) -> swap
    if mrp is not None and landing is not None and landing > mrp:
        mrp, landing = landing, mrp
    return dict(
        brand=brand, category=(r.get("category") or "").strip() or "Uncategorized",
        sub_category=(r.get("sub_category") or "").strip(),
        product_name=name, model_code=(r.get("model_code") or "").strip(),
        description=(r.get("description") or "").strip(),
        variant=(r.get("variant") or "").strip(),
        key_specs=(r.get("key_specs") or "").strip(),
        mrp=mrp, landing_price=landing,
        warranty=(r.get("warranty") or "").strip(),
        source_file=r.get("source_file") or r.get("_origin_file") or "",
        source_sheet=r.get("source_sheet") or "",
        # pass through image data embedded directly by a per-vendor parser
        # (e.g. parse_vip_bags.py extracts images from the source deck itself)
        # so it survives a re-consolidation instead of being silently dropped.
        image_file=(r.get("image_file") or "").strip(),
        image_source=(r.get("image_source") or "").strip(),
    )

def price_range(mrp):
    if mrp is None:
        return "Unpriced / Needs MRP"
    if mrp < 500:
        return "Budget (Under Rs.500)"
    if mrp < 1500:
        return "Everyday (Rs.500 - Rs.1,500)"
    if mrp < 5000:
        return "Mid-Range (Rs.1,500 - Rs.5,000)"
    if mrp < 15000:
        return "Premium (Rs.5,000 - Rs.15,000)"
    if mrp < 40000:
        return "Luxury (Rs.15,000 - Rs.40,000)"
    return "Ultra-Luxury (Above Rs.40,000)"

def main():
    raw = load_all_records()
    print("\nRAW TOTAL:", len(raw))
    cleaned = []
    for r in raw:
        c = clean_record(r)
        if c:
            cleaned.append(c)
    print("CLEANED TOTAL:", len(cleaned))

    # Dedup: prefer record with richer data (has description/specs, has both prices) among same (brand,name norm)
    groups = {}
    for r in cleaned:
        key = norm_key(r["product_name"], r["brand"])
        groups.setdefault(key, []).append(r)

    def richness(r):
        score = 0
        if r["mrp"] is not None: score += 3
        if r["landing_price"] is not None: score += 2
        if r["description"]: score += 1
        if r["key_specs"]: score += 1
        if r["model_code"]: score += 1
        return score

    deduped = []
    merge_notes = 0
    for key, group in groups.items():
        if len(group) == 1:
            deduped.append(group[0])
            continue
        group.sort(key=richness, reverse=True)
        best = dict(group[0])
        # fill gaps from other duplicates
        for other in group[1:]:
            if best["mrp"] is None and other["mrp"] is not None:
                best["mrp"] = other["mrp"]
            if best["landing_price"] is None and other["landing_price"] is not None:
                best["landing_price"] = other["landing_price"]
            if not best["description"] and other["description"]:
                best["description"] = other["description"]
            if not best["key_specs"] and other["key_specs"]:
                best["key_specs"] = other["key_specs"]
        merge_notes += len(group) - 1
        deduped.append(best)
    print("AFTER DEDUP:", len(deduped), f"(merged away {merge_notes} duplicate rows)")

    id_hints = load_id_hints()
    used_ids = set()
    # pass 1: lock in every record whose (brand, name) matches a known
    # historical id, so previously-scraped images/MRP keyed by that id
    # keep pointing at the same product.
    for r in deduped:
        key = norm_key(r["product_name"], r["brand"])
        hint = id_hints.get(key)
        if hint and hint not in used_ids:
            r["product_id"] = hint
            used_ids.add(hint)
        else:
            r["product_id"] = None
    # pass 2: fill everything else from the lowest unused NE-##### slots,
    # so ids stay compact and stable run-to-run instead of drifting.
    next_n = 1
    def alloc():
        nonlocal next_n
        while f"NE-{next_n:05d}" in used_ids:
            next_n += 1
        pid = f"NE-{next_n:05d}"
        used_ids.add(pid)
        next_n += 1
        return pid
    reused = 0
    for r in deduped:
        if r["product_id"] is None:
            r["product_id"] = alloc()
        else:
            reused += 1
    print(f"Product IDs: {reused} reused from history, {len(deduped) - reused} newly assigned")

    today = date.today().isoformat()
    for r in deduped:
        r["price_range_category"] = price_range(r["mrp"])
        r["date_last_updated"] = today
        r["mrp_source"] = r["source_file"]
        if not r.get("image_file"):
            r["image_source"] = ""
            r["image_file"] = ""

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "master_consolidated.json"), "w") as fh:
        json.dump(deduped, fh, indent=1, ensure_ascii=False)
    print("\nSaved master_consolidated.json with", len(deduped), "products")

    # Quick stats
    by_brand = {}
    no_mrp = 0
    for r in deduped:
        by_brand[r["brand"]] = by_brand.get(r["brand"], 0) + 1
        if r["mrp"] is None:
            no_mrp += 1
    print("\nBy brand:")
    for b, c in sorted(by_brand.items(), key=lambda x: -x[1]):
        print(f"  {b}: {c}")
    print(f"\nProducts missing MRP: {no_mrp} ({no_mrp/len(deduped)*100:.1f}%)")

if __name__ == "__main__":
    main()
