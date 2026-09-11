# -*- coding: utf-8 -*-
"""
Re-fetch Noise product images directly and carefully, into a DEDICATED
folder (images/noise_official/) that nothing else writes to — the shared
images/web/ pool has proven vulnerable to filename collisions across
different scraping waves silently overwriting each other's files.

Reuses the already-correct gonoise.com product-page slugs recorded in
noise_enrichment.json's mrp_source_url (verified real, unlike its
image_source_url field which mistakenly duplicated the same page URL).
"""
import json, os, re, time, ssl
import urllib.request

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
IMG_DIR = os.path.join(BASE, "_catalog_build", "images", "noise_official")
os.makedirs(IMG_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
SSL_CTX = ssl._create_unverified_context()

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
        return resp.read()

def norm_key(name):
    return re.sub(r'[^a-z0-9]+', '', (name or "").lower())

def main():
    enrich = json.load(open(os.path.join(OUT_DIR, "noise_enrichment.json")))
    master = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    noise_by_key = {norm_key(r["product_name"]): r for r in master if r.get("brand") == "Noise"}

    results = []
    slug_cache = {}
    for item in enrich:
        pname = item["product_name"]
        page_url = item.get("mrp_source_url", "")
        m = re.search(r'/products/([a-z0-9-]+)', page_url)
        if not m:
            print("NO SLUG:", pname)
            continue
        slug = m.group(1)
        try:
            if slug not in slug_cache:
                data = json.loads(fetch(f"https://www.gonoise.com/products/{slug}.json"))
                slug_cache[slug] = data
            product = slug_cache[slug].get("product", {})
        except Exception as e:
            print("FETCH FAIL:", slug, e)
            continue

        # find the variant whose title best matches this record's colour/name tail
        variants = product.get("variants", [])
        images = product.get("images", [])
        img_by_id = {im["id"]: im["src"] for im in images}
        chosen_src = None
        tail = pname.split(" - ")[-1].strip().lower() if " - " in pname else ""
        for v in variants:
            vtitle = (v.get("title") or "").lower()
            if tail and tail in vtitle and v.get("image_id") in img_by_id:
                chosen_src = img_by_id[v["image_id"]]
                break
        if not chosen_src and images:
            chosen_src = images[0]["src"]
        if not chosen_src:
            print("NO IMAGE:", pname)
            continue
        if chosen_src.startswith("//"):
            chosen_src = "https:" + chosen_src

        rec = noise_by_key.get(norm_key(pname))
        if not rec:
            print("NO MASTER MATCH:", pname)
            continue
        pid = rec["product_id"]
        ext = ".jpg"
        if ".png" in chosen_src.lower():
            ext = ".png"
        fname = f"{pid}{ext}"
        fpath = os.path.join(IMG_DIR, fname)
        try:
            blob = fetch(chosen_src)
            open(fpath, "wb").write(blob)
        except Exception as e:
            print("DOWNLOAD FAIL:", pname, e)
            continue

        results.append({"product_id": pid, "product_name": pname, "image_local_path": f"noise_official/{fname}", "image_source_url": chosen_src})
        print("OK:", pname, "->", chosen_src[:80])
        time.sleep(0.15)

    json.dump(results, open(os.path.join(OUT_DIR, "noise_images_v2.json"), "w"), indent=1, ensure_ascii=False)
    print(f"\nDone: {len(results)}/{len(enrich)} images fetched")

if __name__ == "__main__":
    main()
