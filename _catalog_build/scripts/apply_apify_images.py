# -*- coding: utf-8 -*-
"""
Applies Apify (Google Images) search results to master_consolidated.json.

Input:  output/apify/queue.json      — products searched (reason: 'missing' | 'low')
        output/apify/results_*.json  — per-product picks {product_id, image_url,
                                        confidence, source_domain, matched_title}
Rules (conservative — never downgrade an existing image):
  * reason == 'missing' -> accept 'high' or 'medium' confidence picks
  * reason == 'low'     -> accept only 'high' confidence picks (replaces the
                           existing low-confidence image)
  * Everything else in the catalog is left untouched.

Run BEFORE build_html.py / build_product_pages.py / build_seo_pages.py /
build_budget_pages.py / build_merchant_feed.py so the new images flow through.
"""
import glob, json, os, re
from datetime import date

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
APIFY_DIR = os.path.join(OUT_DIR, "apify")

BAD_HOST = re.compile(r"(encrypted-tbn\d*\.gstatic\.com|lookaside\.|fbsbx|instagram|pinimg|pinterest|ytimg|twimg|x\.com/)", re.I)
IMG_EXT = re.compile(r"\.(jpe?g|png|webp)(\?|$)|/image/|/images/|cdn|media", re.I)


def clean_url(u):
    u = (u or "").strip()
    # Amazon: strip the resize suffix (…/I/ABC._AC_UF350,350_QL80_.jpg -> …/I/ABC.jpg)
    m = re.match(r"(https://m\.media-amazon\.com/images/I/[^.]+)\.[^/]*\.(jpg|png|webp)$", u)
    if m:
        u = f"{m.group(1)}.{m.group(2)}"
    return u


def usable(u):
    return u.startswith("https://") and not BAD_HOST.search(u) and IMG_EXT.search(u)


def main():
    queue = {q["product_id"]: q for q in json.load(open(os.path.join(APIFY_DIR, "queue.json")))}
    picks = {}
    for path in sorted(glob.glob(os.path.join(APIFY_DIR, "results_*.json"))):
        for r in json.load(open(path)):
            if r.get("product_id") in queue:
                picks[r["product_id"]] = r

    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    today = date.today().isoformat()
    stats = {"missing_filled": 0, "low_replaced": 0, "rejected": 0, "no_result": 0}
    for rec in recs:
        q = queue.get(rec["product_id"])
        if not q:
            continue
        p = picks.get(rec["product_id"])
        if not p or not p.get("image_url"):
            stats["no_result"] += 1
            continue
        conf = (p.get("confidence") or "").lower()
        url = clean_url(p["image_url"])
        ok_conf = conf in ("high", "medium") if q["reason"] == "missing" else conf == "high"
        if not ok_conf or not usable(url):
            stats["rejected"] += 1
            continue
        # Guard: only touch records still in the state we queued them in.
        if q["reason"] == "missing" and rec.get("image_file"):
            continue
        if q["reason"] == "low" and rec.get("image_file") != q["current"]:
            continue
        rec["image_file"] = url
        rec["image_source"] = f"Apify Google Images ({conf} confidence): {p.get('source_domain', '')}"
        rec["date_last_updated"] = today
        stats["missing_filled" if q["reason"] == "missing" else "low_replaced"] += 1

    with open(os.path.join(OUT_DIR, "master_consolidated.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
    print(stats)


if __name__ == "__main__":
    main()
