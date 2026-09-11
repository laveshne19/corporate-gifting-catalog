# -*- coding: utf-8 -*-
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
f = "Havells SDA LP MAY 26 Less-32.74%.pdf"
DISCOUNT = 0.3274  # from filename "Less-32.74%" -> approx distributor price

HEADER_LINES = {"model name/", "item description", "master pack", "no. of unit/s",
                 "item code", "hsn", "code", "lp in (rs.)", "per unit"}
PACK_RE = re.compile(r'^\d+\s*N$')
HSN_RE = re.compile(r'^\d{4}$')
PRICE_RE = re.compile(r'^`\s*([\d\s,]+\.\d{2})$')

def get_lines():
    d = pymupdf.open(os.path.join(BASE, f))
    lines = []
    for p in d:
        for l in p.get_text().split("\n"):
            l = l.strip()
            if l:
                lines.append(l)
    return lines

def parse():
    lines = get_lines()
    out = []
    last_end = 0
    n = len(lines)
    i = 0
    while i < n:
        if PACK_RE.match(lines[i]) and i + 2 < n:
            code = lines[i+1]
            hsn = lines[i+2]
            price_line = lines[i+3] if i + 3 < n else ""
            pm = PRICE_RE.match(price_line)
            if HSN_RE.match(hsn) and pm and re.match(r'^[A-Z0-9]{5,}$', code):
                candidates = lines[last_end:i]
                candidates = [c for c in candidates if c.lower() not in HEADER_LINES and not c.startswith("List Price") and not re.fullmatch(r'\d{1,2}', c) and len(c) > 1]
                if candidates:
                    name = candidates[0]
                    desc = " ".join(candidates[1:]) if len(candidates) > 1 else name
                    price_str = pm.group(1).replace(" ", "").replace(",", "")
                    mrp = float(price_str)
                    out.append(dict(
                        brand="Havells", category="Small Domestic Appliances", sub_category="",
                        product_name=name, model_code=code, description=f"{name} - {desc}" if desc != name else name,
                        variant="", key_specs=desc, mrp=round(mrp, 2),
                        landing_price=round(mrp * (1 - DISCOUNT), 2), warranty="",
                        source_file=f, source_sheet="page text",
                    ))
                last_end = i + 4
                i += 4
                continue
        i += 1
    return out

if __name__ == "__main__":
    recs = parse()
    print("Parsed", len(recs))
    for r in recs[:10]:
        print(" ", r["product_name"], "|", r["mrp"], r["landing_price"], "|", r["model_code"])
    with open(os.path.join(OUT, "havells_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
