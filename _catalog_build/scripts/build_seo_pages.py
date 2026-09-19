# -*- coding: utf-8 -*-
"""
Generates crawlable static landing pages — one per authorised brand and one
per top-level category — under _catalog_build/site/brands/<slug>/index.html
and _catalog_build/site/categories/<slug>/index.html.

Why: the homepage is a single-page app that renders all 12,310 products
from one embedded JSON blob, so Google/AI crawlers can only ever index that
one URL. These pages are separate, server-rendered HTML documents — real
crawlable content (product names, images, prices) plus unique title/meta/
JSON-LD per page — that give search and AI-answer engines ~65 additional
indexable entry points into the catalogue, each linking back to the live
searchable homepage for the full experience.

Run AFTER build_html.py (consumes _catalog_build/output/site_meta.json,
which build_html.py writes) and BEFORE finalize_site_assets.py (which reads
these pages' URLs into sitemap.xml).
"""
import json, os, re, html
from datetime import date

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
SITE_DIR = os.path.join(BASE, "_catalog_build", "site")
PRIMARY_DOMAIN = "https://corporategiftingindia.co"
PAGE_CAP = 60  # products shown per landing page — mirrors the homepage's PAGE_SIZE

NAVY = "#0f2a4a"
TOTAL_PRODUCTS = "12,310"  # overwritten from site_meta.json in main()

GTM_ID = "GTM-PHBBN49S"
GTM_HEAD = f"""<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{GTM_ID}');</script>
<!-- End Google Tag Manager -->"""
GTM_BODY = f"""<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->"""


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def fmt_price(p):
    if p is None:
        return "Price on request"
    return f"Rs.{p:,.0f}"


def img_url(rel_prefix, img):
    if not img:
        return ""
    if img.startswith("http://") or img.startswith("https://"):
        return img
    return f"{rel_prefix}images/{img}"


def product_card(rel_prefix, r):
    img = img_url(rel_prefix, r.get("image_file"))
    name = html.escape(r["product_name"])
    brand = html.escape(r["brand"])
    price = fmt_price(r.get("mrp"))
    img_tag = (f'<img src="{img}" alt="{name} — {brand}" loading="lazy">' if img
               else '<div class="ph">No image</div>')
    return f'''<div class="pcard">
  <div class="pcard-img">{img_tag}</div>
  <div class="pcard-brand">{brand}</div>
  <div class="pcard-name">{name}</div>
  <div class="pcard-price">{price}</div>
</div>'''


def abs_img_url(img):
    """Always-absolute image URL for JSON-LD, regardless of page depth."""
    if not img:
        return ""
    if img.startswith("http://") or img.startswith("https://"):
        return img
    return f"{PRIMARY_DOMAIN}/images/{img}"


def product_jsonld(items, page_url):
    entries = []
    for i, r in enumerate(items, 1):
        img = abs_img_url(r.get("image_file"))
        entry = {
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "Product",
                "name": r["product_name"],
                "brand": {"@type": "Brand", "name": r["brand"]},
                "category": r.get("category") or "",
            }
        }
        if img:
            entry["item"]["image"] = img
        if r.get("mrp"):
            entry["item"]["offers"] = {
                "@type": "Offer",
                "price": r["mrp"],
                "priceCurrency": "INR",
                "availability": "https://schema.org/InStock",
                "url": page_url,
            }
        entries.append(entry)
    return {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": entries,
    }


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
{gtm_head}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/png" sizes="32x32" href="{rel}images/_brand/favicon_32.png">
<link rel="shortcut icon" href="{rel}images/_brand/favicon.ico">
<meta name="theme-color" content="{navy}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Corporate Gifting India">
<meta property="og:image" content="{PRIMARY_DOMAIN}/images/_brand/logo_512.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{description}">
<script type="application/ld+json">{breadcrumb_ld}</script>
<script type="application/ld+json">{itemlist_ld}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,800;1,9..144,600&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{--navy:#0f2a4a;--navy-dark:#08172b;--accent:#d98b2b;--accent-light:#f0b866;--bg:#f7f5f0;--card:#ffffff;--text:#1c2733;--muted:#6b7785;--border:#e6e2d8;}}
*{{box-sizing:border-box;}}
body{{margin:0;font-family:'Manrope',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text);}}
h1,h2,.logo{{font-family:'Fraunces',Georgia,serif;}}
a{{color:inherit;text-decoration:none;}}
img{{max-width:100%;}}
.wrap{{max-width:1280px;margin:0 auto;padding:0 24px;}}
nav.topnav{{background:var(--navy-dark);padding:16px 0;}}
nav.topnav .wrap{{display:flex;align-items:center;justify-content:space-between;}}
.logo{{color:#fff;font-size:17px;font-weight:800;}}
.logo b{{color:var(--accent-light);}}
.nav-cta{{background:linear-gradient(135deg,var(--accent),#c06a1a);color:#1b1200;padding:9px 18px;border-radius:24px;font-size:13px;font-weight:800;}}
.breadcrumb{{font-size:12.5px;color:var(--muted);padding:18px 0 0;}}
.breadcrumb a{{color:var(--accent);font-weight:700;}}
header.page-hero{{padding:18px 0 34px;}}
.eyebrow{{font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:var(--accent);}}
h1{{font-size:34px;line-height:1.2;margin:10px 0 12px;font-weight:800;color:var(--navy);}}
.page-sub{{color:var(--muted);font-size:15px;max-width:680px;line-height:1.6;margin:0 0 22px;}}
.stat-row{{display:flex;gap:24px;flex-wrap:wrap;margin-bottom:8px;}}
.stat{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 20px;}}
.stat b{{display:block;font-size:22px;color:var(--navy);font-family:'Fraunces',serif;}}
.stat span{{font-size:11.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;}}
.btn-primary{{display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,var(--accent),#c06a1a);color:#1b1200;padding:13px 24px;border-radius:28px;font-weight:800;font-size:14px;margin-top:18px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:18px;padding:10px 0 40px;}}
.pcard{{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;}}
.pcard-img{{aspect-ratio:1;background:#fff;display:flex;align-items:center;justify-content:center;padding:10px;}}
.pcard-img img{{max-height:100%;object-fit:contain;}}
.pcard-img .ph{{color:var(--muted);font-size:12px;}}
.pcard-brand{{font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:.4px;color:var(--accent);padding:10px 12px 0;}}
.pcard-name{{font-size:13.5px;font-weight:700;padding:4px 12px;line-height:1.35;min-height:2.7em;}}
.pcard-price{{font-size:15px;font-weight:800;color:var(--navy);padding:0 12px 12px;}}
section.more{{background:var(--navy-dark);color:#fff;padding:40px 0;margin-top:20px;}}
section.more h2{{font-size:24px;margin:0 0 10px;}}
section.more p{{color:#c7d3e0;max-width:620px;line-height:1.6;}}
.browse-links{{display:flex;flex-wrap:wrap;gap:10px;padding:24px 0 50px;}}
.browse-links a{{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:7px 16px;font-size:12.5px;font-weight:700;color:var(--navy);}}
footer{{padding:26px 0;border-top:1px solid var(--border);color:var(--muted);font-size:12.5px;}}
.float-wa{{position:fixed;right:20px;bottom:86px;z-index:80;display:flex;align-items:center;gap:9px;background:#25D366;color:#fff;padding:13px;border-radius:50px;box-shadow:0 8px 24px rgba(37,211,102,.45);transition:box-shadow .2s ease,transform .2s ease;text-decoration:none;}}
.float-wa svg{{width:24px;height:24px;flex:none;}}
.float-wa-label{{max-width:0;overflow:hidden;opacity:0;white-space:nowrap;font-size:13.5px;font-weight:700;transition:max-width .25s ease,opacity .2s ease;}}
.float-wa:hover{{box-shadow:0 10px 30px rgba(37,211,102,.6);transform:translateY(-2px);}}
.float-wa:hover .float-wa-label{{max-width:120px;opacity:1;}}
@media (max-width:640px){{.float-wa{{right:14px;bottom:80px;padding:12px;}} .float-wa-label{{display:none;}}}}
</style>
</head>
<body>
{gtm_body}
<nav class="topnav"><div class="wrap">
  <a class="logo" href="{rel}"><b>Corporate</b> Gifting India</a>
  <a class="nav-cta" href="{rel}">Search Full Catalog</a>
</div></nav>
<div class="wrap">
  <div class="breadcrumb"><a href="{rel}">Home</a> &rsaquo; {breadcrumb_label}</div>
  <header class="page-hero">
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p class="page-sub">{intro}</p>
    <div class="stat-row">
      <div class="stat"><b>{count}</b><span>Products</span></div>
      <div class="stat"><b>{price_lo}</b><span>Starting From</span></div>
    </div>
    <a class="btn-primary" href="{deep_link}">Search &amp; Filter Live Catalog &rarr;</a>
  </header>
  <div class="grid">
    {cards}
  </div>
</div>
<section class="more"><div class="wrap">
  <h2>{count} products, {total} in the full catalogue</h2>
  <p>This page shows a sample of {shown} {label_lower} products with verified MRP. Nalanda Enterprises sources and supplies these in bulk for corporate gifting, dealer stock and employee reward programs across India — search the live catalog for the complete range, budget filters and every colour/variant.</p>
  <a class="btn-primary" href="{deep_link}">Open Full Catalog &rarr;</a>
</div></section>
<div class="wrap">
  <h2 style="font-size:16px;color:var(--muted);margin:26px 0 10px;font-family:inherit;">Browse other {other_label}</h2>
  <div class="browse-links">{other_links}</div>
</div>
<footer><div class="wrap">
  Nalanda Enterprises &middot; Chandigarh &middot; Authorised Corporate Gifting Partner &middot; <a href="{rel}">corporategiftingindia.co</a>
</div></footer>
<a class="float-wa" href="https://wa.me/919115513366?text=Hi%2C%20I%27d%20like%20to%20enquire%20about%20corporate%20gifting%20options." target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.29-1.39c1.44.79 3.06 1.2 4.71 1.2h.01c5.46 0 9.91-4.45 9.91-9.91C21.92 6.45 17.5 2 12.04 2zm5.8 14.02c-.24.68-1.4 1.3-1.93 1.38-.49.08-1.11.11-1.79-.11-.41-.13-.94-.31-1.62-.6-2.85-1.23-4.71-4.1-4.85-4.29-.14-.19-1.16-1.54-1.16-2.94 0-1.4.73-2.08 1-2.37.26-.28.57-.35.76-.35h.55c.18 0 .41-.07.64.49.24.57.81 1.98.88 2.12.07.14.11.31.02.5-.09.19-.14.31-.28.47-.14.16-.29.36-.42.48-.14.14-.28.28-.12.55.16.28.71 1.17 1.53 1.9 1.05.94 1.94 1.23 2.21 1.37.28.14.44.12.6-.07.16-.19.68-.79.86-1.06.18-.28.36-.23.6-.14.24.09 1.55.73 1.82.86.27.14.44.2.51.32.07.11.07.65-.17 1.33z"/></svg>
  <span class="float-wa-label">Chat with us</span>
</a>
</body>
</html>"""


def build_pages(kind, meta_list, key_field, recs_by_key, other_kind, other_slugs, brand_logo_map=None):
    """kind: 'brand' or 'category'. Returns list of (url_path, out_file) written."""
    written = []
    rel = "../../"
    for m in meta_list:
        name = m["name"]
        slug = slugify(name)
        count = m["count"]
        items = recs_by_key.get(name, [])[:PAGE_CAP]
        if not items:
            continue

        if kind == "brand":
            dir_path = os.path.join(SITE_DIR, "brands", slug)
            url_path = f"/brands/{slug}/"
            eyebrow = "AUTHORISED BRAND"
            h1 = f"{name} Corporate Gifting Catalog"
            breadcrumb_label = f"Brands &rsaquo; {html.escape(name)}"
            og_title = f"{name} Corporate Gifts — Bulk Pricing | Corporate Gifting India"
            title = f"{name} Corporate Gifts India | Bulk {name} Products — Corporate Gifting India"
            top_cat = m.get("category", "")
            intro = (f"Bulk and corporate gifting supply of {html.escape(name)} products — "
                     f"{count} SKUs across {html.escape(top_cat)} and more, with verified MRP. "
                     f"Sourced and supplied in bulk by Nalanda Enterprises, an authorised {html.escape(name)} "
                     f"corporate gifting partner, for dealer stock, employee rewards and Diwali/festive gifting programs.")
            deep_link = f"{rel}?brand={name.replace(' ', '%20')}"
            label_lower = name
            other_label = "brands"
        else:
            dir_path = os.path.join(SITE_DIR, "categories", slug)
            url_path = f"/categories/{slug}/"
            eyebrow = "PRODUCT CATEGORY"
            h1 = f"{name} — Corporate Gifting Options"
            breadcrumb_label = f"Categories &rsaquo; {html.escape(name)}"
            og_title = f"{name} Corporate Gifts | Corporate Gifting India"
            title = f"{name} Corporate Gifts India | Bulk {name} Options — Corporate Gifting India"
            intro = (f"{count} {html.escape(name)} products across authorised brands, curated for bulk "
                     f"corporate gifting — verified MRP, budget filters and dealer-ready sourcing "
                     f"by Nalanda Enterprises.")
            deep_link = f"{rel}?cat={name.replace(' ', '%20')}"
            label_lower = name
            other_label = "categories"

        description = re.sub(r"<[^>]+>", "", intro)[:157] + "..."
        canonical = f"{PRIMARY_DOMAIN}{url_path}"

        priced = [r["mrp"] for r in items if r.get("mrp")]
        price_lo = fmt_price(min(priced)) if priced else "On request"

        cards = "\n".join(product_card(rel, r) for r in items)

        breadcrumb_ld = json.dumps({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{PRIMARY_DOMAIN}/"},
                {"@type": "ListItem", "position": 2, "name": name, "item": canonical},
            ]
        }, ensure_ascii=False)
        itemlist_ld = json.dumps(product_jsonld(items, canonical), ensure_ascii=False)

        others = [s for s in other_slugs if s[1] != slug][:14]
        other_links = "\n".join(
            f'<a href="{rel}{other_kind}/{s}/">{html.escape(n)}</a>' for n, s in others
        )

        page = PAGE_TEMPLATE.format(
            title=html.escape(title), description=html.escape(description), canonical=canonical,
            rel=rel, navy=NAVY, og_title=html.escape(og_title), PRIMARY_DOMAIN=PRIMARY_DOMAIN,
            gtm_head=GTM_HEAD, gtm_body=GTM_BODY,
            breadcrumb_ld=breadcrumb_ld, itemlist_ld=itemlist_ld,
            breadcrumb_label=breadcrumb_label, eyebrow=eyebrow, h1=html.escape(h1), intro=intro,
            count=count, price_lo=price_lo, deep_link=deep_link, cards=cards,
            total=TOTAL_PRODUCTS, shown=len(items), label_lower=html.escape(label_lower),
            other_label=other_label, other_links=other_links,
        )
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, "index.html"), "w") as fh:
            fh.write(page)
        written.append(url_path)
    return written


def main():
    global TOTAL_PRODUCTS
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    site_meta = json.load(open(os.path.join(OUT_DIR, "site_meta.json")))
    TOTAL_PRODUCTS = f"{site_meta['total']:,}"

    recs_by_brand = {}
    for r in recs:
        if r["category"] == "Gift Cards":
            continue
        recs_by_brand.setdefault(r["brand"], []).append(r)

    recs_by_cat = {}
    for r in recs:
        recs_by_cat.setdefault(r["category"], []).append(r)

    brand_slugs = [(m["name"], slugify(m["name"])) for m in site_meta["brand_meta"]]
    cat_slugs = [(m["name"], slugify(m["name"])) for m in site_meta["cat_meta"]]

    brand_urls = build_pages("brand", site_meta["brand_meta"], "brand", recs_by_brand,
                              "brands", brand_slugs)
    cat_urls = build_pages("category", site_meta["cat_meta"], "category", recs_by_cat,
                            "categories", cat_slugs)

    all_urls = brand_urls + cat_urls
    with open(os.path.join(OUT_DIR, "seo_page_urls.json"), "w") as fh:
        json.dump(all_urls, fh)

    print(f"Wrote {len(brand_urls)} brand pages + {len(cat_urls)} category pages = {len(all_urls)} SEO landing pages")


if __name__ == "__main__":
    main()
