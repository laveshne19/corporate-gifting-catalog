# -*- coding: utf-8 -*-
import openpyxl, os, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
F = "safari price list.xlsx"

CAT_MAP = {
    "BP": "Backpack",
    "HL": "Hard Luggage",
    "ROLLING DUFFLE": "Rolling Duffle Bag",
    "DUFFLE BAG": "Duffle Bag",
    "LAPTOP TROLLY": "Laptop Trolley Bag",
}

def num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return round(float(v), 2)
    try:
        return round(float(str(v).replace(",", "")), 2)
    except ValueError:
        return None

def clean(v):
    return str(v).strip() if v is not None else ""

def parse():
    wb = openpyxl.load_workbook(os.path.join(BASE, F), read_only=True, data_only=True)
    ws = wb["Sheet1"]
    rows = list(ws.iter_rows(values_only=True))
    header = [clean(h) for h in rows[0]]
    idx = {h: i for i, h in enumerate(header)}
    out = []
    for row in rows[1:]:
        material = row[idx.get('Material', 0)]
        if not material:
            continue
        desc = clean(row[idx.get('Material Description')])
        cat_code = clean(row[idx.get('Category')])
        rng = clean(row[idx.get('Range')])
        colour = clean(row[idx.get('Colour')])
        size = clean(row[idx.get('Size')])
        mrp = num(row[idx.get('MRP')])
        price = num(row[idx.get('Pricing')])
        subcat = CAT_MAP.get(cat_code, cat_code or "Luggage")
        name = f"Safari {rng} {size} - {colour}".strip() if rng else desc
        out.append(dict(
            brand="Safari", category="Luggage & Bags", sub_category=subcat,
            product_name=name or desc, model_code=clean(material),
            description=desc, variant=colour, key_specs=f"Size: {size}" if size else "",
            mrp=mrp, landing_price=price, warranty="",
            source_file=F, source_sheet="Sheet1",
        ))
    return out

if __name__ == "__main__":
    recs = parse()
    print("TOTAL", len(recs))
    for r in recs[:6]:
        print(" ", r["sub_category"], "|", r["product_name"], "|", r["mrp"], r["landing_price"])
    with open(os.path.join(OUT, "safari_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
