# -*- coding: utf-8 -*-
"""
Copy all referenced product images into the site's images/ folder, and
generate sitemap.xml + robots.txt for SEO indexing.
Run this AFTER master_consolidated.json has final image_file values.
"""
import json, os, shutil

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
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sitemap.append(f"  <url><loc>{PRIMARY_DOMAIN}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>")
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
    print("Wrote sitemap.xml and robots.txt")

if __name__ == "__main__":
    copy_images()
    write_sitemap()
