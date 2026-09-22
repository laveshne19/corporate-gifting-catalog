# -*- coding: utf-8 -*-
"""
Generates one crawlable static page per product under
_catalog_build/site/products/<slug>-<id>/index.html.

Why: the homepage is a single-page app that renders all ~12,400 products
from one embedded JSON blob, and the brand/category landing pages only
show a capped sample (60) of products each. Neither gives Google (or an
AI answer engine) a dedicated, indexable URL for an individual product,
so a search for a specific product name + "corporate gift" has nothing
of ours to rank. These pages fill that gap: one small, fast, real HTML
document per product, each with unique title/meta/Product JSON-LD,
linking back to its brand page, category page, a matching budget page,
and a handful of related products for internal link equity.

Run AFTER build_seo_pages.py (needs seo_page_urls.json's brand/category
slugs) and BEFORE finalize_site_assets.py (which reads product URLs into
sitemap.xml).
"""
import json, os, re, html
from collections import defaultdict

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
SITE_DIR = os.path.join(BASE, "_catalog_build", "site")
PRIMARY_DOMAIN = "https://corporategiftingindia.co"
NAVY = "#0f2a4a"

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

CONTACT_PHONE = "919115513366"
CONTACT_EMAIL = "info@nalandaenterprises.com"


def slugify(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def fmt_price(p):
    if not p:
        return "Price on request"
    return f"Rs.{p:,.0f}"


def img_url(rel_prefix, img):
    if not img:
        return ""
    if img.startswith("http://") or img.startswith("https://"):
        return img
    return f"{rel_prefix}images/{img}"


def abs_img_url(img):
    if not img:
        return f"{PRIMARY_DOMAIN}/images/_brand/logo_512.png"
    if img.startswith("http://") or img.startswith("https://"):
        return img
    return f"{PRIMARY_DOMAIN}/images/{img}"


def budget_slug_for(mrp):
    if not mrp:
        return None
    if mrp < 500:
        return "under-500"
    if mrp < 1000:
        return "500-1000"
    if mrp < 2000:
        return "1000-2000"
    if mrp < 3000:
        return "2000-3000"
    if mrp < 5000:
        return "3000-5000"
    if mrp < 10000:
        return "5000-10000"
    return "above-10000"


def wa_link(r):
    msg = (f"Hi, I'd like to enquire about bulk corporate gifting of "
           f"{r['product_name']} ({r['brand']}) — Product ID {r['product_id']}, "
           f"listed MRP {fmt_price(r.get('mrp'))}. Please share dealer/bulk pricing.")
    from urllib.parse import quote
    return f"https://wa.me/{CONTACT_PHONE}?text={quote(msg)}"


def mailto_link(r):
    subj = f"Bulk Enquiry: {r['product_name']} ({r['brand']})"
    body = (f"Hello,\n\nI'd like to enquire about bulk corporate gifting pricing for:\n\n"
            f"Product: {r['product_name']}\nBrand: {r['brand']}\nProduct ID: {r['product_id']}\n"
            f"Listed MRP: {fmt_price(r.get('mrp'))}\n\nPlease share bulk/dealer pricing and lead time.\n\nThanks.")
    from urllib.parse import quote
    return f"mailto:{CONTACT_EMAIL}?subject={quote(subj)}&body={quote(body)}"


def mini_card(rel, r):
    img = img_url(rel, r.get("image_file"))
    name = html.escape(r["product_name"])
    brand = html.escape(r["brand"])
    price = fmt_price(r.get("mrp"))
    slug = product_url(r)
    img_tag = (f'<img src="{img}" alt="{name} — {brand}" loading="lazy">' if img
               else '<div class="ph">No image</div>')
    return f'''<a class="pcard" href="{rel}{slug}">
  <div class="pcard-img">{img_tag}</div>
  <div class="pcard-brand">{brand}</div>
  <div class="pcard-name">{name}</div>
  <div class="pcard-price">{price}</div>
</a>'''


_seen_slugs = {}


def product_url(r):
    """/products/<slug>-<id>/ — cached so it's computed once per record."""
    pid = r["product_id"]
    if pid in _seen_slugs:
        return _seen_slugs[pid]
    base_slug = slugify(f"{r['brand']} {r['product_name']}")[:70].strip("-")
    slug = f"{base_slug}-{pid.lower()}" if base_slug else pid.lower()
    url = f"products/{slug}/"
    _seen_slugs[pid] = url
    return url


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
<meta property="og:type" content="product">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Corporate Gifting India">
<meta property="og:image" content="{img_abs}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{description}">
<script type="application/ld+json">{product_ld}</script>
<script type="application/ld+json">{breadcrumb_ld}</script>
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
.wrap{{max-width:1120px;margin:0 auto;padding:0 24px;}}
nav.topnav{{background:var(--navy-dark);padding:16px 0;}}
nav.topnav .wrap{{display:flex;align-items:center;justify-content:space-between;}}
.logo{{color:#fff;font-size:17px;font-weight:800;}}
.logo b{{color:var(--accent-light);}}
.nav-cta{{background:linear-gradient(135deg,var(--accent),#c06a1a);color:#1b1200;padding:9px 18px;border-radius:24px;font-size:13px;font-weight:800;}}
.breadcrumb{{font-size:12.5px;color:var(--muted);padding:18px 0 0;}}
.breadcrumb a{{color:var(--accent);font-weight:700;}}
.pdp{{display:grid;grid-template-columns:380px 1fr;gap:40px;padding:24px 0 10px;}}
@media (max-width:820px){{.pdp{{grid-template-columns:1fr;}}}}
.pdp-img{{background:#fff;border:1px solid var(--border);border-radius:16px;padding:20px;display:flex;align-items:center;justify-content:center;aspect-ratio:1;}}
.pdp-img img{{max-height:100%;object-fit:contain;}}
.eyebrow{{font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:var(--accent);}}
h1{{font-size:28px;line-height:1.25;margin:8px 0 10px;font-weight:800;color:var(--navy);}}
.pdp-brand{{font-size:14px;color:var(--muted);margin-bottom:14px;}}
.pdp-brand a{{color:var(--accent);font-weight:700;}}
.price-row{{display:flex;align-items:baseline;gap:10px;margin:16px 0 6px;}}
.price{{font-size:32px;font-weight:800;color:var(--navy);font-family:'Fraunces',serif;}}
.price-label{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;}}
.meta-list{{list-style:none;padding:0;margin:18px 0;border-top:1px solid var(--border);}}
.meta-list li{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--border);font-size:14px;}}
.meta-list b{{color:var(--muted);font-weight:600;}}
.cta-row{{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px;}}
.btn-wa,.btn-enq,.btn-primary{{display:inline-flex;align-items:center;gap:8px;padding:13px 22px;border-radius:28px;font-weight:800;font-size:14px;}}
.btn-wa{{background:#25D366;color:#fff;}}
.btn-enq{{background:var(--navy);color:#fff;}}
.btn-primary{{background:linear-gradient(135deg,var(--accent),#c06a1a);color:#1b1200;}}
.desc-block{{margin-top:34px;line-height:1.7;color:#374252;max-width:760px;}}
.desc-block h2{{font-size:19px;color:var(--navy);margin:0 0 10px;}}
.related h2{{font-size:19px;color:var(--navy);margin:36px 0 14px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:16px;padding-bottom:40px;}}
.pcard{{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;display:block;}}
.pcard-img{{aspect-ratio:1;background:#fff;display:flex;align-items:center;justify-content:center;padding:10px;}}
.pcard-img img{{max-height:100%;object-fit:contain;}}
.pcard-img .ph{{color:var(--muted);font-size:12px;}}
.pcard-brand{{font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:.4px;color:var(--accent);padding:10px 12px 0;}}
.pcard-name{{font-size:13px;font-weight:700;padding:4px 12px;line-height:1.35;min-height:2.6em;}}
.pcard-price{{font-size:14px;font-weight:800;color:var(--navy);padding:0 12px 12px;}}
.browse-links{{display:flex;flex-wrap:wrap;gap:10px;padding:10px 0 40px;}}
.browse-links a{{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:7px 16px;font-size:12.5px;font-weight:700;color:var(--navy);}}
footer{{padding:26px 0;border-top:1px solid var(--border);color:var(--muted);font-size:12.5px;}}
.float-wa{{position:fixed;right:20px;bottom:86px;z-index:80;display:flex;align-items:center;gap:9px;background:#25D366;color:#fff;padding:13px;border-radius:50px;box-shadow:0 8px 24px rgba(37,211,102,.45);text-decoration:none;}}
.float-wa svg{{width:24px;height:24px;flex:none;}}
.float-wa-label{{max-width:0;overflow:hidden;opacity:0;white-space:nowrap;font-size:13.5px;font-weight:700;}}
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
  <div class="breadcrumb">{breadcrumb_html}</div>
  <div class="pdp">
    <div class="pdp-img">{img_tag}</div>
    <div>
      <span class="eyebrow">{category_esc}</span>
      <h1>{name_esc}</h1>
      <div class="pdp-brand">by <a href="{rel}{brand_url}">{brand_esc}</a> &middot; Product ID {pid}</div>
      <div class="price-row">
        <span class="price">{price}</span>
        <span class="price-label">MRP, bulk/dealer pricing on request</span>
      </div>
      <ul class="meta-list">
        {meta_rows}
      </ul>
      <div class="cta-row">
        <a class="btn-wa" href="{wa}" target="_blank" rel="noopener">WhatsApp Enquiry</a>
        <a class="btn-enq" href="{mail}">Enquire by Email</a>
        <a class="btn-primary" href="{rel}?q={q}">Compare in Full Catalog &rarr;</a>
      </div>
    </div>
  </div>
  <div class="desc-block">
    <h2>Bulk &amp; corporate gifting for {name_esc}</h2>
    <p>{story}</p>
  </div>
  <div class="related">
    <h2>More {brand_esc} corporate gifts</h2>
    <div class="grid">{related_cards}</div>
  </div>
  <h2 style="font-size:16px;color:var(--muted);margin:0 0 10px;font-family:inherit;">Explore by budget</h2>
  <div class="browse-links">{budget_links}</div>
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

BUDGET_LABELS = [
    ("under-500", "Under Rs.500"), ("500-1000", "Rs.500 - Rs.1,000"),
    ("1000-2000", "Rs.1,000 - Rs.2,000"), ("2000-3000", "Rs.2,000 - Rs.3,000"),
    ("3000-5000", "Rs.3,000 - Rs.5,000"), ("5000-10000", "Rs.5,000 - Rs.10,000"),
    ("above-10000", "Above Rs.10,000"),
]


def build():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    site_meta = json.load(open(os.path.join(OUT_DIR, "site_meta.json")))
    brand_slug_map = {m["name"]: slugify(m["name"]) for m in site_meta["brand_meta"]}
    cat_slug_map = {m["name"]: slugify(m["name"]) for m in site_meta["cat_meta"]}

    eligible = [r for r in recs if r.get("mrp") and r.get("category") != "Gift Cards"]
    for r in eligible:
        product_url(r)  # pre-compute+cache unique slugs

    by_brand = defaultdict(list)
    for r in eligible:
        by_brand[r["brand"]].append(r)

    rel = "../../"
    written = []
    for idx, r in enumerate(eligible):
        pid = r["product_id"]
        name = r["product_name"]
        brand = r["brand"]
        category = r.get("category") or "Corporate Gifts"
        mrp = r.get("mrp")
        url_path = "/" + product_url(r)
        canonical = f"{PRIMARY_DOMAIN}{url_path}"
        brand_slug = brand_slug_map.get(brand, slugify(brand))
        cat_slug = cat_slug_map.get(category, slugify(category))
        brand_url = f"brands/{brand_slug}/"
        cat_url = f"categories/{cat_slug}/" if category in cat_slug_map else None
        b_slug = budget_slug_for(mrp)

        title = f"{name} — Bulk Corporate Gift | {brand} | Corporate Gifting India"
        og_title = f"{name} — {brand} Corporate Gift"
        description = (f"{name} by {brand} for bulk corporate gifting — MRP {fmt_price(mrp)}. "
                        f"Sourced and supplied in bulk by Nalanda Enterprises for employee rewards, "
                        f"dealer stock and festive gifting across India.")[:157]
        img = r.get("image_file")
        img_tag = (f'<img src="{img_url(rel, img)}" alt="{html.escape(name)} — {html.escape(brand)}" loading="lazy">'
                    if img else '<div class="ph">No image available</div>')
        img_abs = abs_img_url(img)

        meta_rows_list = []
        if r.get("sub_category"):
            meta_rows_list.append(("Sub-category", r["sub_category"]))
        meta_rows_list.append(("Category", category))
        if r.get("model_code"):
            meta_rows_list.append(("Model", r["model_code"]))
        if r.get("variant"):
            meta_rows_list.append(("Variant", r["variant"]))
        if r.get("warranty"):
            meta_rows_list.append(("Warranty", r["warranty"]))
        meta_rows_list.append(("Availability", "In stock (bulk order)"))
        meta_rows = "\n".join(
            f"<li><b>{html.escape(k)}</b><span>{html.escape(str(v))}</span></li>" for k, v in meta_rows_list
        )

        story = (f"Looking to buy {html.escape(name)} in bulk for corporate gifting, employee rewards, "
                 f"dealer stock or a festive gifting program? Nalanda Enterprises, an authorised "
                 f"{html.escape(brand)} corporate gifting partner based in Chandigarh, supplies this "
                 f"product at bulk/dealer pricing across India, with {html.escape(category.lower())} "
                 f"options in every budget band from {html.escape(brand)}'s full range. "
                 f"Message us on WhatsApp for a bulk quote, minimum order quantity and delivery timelines.")

        breadcrumb_items = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{PRIMARY_DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Brands", "item": f"{PRIMARY_DOMAIN}/brands/"},
            {"@type": "ListItem", "position": 3, "name": brand, "item": f"{PRIMARY_DOMAIN}/{brand_url}"},
            {"@type": "ListItem", "position": 4, "name": name, "item": canonical},
        ]
        breadcrumb_html = (
            f'<a href="{rel}">Home</a> &rsaquo; <a href="{rel}{brand_url}">{html.escape(brand)}</a> &rsaquo; {html.escape(name)}'
        )
        breadcrumb_ld = json.dumps({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": breadcrumb_items,
        }, ensure_ascii=False)

        product_ld = json.dumps({
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "brand": {"@type": "Brand", "name": brand},
            "category": category,
            "image": img_abs,
            "description": description,
            "sku": pid,
            "offers": {
                "@type": "Offer",
                "url": canonical,
                "priceCurrency": "INR",
                "price": mrp,
                "availability": "https://schema.org/InStock",
                "itemCondition": "https://schema.org/NewCondition",
                "seller": {"@type": "Organization", "name": "Nalanda Enterprises"},
            },
        }, ensure_ascii=False)

        related = [x for x in by_brand.get(brand, []) if x["product_id"] != pid][:8]
        related_cards = "\n".join(mini_card(rel, x) for x in related)

        budget_links = "\n".join(
            f'<a href="{rel}budget/{slug}/">{label}</a>' + (' &larr;' if slug == b_slug else '')
            for slug, label in BUDGET_LABELS
        )

        page = PAGE_TEMPLATE.format(
            gtm_head=GTM_HEAD, gtm_body=GTM_BODY, title=html.escape(title),
            description=html.escape(description), canonical=canonical, rel=rel, navy=NAVY,
            og_title=html.escape(og_title), img_abs=img_abs, product_ld=product_ld,
            breadcrumb_ld=breadcrumb_ld, breadcrumb_html=breadcrumb_html, img_tag=img_tag,
            category_esc=html.escape(category), name_esc=html.escape(name),
            brand_url=brand_url, brand_esc=html.escape(brand), pid=pid,
            price=fmt_price(mrp), meta_rows=meta_rows, wa=wa_link(r), mail=mailto_link(r),
            q=html.escape(name).replace(" ", "%20"), story=story, related_cards=related_cards,
            budget_links=budget_links,
        )
        dir_path = os.path.join(SITE_DIR, url_path.strip("/"))
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, "index.html"), "w") as fh:
            fh.write(page)
        written.append(url_path)

    with open(os.path.join(OUT_DIR, "product_page_urls.json"), "w") as fh:
        json.dump(written, fh)
    print(f"Wrote {len(written)} individual product pages")


if __name__ == "__main__":
    build()
