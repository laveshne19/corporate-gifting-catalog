# -*- coding: utf-8 -*-
import json, os, html
from datetime import date

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
SITE_DIR = os.path.join(BASE, "_catalog_build", "site")
VERSION_TAG = date.today().strftime("%Y%m%d")

def main():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    os.makedirs(SITE_DIR, exist_ok=True)

    # Slim payload for the browser — only fields the UI needs
    slim = []
    for r in recs:
        slim.append({
            "id": r["product_id"],
            "b": r["brand"],
            "n": r["product_name"],
            "d": (r.get("description") or "")[:220],
            "c": r["category"],
            "sc": r.get("sub_category") or "",
            "v": r.get("variant") or "",
            "k": r.get("key_specs") or "",
            "m": r["mrp"],
            "pr": r["price_range_category"],
            "bl": r.get("budget_low"),
            "bh": r.get("budget_high"),
            "img": r.get("image_file") or "",
            "imgsrc": r.get("image_source") or "",
        })

    brands = sorted(set(r["b"] for r in slim))
    categories = sorted(set(r["c"] for r in slim))
    # Gift cards are a resale product, not an authorised distributor
    # relationship — Flipkart/Myntra/Amazon etc. must never be counted
    # toward "authorised brands" claims. They stay in `brands` (for the
    # catalog filter dropdown) but are excluded from the brand showcase
    # and every trust-building "N authorised brands" stat below.
    authorised_brand_names = sorted(set(r["b"] for r in slim if r["c"] != "Gift Cards"))
    price_ranges = ["Budget (Under Rs.500)", "Everyday (Rs.500 - Rs.1,500)", "Mid-Range (Rs.1,500 - Rs.5,000)",
                     "Premium (Rs.5,000 - Rs.15,000)", "Luxury (Rs.15,000 - Rs.40,000)",
                     "Ultra-Luxury (Above Rs.40,000)", "Unpriced / Needs MRP"]

    # Budget buckets: based on budget_low (NLC + margin), NOT mrp. This is
    # what customers actually filter/sort by — an estimated price band, not
    # the sticker MRP and not the raw dealer cost.
    BUDGET_BUCKETS = [
        {"key": "u500", "label": "Under Rs.500", "min": 0, "max": 500},
        {"key": "500-1000", "label": "Rs.500 - Rs.1,000", "min": 500, "max": 1000},
        {"key": "1000-2500", "label": "Rs.1,000 - Rs.2,500", "min": 1000, "max": 2500},
        {"key": "2500-5000", "label": "Rs.2,500 - Rs.5,000", "min": 2500, "max": 5000},
        {"key": "5000-10000", "label": "Rs.5,000 - Rs.10,000", "min": 5000, "max": 10000},
        {"key": "10000-25000", "label": "Rs.10,000 - Rs.25,000", "min": 10000, "max": 25000},
        {"key": "25000-50000", "label": "Rs.25,000 - Rs.50,000", "min": 25000, "max": 50000},
        {"key": "above50000", "label": "Above Rs.50,000", "min": 50000, "max": None},
        {"key": "unpriced", "label": "Budget TBD", "min": None, "max": None},
    ]
    for b in BUDGET_BUCKETS:
        if b["key"] == "unpriced":
            b["count"] = sum(1 for r in slim if r.get("bl") is None)
        else:
            b["count"] = sum(1 for r in slim if r.get("bl") is not None and r["bl"] >= b["min"] and (b["max"] is None or r["bl"] < b["max"]))

    # Category metadata: count + a representative emoji
    EMOJI_MAP = [
        (("audio", "speaker", "sound", "earbud", "wearable", "headphone"), "🎧"),
        (("watch",), "⌚"),
        (("kitchen", "dining", "cookware", "gas", "stove", "hob"), "🍳"),
        (("dinnerware", "opalware", "glass", "tableware"), "🍽️"),
        (("water heater", "geyser"), "🚿"),
        (("air purifier",), "🌬️"),
        (("air condition",), "❄️"),
        (("refrigerator", "fridge"), "🧊"),
        (("washing machine",), "🫧"),
        (("fan",), "🌀"),
        (("pc ", "laptop", "computer"), "💻"),
        (("mobile", "accessor", "charger", "cable", "power bank"), "📱"),
        (("smart home", "security", "camera", "lock"), "🏠"),
        (("personal care", "grooming", "trimmer"), "🪒"),
        (("health", "wellness", "massager"), "💆"),
        (("sports", "fitness"), "🏋️"),
        (("bag", "luggage", "suitcase"), "🧳"),
        (("home textile", "bedsheet", "towel", "blanket"), "🛏️"),
        (("microphone",), "🎙️"),
        (("tablet",), "📱"),
        (("appliance",), "🔌"),
    ]
    def emoji_for(cat):
        cl = cat.lower()
        for keys, em in EMOJI_MAP:
            if any(k in cl for k in keys):
                return em
        return "🎁"

    from collections import Counter
    cat_counts = Counter(r["c"] for r in slim)
    cat_meta = [{"name": c, "count": n, "emoji": emoji_for(c)} for c, n in cat_counts.most_common(14)]

    # Brand showcase: every brand, its product count and top category (for the
    # dedicated Brands section — the old top-nav "Brands" link used to just
    # scroll to a thin marquee strip with nothing substantial to see).
    brand_counts = Counter(r["b"] for r in slim if r["c"] != "Gift Cards")
    brand_top_cat = {}
    for r in slim:
        if r["c"] == "Gift Cards":
            continue
        brand_top_cat.setdefault(r["b"], Counter())[r["c"]] += 1
    logo_map_path = os.path.join(OUT_DIR, "brand_logo_map.json")
    brand_logos = json.load(open(logo_map_path)) if os.path.exists(logo_map_path) else {}
    brand_meta = [
        {"name": b, "count": n, "category": brand_top_cat[b].most_common(1)[0][0], "logo": brand_logos.get(b, "")}
        for b, n in brand_counts.most_common()
    ]

    # Hero visual: a brand-diverse rotating pool of product photos for the floating cards
    import random
    random.seed(7)
    eligible = [r for r in slim if r["img"] and r["m"] and r["m"] > 800]
    by_brand_hero = {}
    for r in eligible:
        by_brand_hero.setdefault(r["b"], []).append(r)
    for lst in by_brand_hero.values():
        random.shuffle(lst)
    hero_pool = []
    round_i = 0
    brand_keys = list(by_brand_hero.keys())
    random.shuffle(brand_keys)
    while len(hero_pool) < 48 and any(round_i < len(by_brand_hero[b]) for b in brand_keys):
        for b in brand_keys:
            if round_i < len(by_brand_hero[b]):
                hero_pool.append(by_brand_hero[b][round_i])
        round_i += 1
    hero_images = [{"img": r["img"], "b": r["b"], "n": r["n"], "m": r["m"], "bl": r.get("bl"), "bh": r.get("bh")} for r in hero_pool[:48]]

    data_json = json.dumps(slim, ensure_ascii=False, separators=(",", ":"))
    brands_json = json.dumps(brands, ensure_ascii=False)
    categories_json = json.dumps(categories, ensure_ascii=False)
    ranges_json = json.dumps(price_ranges, ensure_ascii=False)
    budget_buckets_json = json.dumps(BUDGET_BUCKETS, ensure_ascii=False)
    catmeta_json = json.dumps(cat_meta, ensure_ascii=False)
    brandmeta_json = json.dumps(brand_meta, ensure_ascii=False)
    heroimg_json = json.dumps(hero_images, ensure_ascii=False)

    with open(os.path.join(os.path.dirname(__file__), "catalog_template.html")) as fh:
        template = fh.read()

    html_out = (template
        .replace("__DATA_JSON__", data_json)
        .replace("__BRANDS_JSON__", brands_json)
        .replace("__CATEGORIES_JSON__", categories_json)
        .replace("__RANGES_JSON__", ranges_json)
        .replace("__BUDGETBUCKETS_JSON__", budget_buckets_json)
        .replace("__CATMETA_JSON__", catmeta_json)
        .replace("__BRANDMETA_JSON__", brandmeta_json)
        .replace("__HEROIMG_JSON__", heroimg_json)
        .replace("__VERSION__", VERSION_TAG)
        .replace("__TOTAL__", str(len(slim)))
        .replace("__BRANDCOUNT__", str(len(authorised_brand_names)))
        .replace("__GENDATE__", date.today().strftime("%d %b %Y")))

    out_path = os.path.join(SITE_DIR, "index.html")
    with open(out_path, "w") as fh:
        fh.write(html_out)
    print("Wrote", out_path, f"({len(html_out)/1024:.0f} KB)")

if __name__ == "__main__":
    main()
