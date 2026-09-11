# -*- coding: utf-8 -*-
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
f = "Skyline List.pdf"

def get_lines():
    d = pymupdf.open(os.path.join(BASE, f))
    lines = []
    for p in d:
        for l in p.get_text().split("\n"):
            l = l.strip()
            if l:
                lines.append(l)
    return lines

HSN_RE = re.compile(r'^\d{8}$')
PCT_RE = re.compile(r'^\d+(\.\d+)?%$')
INT_RE = re.compile(r'^[\d,]+(\.\d+)?$')

def parse():
    lines = get_lines()
    out = []
    cur_cat = "Kitchen Appliances"
    i = 0
    n = len(lines)
    while i < n:
        if i + 6 < n and HSN_RE.match(lines[i+3]) and PCT_RE.match(lines[i+4]) and INT_RE.match(lines[i+5]) and INT_RE.match(lines[i+6]):
            model, pkg, name, hsn, tax, dp, mrp = lines[i:i+7]
            out.append(dict(
                brand="Skyline", category=cur_cat, sub_category="", product_name=name,
                model_code=model, description=name, variant="", key_specs="",
                mrp=float(mrp.replace(",", "")), landing_price=float(dp.replace(",", "")),
                warranty="", source_file=f, source_sheet="page text",
            ))
            i += 7
            continue
        # category header heuristic: short, all caps, no digits
        if lines[i].isupper() and not any(c.isdigit() for c in lines[i]) and len(lines[i]) < 40:
            cur_cat = lines[i].title()
        i += 1
    return out

if __name__ == "__main__":
    recs = parse()
    print("Parsed", len(recs))
    for r in recs[:5] + recs[-5:]:
        print(r["category"], "|", r["product_name"], r["mrp"], r["landing_price"])
    with open(os.path.join(OUT, "skyline_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
