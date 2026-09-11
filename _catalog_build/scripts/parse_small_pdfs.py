# -*- coding: utf-8 -*-
"""Parsers for the remaining small text-based price-list PDFs."""
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
    s = s.replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None

records = []

# ================= Qubo Distributor Price List =================
def parse_qubo_distributor():
    lines = get_lines("Distributor Price List-w.e.f. 1st Aug 2026.pdf")
    out = []
    i = 0
    # skip header
    while i < len(lines) and lines[i] not in ("MRP",):
        i += 1
    i += 1  # move past first 'MRP' header token
    cur_cat = "Smart Home Devices"
    while i < len(lines):
        code = lines[i]
        if code.startswith("Lifestyle products are available"):
            break
        if code in ("Category", "Product Name", "DLP Pre tax", "DLP", "Margin", "RLP", "MRP"):
            # second header block; skip 7 tokens
            i += 7
            continue
        if i + 6 >= len(lines):
            break
        name = lines[i+1]
        v1 = to_num(lines[i+2])
        v2 = to_num(lines[i+3])
        margin = lines[i+4]
        v3 = to_num(lines[i+5])
        mrp = to_num(lines[i+6])
        if code == "Lifestyle":
            cur_cat = "Lifestyle Accessories"
            code = ""
        out.append(dict(
            brand="Qubo", category=cur_cat, sub_category="", product_name=name,
            model_code=code, description=name, variant="", key_specs="",
            mrp=mrp, landing_price=v2, warranty="", source_file="Distributor Price List-w.e.f. 1st Aug 2026.pdf",
            source_sheet="page1",
        ))
        i += 7
    return out

records += parse_qubo_distributor()

# ================= NM RESELLER PRICELIST =================
def parse_nm_reseller():
    lines = get_lines("NM RESELLER PRICELIST 1.4.26 (1).pdf")
    return lines  # inspect first

nm_lines = parse_nm_reseller()

if __name__ == "__main__":
    print("Qubo distributor records:", len([r for r in records if r["brand"]=="Qubo"]))
    for r in records[:5]:
        print(r)
    print("\n--- NM RESELLER raw lines (first 60) ---")
    for l in nm_lines[:60]:
        print(repr(l))
