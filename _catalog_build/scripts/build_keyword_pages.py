# -*- coding: utf-8 -*-
"""
Generates keyword-cluster landing pages under
_catalog_build/site/corporate-gifts/<slug>/index.html plus a hub page at
/corporate-gifts/.

Why: buyers search with thousands of distinct intents — "bulk earbuds for
corporate gifting", "diwali gifts for employees", "corporate gifts in
mumbai", "wholesale power bank", "gifts for doctors" — and the site only had
brand / category / budget pages. keyword_research.json (≈1,000 researched
Google search terms) groups those intents into clusters; each cluster gets
one page with unique copy (keyword_content.json), real matching catalog
products linking into /products/, an FAQ (FAQPage schema), and cross-links
to sibling clusters. The hub lists every page plus the full searched-term
list so crawlers and AI answer engines (GEO) can map each query to a page.

Run AFTER build_product_pages.py (uses the same product slug scheme) and
BEFORE finalize_site_assets.py (sitemap / llms.txt pick up
keyword_page_urls.json).
"""
import json, os, re, html
from collections import defaultdict

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
SITE_DIR = os.path.join(BASE, "_catalog_build", "site")
PRIMARY_DOMAIN = "https://corporategiftingindia.co"
SECTION = "corporate-gifts"
PAGE_CAP = 48
WA = "https://wa.me/919115513366?text="

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

TYPE_LABEL = {
    "occasion": "Occasion", "audience": "Who it's for", "product-bulk": "Bulk products",
    "brand-bulk": "Brands in bulk", "budget": "By budget", "general": "Corporate gifting",
    "city": "Cities we deliver to", "gift-cards": "Gift cards",
}
TYPE_ORDER = ["general", "audience", "occasion", "product-bulk", "brand-bulk", "budget", "gift-cards", "city"]

# Search-term -> catalog vocabulary. Catalog categories are vendor-supplied and
# inconsistent ("TWS", "Earbuds", "Personal Audio"), so product matching runs
# over name + category + sub-category + brand with these expansions.
SYNONYMS = {
    "earbuds": ["earbud", "tws", "airdopes", "buds", "true wireless"],
    "headphones": ["headphone", "wireless hp", "rockerz", "over-ear", "on-ear"],
    "neckband": ["neckband", "wireless ep"],
    "speaker": ["speaker", "bt speaker", "stone", "soundbar", "sound bar"],
    "smartwatch": ["smartwatch", "smart watch", "wearables", "watch"],
    "power bank": ["power bank", "powerbank", "mah"],
    "charger": ["charger", "wall charger", "adapter", "gan"],
    "cable": ["cable", "cables"],
    "bottle": ["bottle", "flask", "puro", "thermo"],
    "lunch box": ["lunch", "tiffin", "meal mate"],
    "backpack": ["backpack", "laptop bag", "everyday carry"],
    "luggage": ["trolley", "suitcase", "luggage", "duffle", "cabin", "overnighter", "over nighter"],
    "dinner set": ["dinner set", "dinnerware", "plate", "bowl", "tea set", "coffee set", "mug", "glass"],
    "kitchen appliance": ["mixer", "grinder", "kettle", "toaster", "sandwich", "air fryer", "induction",
                          "blender", "juicer", "cooker", "otg", "rice cooker", "coffee maker"],
    "cookware": ["cookware", "kadai", "tawa", "pan", "pressure cooker", "casserole"],
    "fan": ["fan"],
    "iron": ["iron", "steamer"],
    "trimmer": ["trimmer", "shaver", "hair dryer", "straightener", "grooming"],
    "mobile": ["smartphone", "mobile", "5g"],
    "tablet": ["tablet", "tab "],
    "keyboard mouse": ["keyboard", "mouse", "combo"],
    "gift card": ["gift card", "voucher", "e-gift"],
    "towel": ["towel", "bath range", "bedsheet", "blanket", "comforter", "dohar"],
    "yoga mat": ["yoga", "fitness", "gym"],
    "microphone": ["microphone", "mic "],
    "watch": ["watch"],
    "air purifier": ["air purifier"],
    "desk": ["desk", "organizer", "organiser", "stand", "holder", "wireless charger"],
}


def slugify(s):
    s = (s or "").lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def fmt_price(p):
    return f"Rs.{p:,.0f}" if p else "Price on request"


def img_url(img):
    if not img:
        return ""
    if img.startswith("http://") or img.startswith("https://"):
        return img
    return f"../../images/{img}"


def product_slug(r):
    base = slugify(f"{r['brand']} {r['product_name']}")[:70].strip("-")
    return f"products/{base}-{r['product_id'].lower()}/" if base else f"products/{r['product_id'].lower()}/"


def esc(s):
    return html.escape(s or "", quote=True)


def haystack(r):
    return " ".join([r.get("product_name", ""), r.get("category", ""), r.get("sub_category", ""),
                     r.get("brand", "")]).lower()


def expand_terms(terms):
    out = set()
    for t in terms or []:
        t = t.lower().strip()
        if not t:
            continue
        out.add(t)
        for key, syns in SYNONYMS.items():
            if t == key or t in syns or key in t:
                out.update(syns)
                out.add(key)
    return sorted(out)


def match_products(recs, pm, has_page):
    """Return catalog products for a cluster's product_match hints, brand-diverse."""
    pm = pm or {}
    cats = [c.lower() for c in pm.get("categories") or []]
    brands = {b.lower() for b in pm.get("brands") or []}
    terms = expand_terms(pm.get("keywords_in_product_name"))
    max_price = pm.get("max_price")
    min_price = pm.get("min_price")
    out = []
    for r in recs:
        if r["product_id"] not in has_page:
            continue
        if r.get("category") == "Gift Cards" and "gift card" not in terms:
            continue
        hs = haystack(r)
        if brands and r["brand"].lower() not in brands:
            continue
        hit = False
        if terms and any(t in hs for t in terms):
            hit = True
        if cats and any(c in (r.get("category") or "").lower() or c in (r.get("sub_category") or "").lower()
                        for c in cats):
            hit = True
        if not terms and not cats and brands:
            hit = True
        if not hit:
            continue
        mrp = r.get("mrp") or 0
        if max_price and (not mrp or mrp > max_price):
            continue
        if min_price and mrp < min_price:
            continue
        out.append(r)
    # Prefer products with images and prices; round-robin across brands for variety.
    out.sort(key=lambda r: (not r.get("image_file"), not r.get("mrp"), -(r.get("mrp") or 0)))
    by_brand = defaultdict(list)
    order = []
    for r in out:
        if r["brand"] not in by_brand:
            order.append(r["brand"])
        by_brand[r["brand"]].append(r)
    picked = []
    while len(picked) < PAGE_CAP and any(by_brand.values()):
        for b in order:
            if by_brand[b]:
                picked.append(by_brand[b].pop(0))
                if len(picked) >= PAGE_CAP:
                    break
    return picked, len(out)


CSS = """
:root{--navy:#0f2a4a;--navy-dark:#08172b;--accent:#d98b2b;--accent-light:#f0b866;--bg:#f7f5f0;--card:#ffffff;--text:#1c2733;--muted:#6b7785;--border:#e6e2d8;}
*{box-sizing:border-box;}
body{margin:0;font-family:'Manrope',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text);}
h1,h2,h3,.logo{font-family:'Fraunces',Georgia,serif;}
a{color:inherit;text-decoration:none;}
img{max-width:100%;}
.wrap{max-width:1280px;margin:0 auto;padding:0 24px;}
nav.topnav{background:var(--navy-dark);padding:16px 0;}
nav.topnav .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;}
.logo{color:#fff;font-size:17px;font-weight:800;}
.logo b{color:var(--accent-light);}
.nav-links{display:flex;gap:18px;align-items:center;}
.nav-links a{color:#cfd8e3;font-size:13px;font-weight:700;}
.nav-cta{background:linear-gradient(135deg,var(--accent),#c06a1a);color:#1b1200 !important;padding:9px 18px;border-radius:24px;font-size:13px;font-weight:800;}
.breadcrumb{font-size:12.5px;color:var(--muted);padding:18px 0 0;}
.breadcrumb a{color:var(--accent);font-weight:700;}
header.page-hero{padding:18px 0 26px;}
.eyebrow{font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:var(--accent);}
h1{font-size:32px;line-height:1.2;margin:10px 0 12px;font-weight:800;color:var(--navy);}
.page-sub{color:#374252;font-size:15.5px;max-width:820px;line-height:1.7;margin:0 0 22px;}
.stat-row{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:8px;}
.stat{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 20px;}
.stat b{display:block;font-size:22px;color:var(--navy);font-family:'Fraunces',serif;}
.stat span{font-size:11.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;}
.cta-row{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px;}
.btn-primary{display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,var(--accent),#c06a1a);color:#1b1200;padding:13px 24px;border-radius:28px;font-weight:800;font-size:14px;}
.btn-wa{display:inline-flex;align-items:center;gap:8px;background:#25D366;color:#fff;padding:13px 24px;border-radius:28px;font-weight:800;font-size:14px;}
.content{max-width:860px;}
.content h2{font-size:22px;color:var(--navy);margin:30px 0 10px;}
.content p,.content li{color:#374252;line-height:1.75;font-size:15px;}
h2.sec{font-size:22px;color:var(--navy);margin:34px 0 6px;}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:16px;padding:10px 0 20px;}
.pcard{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;display:block;}
.pcard-img{aspect-ratio:1;background:#fff;display:flex;align-items:center;justify-content:center;padding:10px;}
.pcard-img img{max-height:100%;object-fit:contain;}
.pcard-img .ph{color:var(--muted);font-size:12px;}
.pcard-brand{font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:.4px;color:var(--accent);padding:10px 12px 0;}
.pcard-name{font-size:13px;font-weight:700;padding:4px 12px;line-height:1.35;min-height:2.6em;}
.pcard-price{font-size:14px;font-weight:800;color:var(--navy);padding:0 12px 12px;}
.faq{margin:30px 0;max-width:860px;}
.faq h2{font-size:22px;color:var(--navy);}
.faq-item{border-bottom:1px solid var(--border);padding:14px 0;}
.faq-item b{display:block;font-size:14.5px;color:var(--navy);margin-bottom:6px;}
.faq-item p{margin:0;color:#374252;line-height:1.6;font-size:14px;}
.chips{display:flex;flex-wrap:wrap;gap:8px;padding:8px 0 20px;}
.chips span,.chips a{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:6px 14px;font-size:12.5px;font-weight:600;color:#374252;}
.chips a{color:var(--navy);font-weight:700;}
.hub-group{margin:10px 0 26px;}
.hub-group h2{font-size:20px;color:var(--navy);margin:0 0 10px;}
.hub-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;}
.hub-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px;display:block;}
.hub-card b{display:block;color:var(--navy);font-size:14.5px;margin-bottom:4px;}
.hub-card span{color:var(--muted);font-size:12.5px;line-height:1.5;}
.kw-list{columns:4 220px;column-gap:24px;font-size:13px;color:#374252;line-height:1.9;padding:0;margin:0 0 30px;list-style:none;}
.kw-list a{color:#374252;}
footer{padding:26px 0;border-top:1px solid var(--border);color:var(--muted);font-size:12.5px;line-height:1.7;}
footer a{color:var(--navy);font-weight:700;}
.float-wa{position:fixed;right:20px;bottom:86px;z-index:80;display:flex;align-items:center;gap:9px;background:#25D366;color:#fff;padding:13px;border-radius:50px;box-shadow:0 8px 24px rgba(37,211,102,.45);text-decoration:none;}
.float-wa svg{width:24px;height:24px;flex:none;}
@media (max-width:640px){h1{font-size:26px;}.wrap{padding:0 16px;}.nav-links a:not(.nav-cta){display:none;}.float-wa{right:14px;bottom:80px;padding:12px;}}
"""

WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.29-1.39c1.44.79 3.06 1.2 4.71 1.2h.01c5.46 0 9.91-4.45 9.91-9.91C21.92 6.45 17.5 2 12.04 2zm5.8 14.02c-.24.68-1.4 1.3-1.93 1.38-.49.08-1.11.11-1.79-.11-.41-.13-.94-.31-1.62-.6-2.85-1.23-4.71-4.1-4.85-4.29-.14-.19-1.16-1.54-1.16-2.94 0-1.4.73-2.08 1-2.37.26-.28.57-.35.76-.35h.55c.18 0 .41-.07.64.49.24.57.81 1.98.88 2.12.07.14.11.31.02.5-.09.19-.14.31-.28.47-.14.16-.29.36-.42.48-.14.14-.28.28-.12.55.16.28.71 1.17 1.53 1.9 1.05.94 1.94 1.23 2.21 1.37.28.14.44.12.6-.07.16-.19.68-.79.86-1.06.18-.28.36-.23.6-.14.24.09 1.55.73 1.82.86.27.14.44.2.51.32.07.11.07.65-.17 1.33z"/></svg>'


def head(title, description, canonical, rel, ld_blocks, keywords=""):
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>' for b in ld_blocks)
    kw = f'\n<meta name="keywords" content="{esc(keywords)}">' if keywords else ""
    return f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
{GTM_HEAD}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">{kw}
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/png" sizes="32x32" href="{rel}images/_brand/favicon_32.png">
<link rel="shortcut icon" href="{rel}images/_brand/favicon.ico">
<meta name="theme-color" content="#0f2a4a">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="geo.region" content="IN-CH">
<meta name="geo.placename" content="Chandigarh">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="Corporate Gifting India">
<meta property="og:image" content="{PRIMARY_DOMAIN}/images/_brand/logo_512.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
{ld}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,800;1,9..144,600&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{GTM_BODY}
<nav class="topnav"><div class="wrap">
  <a class="logo" href="{rel}">&nbsp;<b>Corporate</b> Gifting India</a>
  <div class="nav-links">
    <a href="{rel}{SECTION}/">Gifting Ideas</a>
    <a href="{rel}budget/2000-3000/">By Budget</a>
    <a href="{rel}services/">Services</a>
    <a class="nav-cta" href="{rel}">Search Full Catalog</a>
  </div>
</div></nav>
"""


def foot(rel, wa_text):
    return f"""<footer><div class="wrap">
  <b>Nalanda Enterprises</b> &middot; SCF-4, Sector 19D, Chandigarh &middot; Authorised corporate gifting partner since 2014 &middot; Pan-India bulk delivery<br>
  Call / WhatsApp <a href="tel:+919115513366">+91-9115513366</a> &middot; <a href="mailto:info@nalandaenterprises.com">info@nalandaenterprises.com</a> &middot;
  <a href="{rel}{SECTION}/">All gifting ideas</a> &middot; <a href="{rel}about/">About</a> &middot; <a href="{rel}contact/">Contact</a> &middot; <a href="{rel}">corporategiftingindia.co</a>
</div></footer>
<a class="float-wa" href="{WA}{wa_text}" target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">{WA_SVG}</a>
</body>
</html>"""


def card(r, rel):
    img = img_url(r.get("image_file"))
    if img and not img.startswith("http"):
        img = img.replace("../../", rel)
    name, brand = esc(r["product_name"]), esc(r["brand"])
    img_tag = (f'<img src="{img}" alt="{name} — {brand} bulk corporate gift" loading="lazy">' if img
               else '<div class="ph">Image on request</div>')
    return f'''<a class="pcard" href="{rel}{product_slug(r)}">
  <div class="pcard-img">{img_tag}</div>
  <div class="pcard-brand">{brand}</div>
  <div class="pcard-name">{name}</div>
  <div class="pcard-price">{fmt_price(r.get("mrp"))}</div>
</a>'''


def org_ld():
    return {
        "@context": "https://schema.org", "@type": "LocalBusiness", "@id": f"{PRIMARY_DOMAIN}/#business",
        "name": "Nalanda Enterprises — Corporate Gifting India", "url": f"{PRIMARY_DOMAIN}/",
        "telephone": "+91-9115513366", "email": "info@nalandaenterprises.com", "foundingDate": "2014",
        "image": f"{PRIMARY_DOMAIN}/images/_brand/logo_512.png",
        "address": {"@type": "PostalAddress", "streetAddress": "SCF-4, Sector 19D",
                    "addressLocality": "Chandigarh", "addressRegion": "Chandigarh", "addressCountry": "IN"},
        "areaServed": {"@type": "Country", "name": "India"},
    }


def build():
    research = json.load(open(os.path.join(OUT_DIR, "keyword_research.json")))
    content_path = os.path.join(OUT_DIR, "keyword_content.json")
    content = json.load(open(content_path)) if os.path.exists(content_path) else {}
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    has_page = {u.rstrip("/").rsplit("-", 2)[-2].upper() + "-" + u.rstrip("/").rsplit("-", 1)[-1]
                for u in json.load(open(os.path.join(OUT_DIR, "product_page_urls.json")))}

    clusters = research["clusters"]
    kw_by_cluster = defaultdict(list)
    for k in research["keywords"]:
        kw_by_cluster[k["cluster"]].append(k)
    pop_rank = {"high": 0, "medium": 1, "long-tail": 2}
    for s in kw_by_cluster:
        kw_by_cluster[s].sort(key=lambda k: (pop_rank.get(k.get("est_popularity"), 3), k["keyword"]))

    by_type = defaultdict(list)
    for c in clusters:
        by_type[c.get("type", "general")].append(c)

    written = []
    rel = "../../"
    for c in clusters:
        slug = slugify(c["slug"])
        cc = content.get(c["slug"], {})
        kws = [k["keyword"] for k in kw_by_cluster.get(c["slug"], [])]
        products, match_count = match_products(recs, c.get("product_match"), has_page)
        brands_here = sorted({r["brand"] for r in products})
        canonical = f"{PRIMARY_DOMAIN}/{SECTION}/{slug}/"
        title = c.get("title") or c["h1"]
        if "corporate gifting india" not in title.lower() and len(title) < 42:
            title = f"{title} | Corporate Gifting India"
        description = (cc.get("meta_description") or
                       f"{c['h1']} — {match_count or 'hundreds of'} options from {len(brands_here) or 50}+ authorised brands, "
                       f"bulk pricing, branding & pan-India delivery by Nalanda Enterprises.")[:158]
        intro = cc.get("intro") or (
            f"Looking for {c['primary_keyword']}? Nalanda Enterprises has supplied corporate gifts in bulk to 500+ "
            f"companies across India since 2014. Browse genuine, brand-authorised products below with verified MRP, "
            f"then WhatsApp us your quantity and budget for a bulk quote.")

        sections_html = "\n".join(
            f"<h2>{esc(s['h2'])}</h2>\n" + "\n".join(f"<p>{esc(p)}</p>" for p in re.split(r"\n\s*\n", s["body"]) if p.strip())
            for s in cc.get("sections", []))
        faqs = cc.get("faqs") or [
            {"q": f"Do you supply {c['primary_keyword']} in bulk?",
             "a": "Yes. We supply corporate orders from 10 units upwards with GST invoices, optional logo branding and gift packaging, delivered anywhere in India."},
            {"q": "How fast can you deliver a bulk corporate gifting order?",
             "a": "In-stock products usually dispatch within 3-7 working days; branded or customised orders typically need 7-15 days depending on quantity."},
            {"q": "Can I get prices below MRP for bulk orders?",
             "a": "Yes. Listed prices are MRP; bulk and dealer pricing is shared on request based on quantity. WhatsApp +91-9115513366 for a quote."},
        ]
        faq_html = "\n".join(f'<div class="faq-item"><b>{esc(f["q"])}</b><p>{esc(f["a"])}</p></div>' for f in faqs)

        siblings = [s for s in by_type[c.get("type", "general")] if s["slug"] != c["slug"]][:12]
        related = siblings + [s for t in TYPE_ORDER if t != c.get("type") for s in by_type[t][:2]][:8]
        related_html = "".join(f'<a href="../{slugify(s["slug"])}/">{esc(s["h1"])}</a>' for s in related)
        kw_html = "".join(f"<span>{esc(k)}</span>" for k in kws)
        cards = "\n".join(card(r, rel) for r in products)
        wa_text = re.sub(r"\s", "%20", f"Hi, I'd like a bulk quote for {c['primary_keyword']}.").replace("'", "%27")

        ld = [
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{PRIMARY_DOMAIN}/"},
                {"@type": "ListItem", "position": 2, "name": "Corporate Gifts", "item": f"{PRIMARY_DOMAIN}/{SECTION}/"},
                {"@type": "ListItem", "position": 3, "name": c["h1"], "item": canonical}]},
            {"@context": "https://schema.org", "@type": "CollectionPage", "name": c["h1"], "url": canonical,
             "description": description, "about": c["primary_keyword"], "keywords": ", ".join(kws[:25]),
             "provider": {"@id": f"{PRIMARY_DOMAIN}/#business"}, "inLanguage": "en-IN"},
            {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                for f in faqs]},
            org_ld(),
        ]
        if products:
            ld.append({"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i, "url": f"{PRIMARY_DOMAIN}/{product_slug(r)}", "name": r["product_name"]}
                for i, r in enumerate(products[:24], 1)]})
        if c.get("type") == "city":
            ld.append({"@context": "https://schema.org", "@type": "Service", "serviceType": "Corporate gifting",
                       "name": c["h1"], "provider": {"@id": f"{PRIMARY_DOMAIN}/#business"},
                       "areaServed": {"@type": "City", "name": c.get("city") or c["h1"].split(" in ")[-1]}})

        stats = ""
        if products:
            stats = (f'<div class="stat-row"><div class="stat"><b>{match_count:,}</b><span>Matching products</span></div>'
                     f'<div class="stat"><b>{len({r["brand"] for r in products})}</b><span>Brands shown</span></div>'
                     f'<div class="stat"><b>500+</b><span>Corporate clients</span></div>'
                     f'<div class="stat"><b>Pan-India</b><span>Delivery</span></div></div>')
        body = f"""<div class="wrap">
  <div class="breadcrumb"><a href="{rel}">Home</a> &rsaquo; <a href="../">Corporate Gifts</a> &rsaquo; {esc(c['h1'])}</div>
  <header class="page-hero">
    <span class="eyebrow">{esc(TYPE_LABEL.get(c.get('type'), 'Corporate gifting'))}</span>
    <h1>{esc(c['h1'])}</h1>
    <p class="page-sub">{esc(intro)}</p>
    {stats}
    <div class="cta-row">
      <a class="btn-wa" href="{WA}{wa_text}" target="_blank" rel="noopener">Get a bulk quote on WhatsApp</a>
      <a class="btn-primary" href="{rel}#catalog">Search all 12,000+ products &rarr;</a>
    </div>
  </header>
  {f'<h2 class="sec">{esc(c["h1"])} — top picks</h2><div class="grid">{cards}</div>' if products else ''}
  <div class="content">{sections_html}</div>
  <div class="faq"><h2>Frequently asked questions</h2>{faq_html}</div>
  <h2 class="sec">People also search for</h2>
  <div class="chips">{kw_html}</div>
  <h2 class="sec">Related gifting pages</h2>
  <div class="chips">{related_html}</div>
</div>"""
        page = head(title, description, canonical, rel, ld, ", ".join(kws[:15])) + body + foot(rel, wa_text)
        d = os.path.join(SITE_DIR, SECTION, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w") as fh:
            fh.write(page)
        written.append(f"/{SECTION}/{slug}/")

    # ---- hub page -------------------------------------------------------
    rel = "../"
    canonical = f"{PRIMARY_DOMAIN}/{SECTION}/"
    groups = []
    for t in TYPE_ORDER:
        if not by_type.get(t):
            continue
        cards_h = "".join(
            f'<a class="hub-card" href="{slugify(c["slug"])}/"><b>{esc(c["h1"])}</b>'
            f'<span>{esc(", ".join(k["keyword"] for k in kw_by_cluster.get(c["slug"], [])[:3]))}</span></a>'
            for c in by_type[t])
        groups.append(f'<div class="hub-group"><h2>{esc(TYPE_LABEL[t])}</h2><div class="hub-grid">{cards_h}</div></div>')
    slug_of = {k["keyword"]: slugify(k["cluster"]) for k in research["keywords"]}
    all_kws = sorted(slug_of)
    kw_list = "".join(f'<li><a href="{slug_of[k]}/">{esc(k)}</a></li>' for k in all_kws)
    hub_title = "Corporate Gifts India — Bulk, Employee & Client Gifting Ideas"
    hub_desc = (f"{len(clusters)} corporate gifting guides: employee gifts, client gifts, Diwali gifts, bulk earbuds, "
                "smartwatches, power banks, bottles & more — pan-India bulk delivery by Nalanda Enterprises.")[:158]
    ld = [
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{PRIMARY_DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Corporate Gifts", "item": canonical}]},
        {"@context": "https://schema.org", "@type": "CollectionPage", "name": hub_title, "url": canonical,
         "description": hub_desc, "inLanguage": "en-IN", "provider": {"@id": f"{PRIMARY_DOMAIN}/#business"},
         "hasPart": [{"@type": "WebPage", "name": c["h1"], "url": f"{PRIMARY_DOMAIN}/{SECTION}/{slugify(c['slug'])}/"}
                     for c in clusters]},
        org_ld(),
    ]
    body = f"""<div class="wrap">
  <div class="breadcrumb"><a href="{rel}">Home</a> &rsaquo; Corporate Gifts</div>
  <header class="page-hero">
    <span class="eyebrow">Gifting ideas &amp; bulk buying guides</span>
    <h1>Corporate Gifts, Bulk &amp; Wholesale Gifting — Every Occasion, Budget &amp; City</h1>
    <p class="page-sub">Whether you need Diwali gifts for 500 employees, premium client gifts, dealer incentives,
    joining kits or simply want to buy earbuds, smartwatches, bottles or appliances in bulk — pick your need below.
    Nalanda Enterprises (Chandigarh, since 2014) supplies 12,000+ genuine products from 54 authorised brands with
    GST invoicing, logo branding and pan-India delivery.</p>
    <div class="cta-row"><a class="btn-wa" href="{WA}Hi%2C%20I%27d%20like%20a%20corporate%20gifting%20quote." target="_blank" rel="noopener">Get a bulk quote on WhatsApp</a>
    <a class="btn-primary" href="{rel}#catalog">Search all products &rarr;</a></div>
  </header>
  {''.join(groups)}
  <h2 class="sec">Popular corporate gifting searches ({len(all_kws):,})</h2>
  <ul class="kw-list">{kw_list}</ul>
</div>"""
    page = head(hub_title, hub_desc, canonical, rel, ld) + body + foot(rel, "Hi%2C%20I%27d%20like%20a%20corporate%20gifting%20quote.")
    with open(os.path.join(SITE_DIR, SECTION, "index.html"), "w") as fh:
        fh.write(page)
    written.insert(0, f"/{SECTION}/")

    with open(os.path.join(OUT_DIR, "keyword_page_urls.json"), "w") as fh:
        json.dump(written, fh, indent=1)
    print(f"Wrote {len(written)} keyword landing pages ({len(research['keywords'])} keywords)")


if __name__ == "__main__":
    build()
