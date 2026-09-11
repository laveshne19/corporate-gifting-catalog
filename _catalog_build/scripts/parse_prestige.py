# -*- coding: utf-8 -*-
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
f = "Prestige Appliance_Price List_2026_May_R.pdf"

def get_lines():
    d = pymupdf.open(os.path.join(BASE, f))
    lines = []
    for p in d:
        for l in p.get_text().split("\n"):
            l = l.strip().replace("ﬁ ", "fi").replace("ﬁ", "fi").replace("ﬂ ", "fl").replace("ﬂ", "fl")
            if l:
                lines.append(l)
    return lines

SKU_RE = re.compile(r'^\d{4,6}$')
NUM_RE = re.compile(r'^[\d,]+(\.\d+)?$')
BOILERPLATE = {"product", "image", "sku", "product description", "mrp", "dealer", "price",
               "case", "lot", "ssp", "dealer price"}

def parse():
    lines = get_lines()
    out = []
    header_stack = []
    i = 0
    n = len(lines)
    while i < n:
        low = lines[i].lower()
        if low in BOILERPLATE:
            i += 1
            continue
        if SKU_RE.match(lines[i]) and i + 4 < n:
            desc = lines[i+1]
            mrp_l, dp_l, case_l, ssp_l = lines[i+2], lines[i+3], lines[i+4], lines[i+5] if i+5 < n else ""
            if NUM_RE.match(mrp_l) and NUM_RE.match(dp_l):
                # case/lot sometimes missing -> only 3 numeric fields follow; detect by checking ssp_l validity
                if NUM_RE.match(case_l) and len(case_l) <= 2 and NUM_RE.match(ssp_l):
                    mrp_v = float(mrp_l.replace(",", ""))
                    dp_v = float(dp_l.replace(",", ""))
                    cat = header_stack[-2] if len(header_stack) >= 2 else (header_stack[-1] if header_stack else "Kitchen Appliances")
                    subcat = header_stack[-1] if header_stack else ""
                    out.append(dict(
                        brand="Prestige", category=cat.title(), sub_category=subcat.title(),
                        product_name=desc, model_code=lines[i], description=desc, variant="",
                        key_specs=subcat.title(), mrp=mrp_v, landing_price=dp_v, warranty="",
                        source_file=f, source_sheet="page text",
                    ))
                    i += 6
                    continue
        # header heuristic: short, mostly uppercase, no digits
        if lines[i].isupper() and not any(c.isdigit() for c in lines[i]) and len(lines[i]) < 45:
            header_stack.append(lines[i])
            if len(header_stack) > 2:
                header_stack.pop(0)
        i += 1
    return out

if __name__ == "__main__":
    recs = parse()
    print("Parsed", len(recs))
    for r in recs[:8]:
        print(" ", r["category"], "|", r["sub_category"], "|", r["product_name"], r["mrp"], r["landing_price"])
    with open(os.path.join(OUT, "prestige_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
