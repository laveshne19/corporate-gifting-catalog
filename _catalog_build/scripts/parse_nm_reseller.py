# -*- coding: utf-8 -*-
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
f = "NM RESELLER PRICELIST 1.4.26 (1).pdf"

def get_lines():
    d = pymupdf.open(os.path.join(BASE, f))
    lines = []
    for p in d:
        for l in p.get_text().split("\n"):
            l = l.strip()
            if l:
                lines.append(l)
    return lines

HSN_RE = re.compile(r'^\d{6,8}$')
PCT_RE = re.compile(r'^\d+%$')
NUM_RE = re.compile(r'^[\d,]+$')

def parse():
    lines = get_lines()
    out = []
    i = 0
    n = len(lines)
    cur_cat = lines[0] if lines else "Luggage & Bags"
    while i < n:
        if i + 5 < n and HSN_RE.match(lines[i+2]) and NUM_RE.match(lines[i+3]) and NUM_RE.match(lines[i+4]) and PCT_RE.match(lines[i+5]):
            typ, name, hsn, mrp, landing, gst = lines[i:i+6]
            try:
                mrp_v = float(mrp.replace(",", ""))
                landing_v = float(landing.replace(",", ""))
            except ValueError:
                i += 1
                continue
            out.append(dict(
                brand="NM", category=cur_cat.title(), sub_category=typ, product_name=name,
                model_code="", description=f"{name} ({typ})", variant="", key_specs=typ,
                mrp=mrp_v, landing_price=landing_v,
                warranty="", source_file=f, source_sheet="page text",
            ))
            if i + 6 < n:
                cur_cat = lines[i+6]
            i += 6
            continue
        i += 1
    return out

if __name__ == "__main__":
    recs = parse()
    print("Parsed", len(recs))
    for r in recs[:5]:
        print(" ", r["category"], r["sub_category"], "|", r["product_name"], r["mrp"], r["landing_price"])
    with open(os.path.join(OUT, "nm_reseller_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
