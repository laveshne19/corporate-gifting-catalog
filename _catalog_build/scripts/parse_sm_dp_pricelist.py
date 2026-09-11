# -*- coding: utf-8 -*-
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
f = "SM DP PRICE LIST SEPT'26.pdf"

def get_lines():
    d = pymupdf.open(os.path.join(BASE, f))
    lines = []
    for p in d:
        for l in p.get_text().split("\n"):
            l = l.strip()
            if l:
                lines.append(l)
    return lines

PURE_INT = re.compile(r'^[\d,]+$')

def parse():
    lines = get_lines()
    out = []
    i = 0
    last_mrp_idx = -1
    n = len(lines)
    while i < n - 2:
        if PURE_INT.fullmatch(lines[i]):
            dp_val = float(lines[i].replace(",", ""))
            # carton size can be plain int or "120 (20pc box)" etc — just skip one line
            mrp_line = lines[i+2] if i + 2 < n else ""
            mrp_m = re.search(r'([\d,]{3,7})$', mrp_line) if PURE_INT.match(mrp_line) or '(' not in mrp_line else None
            if PURE_INT.fullmatch(mrp_line):
                mrp_val = float(mrp_line.replace(",", ""))
                if mrp_val >= dp_val and dp_val > 10:
                    name = lines[i-1] if i - 1 >= 0 else ""
                    desc = " ".join(lines[last_mrp_idx+1:i-1]) if i - 1 > last_mrp_idx + 1 else ""
                    if name and not PURE_INT.fullmatch(name):
                        out.append(dict(
                            brand="Swiss Military", category="Audio, Wearables & Accessories",
                            sub_category="", product_name=name, model_code="",
                            description=desc[:300], variant="", key_specs=desc[:300],
                            mrp=mrp_val, landing_price=dp_val, warranty="",
                            source_file=f, source_sheet="page text",
                        ))
                    last_mrp_idx = i + 2
                    i += 3
                    continue
        i += 1
    return out

if __name__ == "__main__":
    recs = parse()
    print("Parsed", len(recs), "records")
    for r in recs[:8]:
        print(r["product_name"], r["mrp"], r["landing_price"])
    with open(os.path.join(OUT, "sm_dp_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
