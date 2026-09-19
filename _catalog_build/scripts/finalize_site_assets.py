# -*- coding: utf-8 -*-
"""
Copy all referenced product images into the site's images/ folder, and
generate sitemap.xml + robots.txt for SEO indexing.
Run this AFTER master_consolidated.json has final image_file values.
"""
import json, os, re, shutil

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
IMG_SRC_DIR = os.path.join(BASE, "_catalog_build", "images")
SITE_DIR = os.path.join(BASE, "_catalog_build", "site")
SITE_IMG_DIR = os.path.join(SITE_DIR, "images")

DOMAINS = ["corporategiftingindia.co", "corporategiftingindia.net", "corporategiftingindia.info"]
PRIMARY_DOMAIN = "https://corporategiftingindia.co"

def copy_images():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    os.makedirs(SITE_IMG_DIR, exist_ok=True)
    copied, missing = 0, 0
    for r in recs:
        rel = r.get("image_file")
        if not rel or rel.startswith("http://") or rel.startswith("https://"):
            continue  # externally-hosted (web-scraped) image — nothing to copy
        src = os.path.join(IMG_SRC_DIR, rel)
        dst = os.path.join(SITE_IMG_DIR, rel)
        if not os.path.exists(src):
            missing += 1
            r["image_file"] = ""  # clear broken reference
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
        copied += 1
    with open(os.path.join(OUT_DIR, "master_consolidated.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
    print(f"Images copied to site: {copied}, missing/broken references cleared: {missing}")

def write_sitemap():
    seo_urls_path = os.path.join(OUT_DIR, "seo_page_urls.json")
    seo_urls = json.load(open(seo_urls_path)) if os.path.exists(seo_urls_path) else []

    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap.append(f"  <url><loc>{PRIMARY_DOMAIN}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>")
    for path in seo_urls:
        priority = "0.8" if path.startswith("/brands/") else "0.7"
        sitemap.append(f"  <url><loc>{PRIMARY_DOMAIN}{path}</loc><changefreq>weekly</changefreq><priority>{priority}</priority></url>")
    sitemap.append("</urlset>")
    with open(os.path.join(SITE_DIR, "sitemap.xml"), "w") as fh:
        fh.write("\n".join(sitemap))

    robots = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {PRIMARY_DOMAIN}/sitemap.xml",
    ]
    with open(os.path.join(SITE_DIR, "robots.txt"), "w") as fh:
        fh.write("\n".join(robots) + "\n")
    print(f"Wrote sitemap.xml ({1 + len(seo_urls)} URLs) and robots.txt")

def write_llms_txt():
    """GEO: a plain-text index for AI assistants/answer engines (ChatGPT,
    Perplexity, Claude, Gemini) that follow the emerging llms.txt convention
    — a curated, crawlable summary of what the site is and where to find
    the substantive pages, since the homepage itself is a JS-rendered SPA
    that a non-JS-executing crawler can't read past the hero copy."""
    site_meta_path = os.path.join(OUT_DIR, "site_meta.json")
    site_meta = json.load(open(site_meta_path)) if os.path.exists(site_meta_path) else {}
    total = site_meta.get("total", "12,000+")
    brand_count = site_meta.get("authorised_brand_count", 50)
    # brand_meta (not the raw `brands` list) is already scoped to authorised
    # distributor brands — it excludes resale/marketplace gift-card brands
    # (Amazon Pay, Blinkit, AJIO, etc.), which get no /brands/<slug>/ page
    # and must never be described as an authorised partnership.
    brand_meta = site_meta.get("brand_meta", [])
    cat_meta = site_meta.get("cat_meta", [])

    lines = [
        "# Corporate Gifting India",
        "",
        f"> India's corporate gifting catalog by Nalanda Enterprises — {total} products "
        f"across {brand_count} authorised brands (boAt, Noise, Swiss Military, Portronics, "
        "Samsung, Whirlpool, Haier, IFB, Usha, Lifelong, Cello and more), each with a "
        "verified MRP, for bulk corporate gifting, dealer stock and employee reward programs "
        "across India.",
        "",
        "Nalanda Enterprises is a Chandigarh-based authorised distributor and corporate "
        "gifting partner with 12 years' experience, sourcing electronics, appliances, "
        "dinnerware, luggage and lifestyle products in bulk for 500+ corporate clients. "
        "This site is the searchable master catalog: every product a prospective corporate "
        "buyer, dealer or procurement team can ask about.",
        "",
        "## Industries served",
        "Pharma & Healthcare (field-force/MR gifting, hospital rewards), FMCG (trade gifting, "
        "distributor incentives), IT & Corporate Offices (employee onboarding/rewards), "
        "Manufacturing (channel partner/dealer gifts), BFSI, Education, Hospitality, "
        "Retail & E-commerce.",
        "",
        "## Primary",
        f"- [Full searchable catalog]({PRIMARY_DOMAIN}/): all {total} products, filterable by "
        "brand, category and budget",
        f"- [About Nalanda Enterprises]({PRIMARY_DOMAIN}/about/): company history, stats, industries served",
        f"- [Corporate Gifting Services]({PRIMARY_DOMAIN}/services/): programs and occasions supported",
        "",
        "## Brand catalogs",
    ]
    for b in brand_meta:
        name = b["name"]
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        lines.append(f"- [{name}]({PRIMARY_DOMAIN}/brands/{slug}/): {b['count']} products, {b.get('category', '')}")

    lines += ["", "## Categories"]
    for c in cat_meta:
        slug = re.sub(r"[^a-z0-9]+", "-", c["name"].lower()).strip("-")
        lines.append(f"- [{c['name']}]({PRIMARY_DOMAIN}/categories/{slug}/): {c['count']} products")

    lines += [
        "",
        "## Contact",
        "- Nalanda Enterprises, SCF-4 Sector 19D, Chandigarh, India",
        "- Phone: +91-9115513366",
        "- For bulk quotes, dealer pricing or a specific product not listed here, use the "
        f"contact details on [{PRIMARY_DOMAIN}/]({PRIMARY_DOMAIN}/).",
    ]
    with open(os.path.join(SITE_DIR, "llms.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("Wrote llms.txt")

if __name__ == "__main__":
    copy_images()
    write_sitemap()
    write_llms_txt()
