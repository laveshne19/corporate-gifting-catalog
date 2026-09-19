# -*- coding: utf-8 -*-
"""
Generates the three static company pages the SPA homepage doesn't have as
standalone crawlable URLs: /about/, /services/, /contact/. All copy here is
built only from facts already established on the live homepage (see
catalog_template.html's #why-us/#contact sections and hero stats) — no
fabricated history, team bios, or claims.

Run after build_html.py (needs _catalog_build/output/site_meta.json) and
before finalize_site_assets.py (sitemap includes these via seo_page_urls.json,
which this script appends to).
"""
import json, os

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

PAGE_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
{gtm_head}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="icon" type="image/png" sizes="32x32" href="../images/_brand/favicon_32.png">
<link rel="shortcut icon" href="../images/_brand/favicon.ico">
<meta name="theme-color" content="{navy}">
<meta name="keywords" content="corporate gifting for pharma companies, FMCG corporate gifts, corporate gifting for IT companies, corporate gifting company Chandigarh, pharma field force gifting, FMCG trade gifting, corporate gifting vendor India, bulk employee gifts India, 12 years corporate gifting">
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
<script type="application/ld+json">{jsonld}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,800;1,9..144,600&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{--navy:#0f2a4a;--navy-dark:#08172b;--accent:#d98b2b;--accent-light:#f0b866;--bg:#f7f5f0;--card:#ffffff;--text:#1c2733;--muted:#6b7785;--border:#e6e2d8;}}
*{{box-sizing:border-box;}}
body{{margin:0;font-family:'Manrope',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text);}}
h1,h2,.logo{{font-family:'Fraunces',Georgia,serif;}}
a{{color:inherit;text-decoration:none;}}
.wrap{{max-width:1000px;margin:0 auto;padding:0 24px;}}
nav.topnav{{background:var(--navy-dark);padding:16px 0;}}
nav.topnav .wrap{{display:flex;align-items:center;justify-content:space-between;max-width:1280px;}}
.logo{{color:#fff;font-size:17px;font-weight:800;}}
.logo b{{color:var(--accent-light);}}
.navlinks{{display:flex;gap:22px;font-size:13px;font-weight:700;color:#c7d3e0;}}
.navlinks a:hover{{color:#fff;}}
.nav-cta{{background:linear-gradient(135deg,var(--accent),#c06a1a);color:#1b1200;padding:9px 18px;border-radius:24px;font-size:13px;font-weight:800;}}
.breadcrumb{{font-size:12.5px;color:var(--muted);padding:18px 0 0;}}
.breadcrumb a{{color:var(--accent);font-weight:700;}}
header.page-hero{{padding:18px 0 30px;}}
.eyebrow{{font-size:11px;font-weight:800;letter-spacing:1px;text-transform:uppercase;color:var(--accent);}}
h1{{font-size:36px;line-height:1.2;margin:10px 0 14px;font-weight:800;color:var(--navy);}}
.page-sub{{color:var(--muted);font-size:16px;max-width:720px;line-height:1.65;margin:0 0 8px;}}
.stat-row{{display:flex;gap:20px;flex-wrap:wrap;margin:26px 0 6px;}}
.stat{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 22px;}}
.stat b{{display:block;font-size:24px;color:var(--navy);font-family:'Fraunces',serif;}}
.stat span{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;}}
section.block{{padding:34px 0;}}
section.block h2{{font-size:24px;color:var(--navy);margin:0 0 14px;}}
section.block p{{line-height:1.75;font-size:15px;color:var(--text);max-width:780px;}}
.card-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:18px;margin-top:18px;}}
.icard{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px;}}
.icard .ic{{font-size:26px;margin-bottom:10px;}}
.icard h3{{font-size:15.5px;margin:0 0 6px;color:var(--navy);}}
.icard p{{font-size:13.5px;color:var(--muted);line-height:1.55;margin:0;}}
.btn-primary{{display:inline-flex;align-items:center;gap:8px;background:linear-gradient(135deg,var(--accent),#c06a1a);color:#1b1200;padding:14px 26px;border-radius:28px;font-weight:800;font-size:14.5px;margin-top:10px;}}
.contact-grid{{display:grid;grid-template-columns:1.1fr .9fr;gap:32px;margin-top:10px;}}
@media (max-width:720px){{.contact-grid{{grid-template-columns:1fr;}} .navlinks{{display:none;}}}}
.contact-list .row{{font-size:15px;padding:10px 0;border-bottom:1px solid var(--border);}}
.contact-box{{background:var(--navy-dark);color:#fff;border-radius:16px;padding:28px;}}
.contact-box h3{{margin:0 0 8px;font-size:18px;}}
.contact-box p{{color:#c7d3e0;font-size:13.5px;margin:0 0 18px;}}
.contact-box a{{display:block;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);border-radius:10px;padding:12px 16px;margin-bottom:10px;font-weight:700;font-size:14px;}}
.contact-box a:hover{{background:rgba(255,255,255,.14);}}
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
  <a class="logo" href="../"><b>Corporate</b> Gifting India</a>
  <div class="navlinks">
    <a href="../about/">About</a>
    <a href="../services/">Services</a>
    <a href="../#catalog">Catalog</a>
    <a href="../contact/">Contact</a>
  </div>
  <a class="nav-cta" href="../contact/">Request a Quote</a>
</div></nav>
<div class="wrap">
  <div class="breadcrumb"><a href="../">Home</a> &rsaquo; {breadcrumb_label}</div>
  <header class="page-hero">
    <span class="eyebrow">{eyebrow}</span>
    <h1>{h1}</h1>
    <p class="page-sub">{intro}</p>
    {stats_html}
  </header>
  {body_html}
</div>
<footer><div class="wrap">
  Nalanda Enterprises &middot; SCF-4, Sector 19D, Chandigarh &middot; <a href="../">corporategiftingindia.co</a>
</div></footer>
<a class="float-wa" href="https://wa.me/919115513366?text=Hi%2C%20I%27d%20like%20to%20enquire%20about%20corporate%20gifting%20options." target="_blank" rel="noopener" aria-label="Chat with us on WhatsApp">
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.29-1.39c1.44.79 3.06 1.2 4.71 1.2h.01c5.46 0 9.91-4.45 9.91-9.91C21.92 6.45 17.5 2 12.04 2zm5.8 14.02c-.24.68-1.4 1.3-1.93 1.38-.49.08-1.11.11-1.79-.11-.41-.13-.94-.31-1.62-.6-2.85-1.23-4.71-4.1-4.85-4.29-.14-.19-1.16-1.54-1.16-2.94 0-1.4.73-2.08 1-2.37.26-.28.57-.35.76-.35h.55c.18 0 .41-.07.64.49.24.57.81 1.98.88 2.12.07.14.11.31.02.5-.09.19-.14.31-.28.47-.14.16-.29.36-.42.48-.14.14-.28.28-.12.55.16.28.71 1.17 1.53 1.9 1.05.94 1.94 1.23 2.21 1.37.28.14.44.12.6-.07.16-.19.68-.79.86-1.06.18-.28.36-.23.6-.14.24.09 1.55.73 1.82.86.27.14.44.2.51.32.07.11.07.65-.17 1.33z"/></svg>
  <span class="float-wa-label">Chat with us</span>
</a>
</body>
</html>"""


def stat(value, label):
    return f'<div class="stat"><b>{value}</b><span>{label}</span></div>'


def icard(icon, title, desc):
    return f'<div class="icard"><div class="ic">{icon}</div><h3>{title}</h3><p>{desc}</p></div>'


INDUSTRIES = [
    ("💊", "Pharma &amp; Healthcare", "Field-force &amp; MR gifting, hospital &amp; clinic rewards"),
    ("🛒", "FMCG", "Trade gifting, distributor incentives, retail rollouts"),
    ("💼", "IT &amp; Corporate Offices", "Employee onboarding &amp; reward programmes"),
    ("🏭", "Manufacturing", "Channel partner &amp; dealer recognition gifts"),
    ("🏦", "BFSI", "Banks, NBFCs &amp; insurance client gifting"),
    ("🎓", "Education", "Institutional &amp; staff recognition gifting"),
    ("🏨", "Hospitality", "Guest amenities &amp; staff reward gifting"),
    ("🛍️", "Retail &amp; E-commerce", "Seasonal &amp; festive bulk gifting programmes"),
]


def industries_html():
    cards = "".join(
        f'<div class="icard"><div class="ic">{ic}</div><h3>{name}</h3><p>{desc}</p></div>'
        for ic, name, desc in INDUSTRIES
    )
    return f"""
  <section class="block">
    <h2>Industries we serve</h2>
    <p>12 years of bulk gifting programmes for procurement and HR teams across India's
    largest-volume sectors — from pharma field-force incentives to FMCG trade gifting.</p>
    <div class="card-grid">{cards}</div>
  </section>
"""


def build_about(total, brand_count):
    stats_html = '<div class="stat-row">' + "".join([
        stat("12 Years", "Trusted Gifting"),
        stat("500+", "Corporate Clients"),
        stat(f"{brand_count}", "Authorised Brands"),
        stat(f"{total:,}", "Products Catalogued"),
    ]) + "</div>"

    body = f"""
  <section class="block">
    <h2>Our story</h2>
    <p>Nalanda Enterprises has spent 12 years building trust as a Chandigarh-based authorised
    corporate gifting partner. What started as a regional distributor relationship has grown into
    a catalog of {brand_count} authorised brands and {total:,} verified-MRP products, serving
    500+ corporate clients — from pharma field-force incentive programmes to FMCG trade gifting,
    IT employee onboarding kits to festive dealer rollouts. We consolidate price lists and product
    catalogues from every authorised brand we carry — spanning electronics, home appliances,
    dinnerware, luggage and lifestyle categories — into one searchable catalog, so dealers,
    procurement teams and HR departments across India can source and price bulk corporate gifting
    orders without chasing dozens of separate vendor PDFs.</p>
  </section>
  <section class="block">
    <h2>How we work</h2>
    <div class="card-grid">
      {icard("✅", "Verified MRP", "Every price is sourced from the vendor's own current price list or checked against official retail listings.")}
      {icard("🔄", "Kept Current", "The catalog is refreshed as our authorised brands update pricing, so quotes are built on current numbers, not stale sheets.")}
      {icard("🏷️", "Authorised Distribution", "Every listed brand is sourced through Nalanda Enterprises' own authorised distributor network — not grey-market resale.")}
      {icard("🇮🇳", "Pan-India Sourcing", "Brand partnerships across electronics, appliances and lifestyle categories, fulfilled from Chandigarh.")}
      {icard("💬", "A Gifting Specialist, Not a Form", "Every enquiry — WhatsApp, call or email — reaches a person who builds your options and pricing directly.")}
      {icard("🎁", "Built for Bulk", "From festive/Diwali gifting programs to employee reward rollouts, quantities and budgets are handled as a program, not a one-off order.")}
    </div>
  </section>
  {industries_html()}
  <section class="block">
    <h2>Who we work with</h2>
    <p>Procurement teams sourcing employee gifts, dealers stocking up for the festive season, HR
    departments running reward programs, and event/gifting agencies putting together client
    packages — anyone who needs verified pricing across many brands at once, at bulk quantities.</p>
    <a class="btn-primary" href="../contact/">Get in touch &rarr;</a>
  </section>
"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "AboutPage",
        "name": "About Nalanda Enterprises",
        "url": f"{PRIMARY_DOMAIN}/about/",
        "mainEntity": {
            "@type": "Organization",
            "name": "Nalanda Enterprises",
            "url": f"{PRIMARY_DOMAIN}/",
            "telephone": "+91-9115513366",
            "email": "info@nalandaenterprises.com",
            "foundingDate": "2014",
            "address": {"@type": "PostalAddress", "streetAddress": "SCF-4, Sector 19D",
                        "addressLocality": "Chandigarh", "addressCountry": "IN"},
        }
    }
    return stats_html, body, jsonld


PROGRAMS = [
    ("🎉", "Employee Onboarding Kits", "Welcome hampers that make a first impression from day one."),
    ("🏆", "Rewards &amp; Recognition", "Milestone gifts for work anniversaries, promotions and top performers."),
    ("🎆", "Festival Gifting", "Diwali, New Year and festive programmes planned and delivered on time, every year."),
    ("🤝", "Client Appreciation", "Premium gifts that strengthen relationships, branded to your company."),
    ("📈", "Channel Partner &amp; Dealer Rewards", "Scalable recognition gifting for distributors and dealers."),
    ("🎯", "Sales Incentive Programs", "Structured incentive gifting for quarterly and annual achievers."),
]


def build_services(total, brand_count):
    programs_cards = "".join(
        f'<div class="icard"><div class="ic">{ic}</div><h3>{name}</h3><p>{desc}</p></div>'
        for ic, name, desc in PROGRAMS
    )
    body = f"""
  <section class="block">
    <h2>Corporate gifting, sourced and supplied in bulk</h2>
    <div class="card-grid">
      {icard("🏢", "Corporate &amp; Employee Gifting", "Reward and onboarding gifts sourced across electronics, wearables and lifestyle categories, at quantity pricing.")}
      {icard("🎆", "Festive &amp; Diwali Programs", "Seasonal gifting rollouts planned ahead of Diwali and other festive occasions, across budget tiers.")}
      {icard("🏬", "Dealer &amp; Distributor Stock", "Bulk stock sourcing across {brand_count} authorised brands for dealers and retailers, at verified MRP.")}
      {icard("🎯", "Budget-Tiered Curation", "Options built around a per-unit budget — under ₹500 up to premium appliance tiers — not a fixed catalog page.")}
      {icard("🎁", "E-Gift Card Add-Ons", "20+ leading e-gift card brands (Flipkart, Amazon, Myntra and more) available as a flexible add-on alongside physical gifts.")}
      {icard("📋", "Quotation &amp; Proposal Support", "Priced, presentation-ready product proposals built from the live catalog for your internal approvals.")}
    </div>
  </section>
  <section class="block">
    <h2>Every gifting occasion, handled by one team</h2>
    <p>12 years of experience across the full corporate gifting lifecycle — from a new hire's first day
    to a dealer's tenth year with us.</p>
    <div class="card-grid">{programs_cards}</div>
  </section>
  {industries_html()}
  <section class="block">
    <h2>The catalog behind every quote</h2>
    <p>All {total:,} products across {brand_count} authorised brands are searchable by name, spec or
    budget in the live catalog — the same data every quote and proposal is built from.</p>
    <a class="btn-primary" href="../#catalog">Search the Catalog &rarr;</a>
  </section>
"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": "Corporate Gifting Sourcing and Supply",
        "provider": {"@type": "Organization", "name": "Nalanda Enterprises", "url": f"{PRIMARY_DOMAIN}/"},
        "areaServed": "IN",
        "url": f"{PRIMARY_DOMAIN}/services/",
    }
    return "", body, jsonld


def build_contact():
    body = """
  <div class="contact-grid">
    <div>
      <section class="block" style="padding-top:0;">
        <h2>Talk to a gifting specialist</h2>
        <p>Tell us the occasion, quantity and budget — we'll put together options and pricing from
        the live catalog. Every enquiry reaches a person directly, not a ticket queue.</p>
        <div class="contact-list">
          <div class="row">📞 <b>+91 91155 13366</b> / +91 95699 13332</div>
          <div class="row">✉️ <b><a href="mailto:info@nalandaenterprises.com" style="color:inherit;text-decoration:underline">info@nalandaenterprises.com</a></b></div>
          <div class="row">📍 <b>Nalanda Enterprises</b>, SCF-4, Sector 19D, Chandigarh, India</div>
        </div>
      </section>
    </div>
    <div class="contact-box">
      <h3>Request Bulk Pricing</h3>
      <p>Fastest way to reach us directly.</p>
      <a href="https://wa.me/919115513366?text=Hi%2C%20I%27d%20like%20to%20enquire%20about%20corporate%20gifting%20options." target="_blank" rel="noopener">💬 Chat on WhatsApp</a>
      <a href="tel:+919115513366">📞 Call +91 91155 13366</a>
      <a href="mailto:info@nalandaenterprises.com?subject=Corporate%20Gifting%20Enquiry">✉️ Email Us</a>
      <a href="../#catalog">🔎 Search the Catalog First</a>
    </div>
  </div>
"""
    jsonld = {
        "@context": "https://schema.org",
        "@type": "ContactPage",
        "url": f"{PRIMARY_DOMAIN}/contact/",
        "mainEntity": {
            "@type": "Organization",
            "name": "Nalanda Enterprises",
            "telephone": "+91-9115513366",
            "address": {"@type": "PostalAddress", "streetAddress": "SCF-4, Sector 19D",
                        "addressLocality": "Chandigarh", "addressCountry": "IN"},
        }
    }
    return "", body, jsonld


def main():
    site_meta = json.load(open(os.path.join(OUT_DIR, "site_meta.json")))
    total = site_meta["total"]
    brand_count = site_meta["authorised_brand_count"]

    pages = [
        ("about", "About Nalanda Enterprises | 12 Years of Corporate Gifting India",
         f"12 years, 500+ corporate clients, {brand_count} authorised brands — Chandigarh-based corporate "
         f"gifting partner for Pharma, FMCG, IT and Healthcare companies across India.",
         "COMPANY", "About Nalanda Enterprises", "About",
         f"Authorised corporate gifting partner sourcing {total:,} products across {brand_count} brands — verified MRP, bulk supply, Chandigarh-based.",
         *build_about(total, brand_count)),
        ("services", "Corporate Gifting Services for Pharma, FMCG &amp; IT | Nalanda Enterprises",
         f"Bulk corporate gifting for Pharma, FMCG, IT and Manufacturing companies — festive programs, "
         f"dealer stock sourcing and budget-tiered gift curation across {brand_count} authorised brands.",
         "SERVICES", "Corporate Gifting Services", "Services",
         "Bulk corporate gifting, festive gifting programs, dealer stock sourcing and budget-tiered curation.",
         *build_services(total, brand_count)),
        ("contact", "Contact Nalanda Enterprises | Corporate Gifting India",
         "Reach Nalanda Enterprises for bulk corporate gifting quotes — WhatsApp, phone or visit us in Sector 19D, Chandigarh.",
         "CONTACT", "Contact Us", "Contact",
         "Contact Nalanda Enterprises for bulk corporate gifting pricing and quotes.",
         *build_contact()),
    ]

    urls = []
    for slug, title, description, eyebrow, h1, breadcrumb_label, og_desc, stats_html, body_html, jsonld in pages:
        canonical = f"{PRIMARY_DOMAIN}/{slug}/"
        page = PAGE_SHELL.format(
            title=title, description=description, canonical=canonical, navy=NAVY,
            og_title=title, PRIMARY_DOMAIN=PRIMARY_DOMAIN,
            gtm_head=GTM_HEAD, gtm_body=GTM_BODY,
            jsonld=json.dumps(jsonld, ensure_ascii=False),
            breadcrumb_label=breadcrumb_label, eyebrow=eyebrow, h1=h1, intro=og_desc,
            stats_html=stats_html, body_html=body_html,
        )
        dir_path = os.path.join(SITE_DIR, slug)
        os.makedirs(dir_path, exist_ok=True)
        with open(os.path.join(dir_path, "index.html"), "w") as fh:
            fh.write(page)
        urls.append(f"/{slug}/")
        print(f"Wrote /{slug}/")

    # Merge into seo_page_urls.json (created by build_seo_pages.py) so
    # finalize_site_assets.py's sitemap picks these up too.
    seo_urls_path = os.path.join(OUT_DIR, "seo_page_urls.json")
    existing = json.load(open(seo_urls_path)) if os.path.exists(seo_urls_path) else []
    merged = urls + [u for u in existing if u not in urls]
    with open(seo_urls_path, "w") as fh:
        json.dump(merged, fh)
    print(f"Wrote {len(pages)} company pages; seo_page_urls.json now has {len(merged)} URLs")


if __name__ == "__main__":
    main()
