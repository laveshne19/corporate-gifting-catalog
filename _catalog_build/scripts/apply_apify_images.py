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

BAD_HOST = re.compile(r"(encrypted-tbn\d*\.gstatic\.com|lookaside\.|fbsbx|instagram|pinimg|pinterest|ytimg|twimg|//(www\.)?x\.com/"
                      r"|corporategiftingindia\.|alienfox\.)", re.I)  # own site = circular; alienfox = placeholders
# Exact-model but small (~200-400px) images: good enough to fill a blank, not to replace an existing image.
LOW_RES_HOST = re.compile(r"(bajajfinserv|greateasternretail)", re.I)
IMG_EXT = re.compile(r"\.(jpe?g|png|webp)(\?|$)|/image/|/images/|cdn|media", re.I)


# Picks the search agents themselves flagged as wrong variant / unreliable source.
EXCLUDE = {
    "NE-00060",  # Luminarc Ingmar Blue: image is set V6605, not the listed set
    "NE-00295",  # Welspun Chair Towel: second-hand marketplace (freeup.app) photo
    # Whirlpool fridges where the image page title names a different print than the file name
    "NE-09796", "NE-09833", "NE-09870", "NE-09934",
    "NE-09725",  # Whirlpool: Shopify image id shared by two different models
}


def clean_url(u):
    u = (u or "").strip()
    if u.startswith("http://"):  # Shopify/CDN hosts serve the same file over https
        u = "https://" + u[len("http://"):]
    # Amazon: strip the resize suffix (…/I/ABC._AC_UF350,350_QL80_.jpg -> …/I/ABC.jpg)
    m = re.match(r"(https://m\.media-amazon\.com/images/I/[^.]+)\.[^/]*\.(jpg|png|webp)$", u)
    if m:
        u = f"{m.group(1)}.{m.group(2)}"
    return u


def usable(u):
    return u.startswith("https://") and not BAD_HOST.search(u) and IMG_EXT.search(u)


# Passes are applied in order; a later pass overrides an earlier one.
#   refresh : products with no image ('missing') or a low-confidence image ('low')
#   recheck : products whose image was proven wrong (shared across product types,
#             or another brand's photo) -> exact match or cleared
#   verify  : full-catalog re-verification (owner's rule: a photo stays only if it
#             is confirmed to be the exact product; otherwise "Image on request")
PASSES = [
    ("refresh", "queue.json", "results_[0-9]*.json"),
    ("recheck", "recheck_queue.json", "recheck_results.json"),
    ("verify", "verify_queue.json", "verify_results_*.json"),
]


def load_pass(queue_name, results_glob):
    qpath = os.path.join(APIFY_DIR, queue_name)
    if not os.path.exists(qpath):
        return {}, {}
    queue = {q["product_id"]: q for q in json.load(open(qpath))}
    picks = {}
    for path in sorted(glob.glob(os.path.join(APIFY_DIR, results_glob))):
        for r in json.load(open(path)):
            if r.get("product_id") in queue:
                picks[r["product_id"]] = r
    return queue, picks


def main():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    by_id = {r["product_id"]: r for r in recs}
    today = date.today().isoformat()
    for name, queue_name, results_glob in PASSES:
        queue, picks = load_pass(queue_name, results_glob)
        stats = {"set": 0, "kept": 0, "cleared": 0, "unchanged": 0, "rejected": 0}
        for pid, q in queue.items():
            rec = by_id.get(pid)
            if rec is None:
                continue
            p = picks.get(pid)
            if name != "refresh" and p is None:
                stats["unchanged"] += 1  # not processed yet (pass still running)
                continue
            if p and p.get("keep") and name == "verify":
                rec["image_source"] = "Verified exact match (Apify Google Images re-check)"
                rec["date_last_updated"] = today
                stats["kept"] += 1
                continue
            url = clean_url(p.get("image_url")) if p else ""
            conf = ((p or {}).get("confidence") or "").lower()
            if pid in EXCLUDE:
                url = ""
            if name == "refresh":
                ok = (conf in ("high", "medium") if q["reason"] == "missing" else conf == "high") and url
                ok = ok and usable(url) and not (q["reason"] == "low" and LOW_RES_HOST.search(url))
                if not ok:
                    stats["rejected" if url else "unchanged"] += 1
                    continue
                # Only touch records still in the state they were queued in.
                if (q["reason"] == "missing" and rec.get("image_file")) or \
                        (q["reason"] == "low" and rec.get("image_file") != q["current"]):
                    continue
            else:
                if not (conf == "high" and url and usable(url)):
                    rec["image_file"] = ""
                    rec["image_source"] = "Image on request (no exact-match photo confirmed)"
                    rec["date_last_updated"] = today
                    stats["cleared"] += 1
                    continue
            rec["image_file"] = url
            rec["image_source"] = f"Apify Google Images ({conf} confidence, {name}): {p.get('source_domain', '')}"
            rec["date_last_updated"] = today
            stats["set"] += 1
        if queue:
            print(name, stats)

    with open(os.path.join(OUT_DIR, "master_consolidated.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
