# -*- coding: utf-8 -*-
"""
Portronics catalogue is a PowerPoint-exported PDF: one product per slide/page,
with free-form element positions rather than a table. Plain get_text() reads
elements in whatever order they happen to sit in the PDF's content stream,
which is NOT reading order for a designed slide — on many pages a feature
bullet (e.g. "Bass Boost Technology") comes before the actual product name
("DASH 8"), so naively taking the first line produces garbage names that are
useless for both display and image search.

Every real product slide follows one consistent type style, though: the
product name is always set in Poppins-Bold at ~44pt (by far the largest text
on the page); the one-line marketing description is Poppins-Regular ~20pt;
feature bullets are Poppins-Light ~16pt; the price is ArialMT ~18pt with a
"₹" prefix; the model code is Poppins-SemiBold matching "POR ####". Using
font size/weight to identify each field (rather than line order) is what
actually gets the real product name.
"""
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
f = "Portronics_PPT_Mid-Aug_2026 (1).pdf"

PRICE_RE = re.compile(r'₹\s*([\d,]+)')
CODE_RE = re.compile(r'POR\s*\d+', re.IGNORECASE)

def parse():
    d = pymupdf.open(os.path.join(BASE, f))
    out = []
    cur_category = "Electronics Accessories"
    for pno in range(d.page_count):
        dct = d[pno].get_text("dict")
        lines = []  # (text, max_size, font)
        for block in dct["blocks"]:
            for line in block.get("lines", []):
                text = "".join(s["text"] for s in line["spans"]).strip()
                if not text:
                    continue
                size = max(s["size"] for s in line["spans"])
                font = line["spans"][0]["font"]
                lines.append((text, size, font))
        if not lines:
            continue

        name_parts = [t for t, sz, fo in lines if "Bold" in fo and sz >= 30]
        price_line = next((t for t, sz, fo in lines if PRICE_RE.search(t)), None)
        code_line = next((t for t, sz, fo in lines if CODE_RE.search(t)), None)

        if not name_parts:
            # No big-bold product name -> not a product slide (category
            # divider / section break, e.g. "AUDIO", "PC ACCESSORIES").
            plain = [t for t, sz, fo in lines]
            if not price_line and not code_line and len(plain) <= 3 and all(l.isupper() for l in plain):
                cur_category = " ".join(plain)
            continue

        name = " ".join(name_parts)
        mrp = float(PRICE_RE.search(price_line).group(1).replace(",", "")) if price_line else None
        code = CODE_RE.search(code_line).group(0).upper().replace("  ", " ") if code_line else ""

        desc_parts = [t for t, sz, fo in lines if 19 <= sz <= 21 and "Bold" not in fo]
        description = " ".join(desc_parts)

        used = set(name_parts) | {price_line, code_line, "MRP"} | set(desc_parts)
        specs = [t for t, sz, fo in lines if t not in used and t != "MRP" and not PRICE_RE.fullmatch(t)]
        key_specs = " | ".join(specs)

        out.append(dict(
            brand="Portronics", category=cur_category, sub_category="",
            product_name=name, model_code=code, description=description or name,
            variant="", key_specs=key_specs, mrp=mrp, landing_price=None,
            warranty="", source_file=f, source_sheet=f"page {pno+1}",
        ))
    return out

if __name__ == "__main__":
    recs = parse()
    print("Extracted", len(recs), "products from Portronics catalogue PDF")
    with open(os.path.join(OUT, "portronics_pdf_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
    for r in recs[:8]:
        print(" ", r["product_name"], "|", r["model_code"], "|", r["mrp"], "|", r["description"][:50])
