# -*- coding: utf-8 -*-
"""
Generates budget-band landing pages under
_catalog_build/site/budget/<slug>/index.html — e.g. /budget/2000-3000/.

Why: real buyer search intent for corporate gifting is overwhelmingly
budget-first ("corporate gifts under 500", "corporate gifting ideas in
2000-3000 budget"), but the site had no page targeting that intent at
all. Each page lists real, priced products in that band (linking to
their individual product pages), across multiple brands/categories, so
it can rank for budget + category queries and hands crawlers a dense
cluster of internal links into the product-page graph.

Run AFTER build_product_pages.py (needs product_page_urls.json / the
per-product slug so links resolve) and BEFORE finalize_site_assets.py.
"""
import json, os, re, html
from collections import defaultdict

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
SITE_DIR = os.path.join(BASE, "_catalog_build", "site")
PRIMARY_DOMAIN = "https://corporategiftingindia.co"
NAVY = "#0f2a4a"
PAGE_CAP = 80

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

BANDS = [
    ("under-500", "Under Rs.500", "Corporate Gifts Under Rs.500", 0, 500,
     "budget corporate gifts, giveaways and bulk small tokens for large employee/dealer counts"),
    ("500-1000", "Rs.500 - Rs.1,000", "Corporate Gifts Between Rs.500 and Rs.1,000", 500, 1000,
     "affordable corporate gifting for onboarding kits, festive tokens and dealer incentives"),
    ("1000-2000", "Rs.1,000 - Rs.2,000", "Corporate Gifts Between Rs.1,000 and Rs.2,000", 1000, 2000,
     "mid-range corporate gifts for employee rewards and client appreciation"),
    ("2000-3000", "Rs.2,000 - Rs.3,000", "Corporate Gifts Between Rs.2,000 and Rs.3,000", 2000, 3000,
     "premium mid-range corporate gifting — a popular budget for Diwali and year-end gifting"),
    ("3000-5000", "Rs.3,000 - Rs.5,000", "Corporate Gifts Between Rs.3,000 and Rs.5,000", 3000, 5000,
     "premium corporate gifts for senior employees, top clients and long-service awards"),
    ("5000-10000", "Rs.5,000 - Rs.10,000", "Corporate Gifts Between Rs.5,000 and Rs.10,000", 5000, 10000,
     "high-value corporate gifting for leadership gifts and marquee client relationships"),
    ("above-10000", "Above Rs.10,000", "Premium Corporate Gifts Above Rs.10,000", 10000, float("inf"),
     "luxury and premium electronics/appliance corporate gifting for top-tier recognition"),
]


def slugify(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def fmt_price(p):
    if not p:
        return "Price on request"
    return f"Rs.{p:,.0f}"


def img_url(img):
    if not img:
        return ""
    if img.startswith("http://") or img.startswith("https://"):
        return img
    return f"../../images/{img}"


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
{gtm_head}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/png" sizes="32x32" href="../../images/_brand/favicon_32.png">
<link rel="shortcut icon" href="../../images/_brand/favicon.ico">
<meta name="theme-color" content="{navy}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Corporate Gifting India">
<meta property="og:image" content="{PRIMARY_DOMAIN}/images/_brand/logo_512.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<script type="application/ld+json">{breadcrumb_ld}</script>
<script type="application/ld+json">{itemlist_ld}</script>
<script type="application/ld+json">{faq_ld}</script>
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
header.page-hero{{padding:18px 0 30px;}}
.eyebrow{{font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:var(--accent);}}
h1{{font-size:32px;line-height:1.2;margin:10px 0 12px;font-weight:800;color:var(--navy);}}
.page-sub{{color:var(--muted);font-size:15px;max-width:700px;line-height:1.6;margin:0 0 22px;}}
.stat-row{{display:flex;gap:24px;flex-wrap:wrap;margin-bottom:8px;}}
.stat{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 20px;}}
.stat b{{display:block;font-size:22px;color:var(--navy);font-family:'Fraunces',serif;}}
.stat span{{font-size:11.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;}}
.btn-primary{{display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,var(--accent),#c06a1a);color:#1b1200;padding:13px 24px;border-radius:28px;font-weight:800;font-size:14px;margin-top:18px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:16px;padding:10px 0 30px;}}
.pcard{{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;display:block;}}
.pcard-img{{aspect-ratio:1;background:#fff;display:flex;align-items:center;justify-content:center;padding:10px;}}
.pcard-img img{{max-height:100%;object-fit:contain;}}
.pcard-img .ph{{color:var(--muted);font-size:12px;}}
.pcard-brand{{font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:.4px;color:var(--accent);padding:10px 12px 0;}}
.pcard-name{{font-size:13px;font-weight:700;padding:4px 12px;line-height:1.35;min-height:2.6em;}}
.pcard-price{{font-size:14px;font-weight:800;color:var(--navy);padding:0 12px 12px;}}
.faq{{margin:30px 0;}}
.faq h2{{font-size:20px;color:var(--navy);}}
.faq-item{{border-bottom:1px solid var(--border);padding:14px 0;}}
.faq-item b{{display:block;font-size:14.5px;color:var(--navy);margin-bottom:6px;}}
.faq-item p{{margin:0;color:#374252;line-height:1.6;font-size:14px;}}
.browse-links{{display:flex;flex-wrap:wrap;gap:10px;padding:14px 0 40px;}}
.browse-links a{{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:7px 16px;font-size:12.5px;font-weight:700;color:var(--navy);}}
.browse-links a.active{{background:var(--navy);color:#fff;}}
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
  <a class="logo" href="../../">&nbsp;<b>Corporate</b> Gifting India</a>
  <a class="nav-cta" href="../../">Search Full Catalog</a>
</div></nav>
<div class="wrap">
  <div class="breadcrumb"><a href="../../">Home</a> &rsaquo; Budget &rsaquo; {label}</div>
  <header class="page-hero">
    <span class="eyebrow">SHOP BY BUDGET</span>
    <h1>{h1}</h1>
    <p class="page-sub">{intro}</p>
    <div class="stat-row">
      <div class="stat"><b>{count}</b><span>Products in this range</span></div>
      <div class="stat"><b>{brand_count}</b><span>Brands</span></div>
    </div>
    <a class="btn-primary" href="../../?mrpmin={mrp_lo}&amp;mrpmax={mrp_hi}">Search &amp; Filter Live Catalog &rarr;</a>
  </header>
  <div class="grid">
    {cards}
  </div>
  <div class="faq">
    <h2>Frequently asked questions</h2>
    {faq_html}
  </div>
  <h2 style="font-size:16px;color:var(--muted);margin:0 0 10px;font-family:inherit;">Other budget ranges</h2>
  <div class="browse-links">{other_links}</div>
</div>
<footer><div class="wrap">
  Nalanda Enterprises &middot; Chandigarh &middot; Authorised Corporate Gifting Partner &middot; <a href="../../">corporategiftingindia.co</a>
</div></footer>
<a class="float-wa" href="https://wa.me/919115513366?text=Hi%2C%20I%27d%20like%20to%20enquire%20about%20corporate%20gifting%20options." target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.29-1.39c1.44.79 3.06 1.2 4.71 1.2h.01c5.46 0 9.91-4.45 9.91-9.91C21.92 6.45 17.5 2 12.04 2zm5.8 14.02c-.24.68-1.4 1.3-1.93 1.38-.49.08-1.11.11-1.79-.11-.41-.13-.94-.31-1.62-.6-2.85-1.23-4.71-4.1-4.85-4.29-.14-.19-1.16-1.54-1.16-2.94 0-1.4.73-2.08 1-2.37.26-.28.57-.35.76-.35h.55c.18 0 .41-.07.64.49.24.57.81 1.98.88 2.12.07.14.11.31.02.5-.09.19-.14.31-.28.47-.14.16-.29.36-.42.48-.14.14-.28.28-.12.55.16.28.71 1.17 1.53 1.9 1.05.94 1.94 1.23 2.21 1.37.28.14.44.12.6-.07.16-.19.68-.79.86-1.06.18-.28.36-.23.6-.14.24.09 1.55.73 1.82.86.27.14.44.2.51.32.07.11.07.65-.17 1.33z"/></svg>
  <span class="float-wa-label">Chat with us</span>
</a>
</body>
</html>"""


def product_slug(r):
    base = slugify(f"{r['brand']} {r['product_name']}")[:70].strip("-")
    return f"products/{base}-{r['product_id'].lower()}/" if base else f"products/{r['product_id'].lower()}/"


def card(r):
    img = img_url(r.get("image_file"))
    name = html.escape(r["product_name"])
    brand = html.escape(r["brand"])
    price = fmt_price(r.get("mrp"))
    img_tag = (f'<img src="{img}" alt="{name} — {brand}" loading="lazy">' if img
               else '<div class="ph">No image</div>')
    return f'''<a class="pcard" href="../../{product_slug(r)}">
  <div class="pcard-img">{img_tag}</div>
  <div class="pcard-brand">{brand}</div>
  <div class="pcard-name">{name}</div>
  <div class="pcard-price">{price}</div>
</a>'''


def build():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    site_meta = json.load(open(os.path.join(OUT_DIR, "site_meta.json")))
    total = f"{site_meta['total']:,}"

    eligible = [r for r in recs if r.get("mrp") and r.get("category") != "Gift Cards"]

    by_band = defaultdict(list)
    for r in eligible:
        mrp = r["mrp"]
        for slug, label, h1, lo, hi, desc in BANDS:
            if lo <= mrp < hi:
                by_band[slug].append(r)
                break

    written = []
    for slug, label, h1, lo, hi, desc in BANDS:
        items_all = sorted(by_band.get(slug, []), key=lambda r: -(r.get("mrp") or 0))
        if not items_all:
            continue
        items = items_all[:PAGE_CAP]
        count = len(items_all)
        brands_here = sorted(set(r["brand"] for r in items_all))
        cats_here = sorted(set(r["category"] for r in items_all if r.get("category")))[:6]

        title = f"{h1} | 2026 Guide — Corporate Gifting India"
        description = (f"{count} corporate gifting products priced {label} across {len(brands_here)} brands — "
                        f"{desc}. Verified MRP, bulk pricing on request, supplied by Nalanda Enterprises.")[:157]
        canonical = f"{PRIMARY_DOMAIN}/budget/{slug}/"
        intro = (f"{count} corporate gift options priced {label}, across {len(brands_here)} authorised brands "
                 f"including {', '.join(brands_here[:6])}{' and more' if len(brands_here) > 6 else ''} — "
                 f"ideal for {desc}. Every product below has a verified MRP; message us for bulk/dealer pricing.")

        cards = "\n".join(card(r) for r in items)

        faqs = [
            (f"What corporate gifts are available {label.lower()}?",
             f"We stock {count} products in this range across categories like {', '.join(cats_here) or 'electronics, appliances and lifestyle'}, "
             f"from brands including {', '.join(brands_here[:5])}. Browse the list above or use the live catalog filter for the full range."),
            ("Do you offer bulk/dealer pricing below the listed MRP?",
             "Yes — the prices shown are MRP. For bulk corporate orders (50+ units), dealer stock or festive gifting "
             "programs, WhatsApp or email us with the quantity and we'll share dealer pricing and lead time."),
            ("What is the minimum order quantity for corporate gifting?",
             "Minimum order quantities vary by product and brand. Most corporate gifting orders start from 25-50 units; "
             "contact us with your requirement and we'll confirm MOQ, customisation options and delivery timelines."),
        ]
        faq_html = "\n".join(
            f'<div class="faq-item"><b>{html.escape(q)}</b><p>{html.escape(a)}</p></div>' for q, a in faqs
        )
        faq_ld = json.dumps({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs
            ]
        }, ensure_ascii=False)

        breadcrumb_ld = json.dumps({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{PRIMARY_DOMAIN}/"},
                {"@type": "ListItem", "position": 2, "name": "Budget", "item": f"{PRIMARY_DOMAIN}/budget/"},
                {"@type": "ListItem", "position": 3, "name": label, "item": canonical},
            ]
        }, ensure_ascii=False)
        itemlist_ld = json.dumps({
            "@context": "https://schema.org", "@type": "ItemList",
            "itemListElement": [
                {"@type": "ListItem", "position": i, "item": {
                    "@type": "Product", "name": r["product_name"],
                    "brand": {"@type": "Brand", "name": r["brand"]},
                    "offers": {"@type": "Offer", "price": r["mrp"], "priceCurrency": "INR",
                               "url": f"{PRIMARY_DOMAIN}/{product_slug(r)}"},
                }} for i, r in enumerate(items, 1)
            ]
        }, ensure_ascii=False)

        other_links = "\n".join(
            f'<a href="../{s}/"{" class=\"active\"" if s == slug else ""}>{lbl}</a>'
            for s, lbl, *_ in BANDS if by_band.get(s)
        )

        page = PAGE_TEMPLATE.format(
            gtm_head=GTM_HEAD, gtm_body=GTM_BODY, title=html.escape(title),
            description=html.escape(description), canonical=canonical, navy=NAVY,
            PRIMARY_DOMAIN=PRIMARY_DOMAIN, breadcrumb_ld=breadcrumb_ld, itemlist_ld=itemlist_ld,
            faq_ld=faq_ld, label=html.escape(label), h1=html.escape(h1), intro=intro,
            count=count, brand_count=len(brands_here), slug=slug, cards=cards,
            faq_html=faq_html, other_links=other_links,
            mrp_lo=int(lo), mrp_hi=(int(hi) if hi != float("inf") else 99999999),
        )
        dir_path = os.path.join(SITE_DIR, "budget", slug)
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, "index.html"), "w") as fh:
            fh.write(page)
        written.append(f"/budget/{slug}/")

    with open(os.path.join(OUT_DIR, "budget_page_urls.json"), "w") as fh:
        json.dump(written, fh)
    print(f"Wrote {len(written)} budget landing pages")


if __name__ == "__main__":
    build()
