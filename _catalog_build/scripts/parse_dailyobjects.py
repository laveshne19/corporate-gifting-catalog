# -*- coding: utf-8 -*-
"""
DailyObjects corporate gifting catalogue (customer-facing PDF, MRP-only —
no NLC given, so budget falls back to the estimated-from-MRP path same as
other MRP-only sources). One page = a small grid of products: each product
has a photo directly above its name/material/price text block. A handful of
large "lifestyle" photos (a person using the bag, decorative backgrounds)
and tiny colour-swatch dots also appear as embedded images on the same
pages — filtered out by size (swatches) and by area fraction of the page
(lifestyle shots), since real product photos on this catalogue's grid pages
consistently land in the ~3-20% of page-area range.

Images are extracted to local files (this catalogue has no public product
URLs to link to instead) and referenced by relative path — clean_record()
already passes image_file through untouched, and finalize_site_assets.py
copies local paths into the site's images folder same as other local-image
brands.
"""
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
PDF = "/Users/laveshbansal/.claude/uploads/b3692fd6-d517-4c0a-9342-d40ac9724218/bdc7745c-Corporate_Catalogue__June_26.pdf"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
IMG_DIR = os.path.join(BASE, "_catalog_build", "images", "dailyobjects")

SECTION_PAGES = {
    4: "Everyday Carry", 25: "Work Essentials", 42: "Organisers",
    48: "Notebooks", 50: "Accessories", 57: "Phone Lanyards",
}
CONTENT_PAGE_RANGE = range(4, 59)  # bundles(59-63)/co-branding(64-66)/testimonials/contact excluded

PRICE_RE = re.compile(r'₹\s*([\d,]+)')

MATERIAL_WORDS = ("canvas", "leatherite", "recycled nylon", "recycled polyester", "cotton canvas",
                   "polyester and polyfill", "recycled pet", "aluminium", "genuine leather",
                   "leather", "ripstop", "polyester", "nylon", "vegan leather", "felt", "gan5",
                   "aerospace-grade", "powder coated", "uncoated paper", "pebbled", "tpu",
                   "full-grain", "fabric")

def is_paragraph(text):
    t = text.strip()
    words = t.split()
    return len(words) >= 9 or t.endswith((".", "—")) or t.count(".") >= 1

def is_name_line(text):
    t = text.strip()
    tl = t.lower()
    if not t or PRICE_RE.search(t):
        return False
    if '"' in t or '”' in t or "|" in t:
        return False  # size/variant line, e.g. Medium(14") | Large(16")
    if re.fullmatch(r'[\d\s.,%]+', t):
        return False  # bare numbers
    if is_paragraph(t):
        return False
    if t.isupper() and len(t.split()) <= 4:
        return False  # section/category header e.g. "CROSSBODY BAGS", "WEEKENDER BAGS"
    if any(mw in tl for mw in MATERIAL_WORDS):
        return False
    if len(t) < 3:
        return False
    return True

def parse():
    d = pymupdf.open(PDF)
    out = []
    cur_section = "Everyday Carry"
    img_counter = 0
    os.makedirs(IMG_DIR, exist_ok=True)

    for pno in CONTENT_PAGE_RANGE:
        if pno in SECTION_PAGES:
            cur_section = SECTION_PAGES[pno]
        pg = d[pno]
        page_area = pg.rect.width * pg.rect.height

        # Candidate product images: not tiny swatches, not huge lifestyle shots
        candidates = []
        for info in pg.get_image_info(xrefs=True):
            x0, y0, x1, y1 = info["bbox"]
            w, h = x1 - x0, y1 - y0
            if w < 40 or h < 40:
                continue
            frac = (w * h) / page_area
            if frac > 0.35:
                continue
            candidates.append({"xref": info["xref"], "bbox": (x0, y0, x1, y1)})

        blocks = [{"bbox": b[:4], "text": b[4]} for b in pg.get_text("blocks")]
        # Split multi-line blocks into individual lines with an approximated bbox.
        # Section-intro paragraphs are dropped whole (at the block level, using the
        # full block's word count) — checking line-by-line after wrapping misses
        # them, since each wrapped visual line individually looks short enough to
        # pass as a product name.
        lines = []
        for b in blocks:
            x0, y0, x1, y1 = b["bbox"]
            if is_paragraph(b["text"].replace("\n", " ")):
                continue
            parts = [l for l in b["text"].split("\n") if l.strip()]
            if not parts:
                continue
            h_per = (y1 - y0) / len(parts)
            for i, p in enumerate(parts):
                lines.append({"bbox": (x0, y0 + i * h_per, x1, y0 + (i + 1) * h_per), "text": p})

        # Group consecutive lines starting at each name-line into a product's text block
        products_text = []
        i = 0
        while i < len(lines):
            if is_name_line(lines[i]["text"]):
                name_parts = [lines[i]["text"].strip()]
                j = i + 1
                # A name can wrap onto a second line (no material/price/digits)
                while j < len(lines) and is_name_line(lines[j]["text"]) and len(name_parts) < 2:
                    name_parts.append(lines[j]["text"].strip())
                    j += 1
                attrs = []
                while j < len(lines) and not is_name_line(lines[j]["text"]):
                    attrs.append(lines[j]["text"].strip())
                    j += 1
                    if j < len(lines) and PRICE_RE.search(lines[j-1]["text"]):
                        break
                x0 = min(lines[i]["bbox"][0], lines[j-1]["bbox"][0] if j > i else lines[i]["bbox"][0])
                y0 = lines[i]["bbox"][1]
                products_text.append({"name": " ".join(name_parts), "attrs": attrs,
                                        "x0": lines[i]["bbox"][0], "x1": lines[i]["bbox"][2], "y0": y0})
                i = j
            else:
                i += 1

        # Match each product text block to the nearest candidate image above it
        used_xrefs = set()
        for pt in products_text:
            best = None
            best_gap = None
            for c in candidates:
                if c["xref"] in used_xrefs:
                    continue
                cx0, cy0, cx1, cy1 = c["bbox"]
                c_center = (cx0 + cx1) / 2
                if not (pt["x0"] - 40 <= c_center <= pt["x1"] + 40):
                    continue
                gap = pt["y0"] - cy1
                if gap < -70 or gap > 220:
                    continue
                if best_gap is None or gap < best_gap:
                    best = c
                    best_gap = gap
            if best:
                used_xrefs.add(best["xref"])
                img_counter += 1
                pix = pymupdf.Pixmap(d, best["xref"])
                if pix.n - pix.alpha >= 4:
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                fname = f"do_{pno:02d}_{img_counter:04d}.png"
                fpath = os.path.join(IMG_DIR, fname)
                pix.save(fpath)
                pt["image_file"] = f"dailyobjects/{fname}"
            else:
                pt["image_file"] = ""

        for pt in products_text:
            attrs_text = [a for a in pt["attrs"]]
            prices = []
            for a in attrs_text:
                for m in PRICE_RE.finditer(a):
                    prices.append(float(m.group(1).replace(",", "")))
            material = next((a for a in attrs_text if not PRICE_RE.search(a) and "|" not in a
                              and not re.search(r'\d"', a)), "")
            variant = next((a for a in attrs_text if "|" in a or re.search(r'\d"', a)), "")
            mrp = min(prices) if prices else None  # base/lowest variant price
            out.append(dict(
                brand="DailyObjects", category="Corporate Gifting Accessories", sub_category=cur_section,
                product_name=pt["name"], model_code="",
                description=f"{pt['name']} — {material}".strip(" —"),
                variant=variant, key_specs=material,
                mrp=mrp, landing_price=None, warranty="",
                source_file="Corporate_Catalogue_June_26.pdf", source_sheet=f"page {pno+1}",
                image_file=pt["image_file"],
                image_source="Extracted from Corporate_Catalogue_June_26.pdf (official brand catalogue)" if pt["image_file"] else "",
            ))
    return out

if __name__ == "__main__":
    recs = parse()
    print(f"Parsed {len(recs)} DailyObjects products")
    with_img = sum(1 for r in recs if r["image_file"])
    print(f"With image: {with_img} ({with_img/len(recs)*100:.0f}%)")
    with open(os.path.join(OUT, "dailyobjects_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
    for r in recs[:20]:
        print(" ", r["product_name"], "|", r["mrp"], "|", r["variant"][:30], "|", "IMG" if r["image_file"] else "no-img")
