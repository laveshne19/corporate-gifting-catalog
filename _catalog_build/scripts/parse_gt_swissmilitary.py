# -*- coding: utf-8 -*-
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
IMG_OUT = os.path.join(BASE, "_catalog_build", "images")
f = "Product Range Aug 2026_GT (2).pdf"

PRICE_RE = re.compile(r'MRP\s*-?\s*₹\s*([\d,]+)')

def get_lines(page):
    return [l.strip() for l in page.get_text().split("\n") if l.strip()]

def parse():
    d = pymupdf.open(os.path.join(BASE, f))
    out = []
    for pno in range(d.page_count):
        page = d[pno]
        lines = get_lines(page)
        text = page.get_text()
        m = PRICE_RE.search(text)
        if not m or len(lines) < 2:
            continue
        mrp = float(m.group(1).replace(",", ""))
        bullet_idx = next((i for i, l in enumerate(lines) if l.startswith("-")), None)
        if bullet_idx and bullet_idx >= 1:
            name = lines[bullet_idx - 1]
            category = lines[0] if bullet_idx - 1 != 0 else "Audio & Accessories"
        else:
            name = lines[1] if len(lines) > 1 else lines[0]
            category = lines[0]
        specs = [l for l in lines if l.startswith("-")]
        out.append(dict(
            brand="Swiss Military", category="Audio, Wearables & Accessories", sub_category=category,
            product_name=name, model_code="", description=" | ".join(s.lstrip("- ") for s in specs),
            variant="", key_specs=" | ".join(s.lstrip("- ") for s in specs),
            mrp=mrp, landing_price=None, warranty="",
            source_file=f, source_sheet=f"page {pno+1}",
        ))
    return out

# ---- extract images (same logic as extract_pdf_images.py) ----
def extract_images():
    d = pymupdf.open(os.path.join(BASE, f))
    safe = "".join(c if c.isalnum() else "_" for c in f)[:60]
    out_dir = os.path.join(IMG_OUT, safe)
    os.makedirs(out_dir, exist_ok=True)
    manifest = []
    seen = set()
    import hashlib
    for pno in range(d.page_count):
        page = d[pno]
        for idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            try:
                base = d.extract_image(xref)
            except Exception:
                continue
            w, h = base.get("width", 0), base.get("height", 0)
            if w < 250 or h < 250:
                continue
            data = base["image"]
            hh = hashlib.md5(data).hexdigest()[:12]
            if hh in seen:
                continue
            seen.add(hh)
            ext = base.get("ext", "png")
            fname = f"p{pno+1:03d}_{idx:02d}_{hh}.{ext}"
            with open(os.path.join(out_dir, fname), "wb") as fh:
                fh.write(data)
            manifest.append(dict(page=pno + 1, file=fname, width=w, height=h, rel_path=os.path.join(safe, fname)))
    return manifest

if __name__ == "__main__":
    recs = parse()
    print("Parsed", len(recs), "SM records from GT catalogue")
    manifest = extract_images()
    print("Extracted", len(manifest), "images")

    # pick largest image per page
    by_page = {}
    for im in manifest:
        by_page.setdefault(im["page"], []).append(im)
    for r in recs:
        pno = int(r["source_sheet"].split()[1])
        imgs = by_page.get(pno, [])
        if imgs:
            best = max(imgs, key=lambda im: im["width"] * im["height"])
            r["image_file"] = best["rel_path"]
            r["image_source"] = f"Extracted from Swiss Military catalogue PDF (page {pno})"

    with open(os.path.join(OUT, "gt_swissmilitary_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
    with_img = sum(1 for r in recs if r.get("image_file"))
    print(f"{with_img}/{len(recs)} records have an image assigned")
    for r in recs[:5]:
        print(" ", r["product_name"], r["mrp"], r.get("image_file"))
