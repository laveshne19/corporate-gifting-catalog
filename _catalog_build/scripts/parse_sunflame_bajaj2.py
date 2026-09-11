# -*- coding: utf-8 -*-
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")

def get_lines(fname):
    d = pymupdf.open(os.path.join(BASE, fname))
    lines = []
    for p in d:
        for l in p.get_text().split("\n"):
            l = l.strip()
            if l:
                lines.append(l)
    return lines

def to_num(s):
    s = s.replace("₹", "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None

# ================= Sunflame =================
def parse_sunflame():
    f = "Sunflame Price List - Direct Dealer W.E.F 15th Jun 2026.pdf"
    lines = get_lines(f)
    out = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].isdigit() and i + 8 < n:
            sno, cat, subcat, series, sap, desc, mrp, basic, gstprice = lines[i:i+9]
            if mrp.startswith("₹") and basic.startswith("₹"):
                out.append(dict(
                    brand="Sunflame", category=cat.title(), sub_category=subcat.title(),
                    product_name=desc, model_code=sap, description=f"{desc} ({series})",
                    variant=series, key_specs="", mrp=to_num(mrp), landing_price=to_num(gstprice),
                    warranty="", source_file=f, source_sheet="page text",
                ))
                i += 9
                continue
        i += 1
    return out

# ================= Bajaj (Consumer durables price list) =================
def parse_bajaj():
    f = "bajaj price list.pdf"
    lines = get_lines(f)
    out = []
    i = 0
    n = len(lines)
    BU_CODES = {"DAP", "FANS", "APP", "MOR", "LIGHT", "EF", "NP", "KAP", "MR", "MIXERS", "OTG", "JMG", "FP"}
    cur_cat = ""
    while i < n:
        if lines[i] in BU_CODES and i + 5 < n:
            bu, cat, sku, name, mrp, rlp = lines[i:i+6]
            mrp_v, rlp_v = to_num(mrp), to_num(rlp)
            if mrp_v is not None and rlp_v is not None:
                out.append(dict(
                    brand="Bajaj", category=cat, sub_category="", product_name=name,
                    model_code=sku, description=name, variant="", key_specs="",
                    mrp=mrp_v, landing_price=rlp_v, warranty="",
                    source_file=f, source_sheet="page text",
                ))
                i += 6
                continue
        i += 1
    return out

if __name__ == "__main__":
    sun = parse_sunflame()
    print("Sunflame:", len(sun))
    for r in sun[:5]:
        print(" ", r["category"], r["sub_category"], "|", r["product_name"], r["mrp"], r["landing_price"])
    with open(os.path.join(OUT, "sunflame_records.json"), "w") as fh:
        json.dump(sun, fh, indent=1, ensure_ascii=False)

    baj = parse_bajaj()
    print("Bajaj:", len(baj))
    for r in baj[:5]:
        print(" ", r["category"], "|", r["product_name"], r["mrp"], r["landing_price"])
    with open(os.path.join(OUT, "bajaj_pricelist_records.json"), "w") as fh:
        json.dump(baj, fh, indent=1, ensure_ascii=False)
