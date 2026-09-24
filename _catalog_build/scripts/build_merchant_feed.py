# -*- coding: utf-8 -*-
"""
Generates a Google Merchant Center product feed (RSS 2.0 + g: namespace,
per https://support.google.com/merchants/answer/7052112) at
_catalog_build/site/google-merchant-feed.xml.

Why: individual product pages (build_product_pages.py) give Google a
crawlable URL per product, but Shopping-style results (the "nearby"/
price-carousel results in Google Search, and the Shopping tab) come
from a separate structured feed submitted to Merchant Center, not from
crawling. This feed points each entry at its matching /products/<slug>/
page so title/price/availability shown to Google match what a visitor
sees on click-through, which Merchant Center requires.

Run AFTER build_product_pages.py (needs the same product_id -> slug
mapping) and BEFORE finalize_site_assets.py is not required, but keep
it late in the pipeline since it reads master_consolidated.json as the
source of truth for price/availability.
"""
import json, os, re, html

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
SITE_DIR = os.path.join(BASE, "_catalog_build", "site")
PRIMARY_DOMAIN = "https://corporategiftingindia.co"


def slugify(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def product_url(r):
    base = slugify(f"{r['brand']} {r['product_name']}")[:70].strip("-")
    pid = r["product_id"].lower()
    slug = f"{base}-{pid}" if base else pid
    return f"{PRIMARY_DOMAIN}/products/{slug}/"


def abs_img(img):
    if not img:
        return ""
    if img.startswith("http://") or img.startswith("https://"):
        return img
    return f"{PRIMARY_DOMAIN}/images/{img}"


def esc(s):
    return html.escape(str(s or ""), quote=False)


def build():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    eligible = [
        r for r in recs
        if r.get("mrp") and r.get("category") != "Gift Cards" and r.get("image_file")
    ]

    items = []
    for r in eligible:
        name = r["product_name"]
        full_title = name if name.lower().startswith(r["brand"].lower()) else f"{r['brand']} {name}"
        title = esc(full_title[:150])
        desc = esc((r.get("description") or r.get("key_specs") or r["product_name"])[:5000])
        link = esc(product_url(r))
        img = esc(abs_img(r["image_file"]))
        price = f"{r['mrp']:.2f} INR"
        gid = esc(r["product_id"])
        brand = esc(r["brand"])
        item = f"""  <item>
    <g:id>{gid}</g:id>
    <title>{title}</title>
    <description>{desc}</description>
    <link>{link}</link>
    <g:image_link>{img}</g:image_link>
    <g:availability>in stock</g:availability>
    <g:price>{price}</g:price>
    <g:condition>new</g:condition>
    <g:brand>{brand}</g:brand>
    <g:identifier_exists>no</g:identifier_exists>
  </item>"""
        items.append(item)

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">
<channel>
  <title>Corporate Gifting India — Product Feed</title>
  <link>{PRIMARY_DOMAIN}/</link>
  <description>Bulk corporate gifting catalog by Nalanda Enterprises — {len(items)} products with verified MRP.</description>
{chr(10).join(items)}
</channel>
</rss>
"""
    out_path = os.path.join(SITE_DIR, "google-merchant-feed.xml")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(feed)
    print(f"Wrote google-merchant-feed.xml ({len(items)} products)")


if __name__ == "__main__":
    build()
