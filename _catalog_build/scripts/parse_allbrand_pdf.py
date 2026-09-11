# -*- coding: utf-8 -*-
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
f = "All brand price list2.pdf"
OUT = os.path.join(BASE, "_catalog_build", "extracted")

d = pymupdf.open(os.path.join(BASE, f))
full_text = ""
page_texts = []
for p in d:
    t = p.get_text()
    page_texts.append(t)
    full_text += t + "\n"

NOISE_LINES = {"nalanda enterprises", "scf-4 sector 19d chandigarh", "9115513366/9569913332",
               "catalog and price list", "c a t a l o g a n d", "p r i c e l i s t"}

def clean_lines(txt):
    return [l.strip() for l in txt.split("\n") if l.strip() and l.strip().lower() not in NOISE_LINES]

records = []

# ---- Section boundaries by page index (0-based) ----
# 0-6: boAt (incl watches/earbuds/speakers)
# 7-9: FireBoltt watches (part of page 7-9)
# 10-13: Swiss Military Audio (handled separately in parse_swissmilitary_grid.py)
# 14: Mivi (starts) 14-15
# 16: Realme
# 17: Qubo
# 18: Vaku
# 19-21: WiWu, Amazon Echo/FireTV

boat_pages = "\n".join(page_texts[0:10])
mivi_pages = "\n".join(page_texts[14:16])
realme_pages = page_texts[16]
qubo_pages = page_texts[17]
vaku_pages = page_texts[18]
wiwu_pages = "\n".join(page_texts[19:21])
amazon_pages = page_texts[21] if len(page_texts) > 21 else ""

# Pattern A: NAME ... RS.### ... MRP-### / MRP ###  (allow newline, dash, space variants)
PAT_A = re.compile(
    r'([A-Z][A-Z0-9 \-\.’\'®]{2,60}?)\s*[\-\s]\s*(?:RS\.?|PRICE\s+RS-?)\s*[\-\s]*([\d,]+)\.?\s*[\r\n \-]*MRP\s*[\-`]?\s*([\d,]+)',
    re.MULTILINE
)

def parse_pattern_a(text, brand, category):
    out = []
    for m in PAT_A.finditer(text):
        name = re.sub(r'\s+', ' ', m.group(1)).strip(" -")
        price = float(m.group(2).replace(",", ""))
        mrp = float(m.group(3).replace(",", ""))
        if mrp < price:
            price, mrp = mrp, price
        if len(name) < 3:
            continue
        out.append(dict(
            brand=brand, category=category, sub_category="", product_name=name.title(),
            model_code="", description=name.title(), variant="", key_specs="",
            mrp=mrp, landing_price=price, warranty="", source_file=f,
            source_sheet="All brand price list (text)",
        ))
    return out

# boAt is deliberately NOT parsed from this crude multi-brand PDF: boAt has
# its own authoritative, per-SKU distributor price list ("GT Price List_01-
# Sep'26 (1).xlsx", parsed by parse_boat() in extract_xlsx.py) which covers
# every boAt product here plus color variants and clean model names. Cross-
# checking confirmed the two sources fully overlap and this PDF's numbers
# are wrong where they differ (e.g. Hive Dashcam F1/E1/M1 here were ~2.2x
# the real MRP from the distributor sheet) — so this PDF would only add
# duplicate listings with worse data, never new inventory.
records += parse_pattern_a(mivi_pages, "Mivi", "Audio")
records += parse_pattern_a(realme_pages, "Realme", "Electronics & Accessories")
records += parse_pattern_a(amazon_pages, "Amazon (Echo/Fire TV)", "Smart Devices")

# Fire-Boltt watches: pattern "FIRE-BOLTT NAME-price\nMRP-mrp" (no RS keyword)
PAT_FB = re.compile(r'(FIRE[\s\-]?BOLTT?\s+[A-Z0-9 \-\.\']{2,40}?)\s*[\-]\s*([\d,]+)\s*[\r\n]+\s*MRP\s*[\-]?\s*([\d,]+)')
for m in PAT_FB.finditer(boat_pages):
    name = re.sub(r'\s+', ' ', m.group(1)).strip(" -")
    price = float(m.group(2).replace(",", ""))
    mrp = float(m.group(3).replace(",", ""))
    if mrp < price:
        price, mrp = mrp, price
    records.append(dict(brand="Fire-Boltt", category="Wearables", sub_category="Smartwatch",
                         product_name=name.title(), model_code="", description=name.title(),
                         variant="", key_specs="", mrp=mrp, landing_price=price, warranty="",
                         source_file=f, source_sheet="All brand price list (text)"))

# Qubo: "QUBO NAME\nPRICE RS-price\nMRP-mrp" or "QUBI ..." (typo)
PAT_QUBO = re.compile(r'(QUBO?I?\s+[A-Z0-9 \-\.\+]{2,50}?)\s*[\-]?\s*\r?\n?\s*PRICE\s+RS-?\s*([\d,]+)\s*[\r\n]+\s*MRP\s*[\-]?\s*([\d,]+)')
for m in PAT_QUBO.finditer(qubo_pages):
    name = re.sub(r'\s+', ' ', m.group(1)).strip(" -")
    price = float(m.group(2).replace(",", ""))
    mrp = float(m.group(3).replace(",", ""))
    if mrp < price:
        price, mrp = mrp, price
    records.append(dict(brand="Qubo", category="Smart Home Devices", sub_category="",
                         product_name=name.title(), model_code="", description=name.title(),
                         variant="", key_specs="", mrp=mrp, landing_price=price, warranty="",
                         source_file=f, source_sheet="All brand price list (text)"))

# Vaku: "NAME-\nMRP-mrp" (no discount price given)
PAT_VAKU = re.compile(r'([A-Z][A-Z0-9 \-®\'’]{3,70}?)\s*[\-]\s*[\r\n]+\s*MRP\s*[\-]?\s*([\d,]+)')
for m in PAT_VAKU.finditer(vaku_pages):
    name = re.sub(r'\s+', ' ', m.group(1)).strip(" -")
    mrp = float(m.group(2).replace(",", ""))
    if len(name) < 4:
        continue
    records.append(dict(brand="Vaku", category="Electronics Accessories", sub_category="",
                         product_name=name.title(), model_code="", description=name.title(),
                         variant="", key_specs="", mrp=mrp, landing_price=None, warranty="",
                         source_file=f, source_sheet="All brand price list (text)"))

# WiWu: two formats -> "NAME-\nMRP-mrp" (no price) OR "NAME\n- MRP-mrp Price-price" / "MRP-mrp Price - price" or "Price - price" then "MRP-mrp"
PAT_WIWU_1 = re.compile(r'([A-Za-z][A-Za-z0-9 \-®\'’\.&,/]{3,80}?)\s*[\-\r\n]+\s*MRP\s*[\-]?\s*([\d,]+)\s*(?:Price|PRICE|Pfice)\s*[\-]?\s*([\d,]+)', re.MULTILINE)
seen_wiwu = set()
for m in PAT_WIWU_1.finditer(wiwu_pages):
    name = re.sub(r'\s+', ' ', m.group(1)).strip(" -")
    mrp = float(m.group(2).replace(",", ""))
    price = float(m.group(3).replace(",", ""))
    if mrp < price:
        price, mrp = mrp, price
    key = (name.lower(), mrp)
    if key in seen_wiwu or len(name) < 4:
        continue
    seen_wiwu.add(key)
    records.append(dict(brand="WiWu", category="Electronics Accessories", sub_category="",
                         product_name=name.title(), model_code="", description=name.title(),
                         variant="", key_specs="", mrp=mrp, landing_price=price, warranty="",
                         source_file=f, source_sheet="All brand price list (text)"))
# WiWu simple MRP-only (bags section, no discount price)
PAT_WIWU_2 = re.compile(r'([A-Z][A-Za-z0-9 \-®\'’\.&,/"]{3,80}?)\s*[\-]\s*[\r\n]+\s*MRP\s*[\-]?\s*([\d,]+)(?!\s*(?:Price|PRICE))')
for m in PAT_WIWU_2.finditer(wiwu_pages):
    name = re.sub(r'\s+', ' ', m.group(1)).strip(" -")
    mrp_s = m.group(2).replace(",", "")
    if not mrp_s:
        continue
    mrp = float(mrp_s)
    key = (name.lower(), mrp)
    if key in seen_wiwu or len(name) < 4:
        continue
    seen_wiwu.add(key)
    records.append(dict(brand="WiWu", category="Electronics Accessories", sub_category="",
                         product_name=name.title(), model_code="", description=name.title(),
                         variant="", key_specs="", mrp=mrp, landing_price=None, warranty="",
                         source_file=f, source_sheet="All brand price list (text)"))

# A handful of WiWu / Qubo entries from this crude PDF are exact-MRP-match
# duplicates of products already covered (with cleaner names and, for WiWu,
# real dealer landing cost) by WiWU_Dealer_Price_List.pdf and Qubo's own
# MRP Leaflet — drop those so the site doesn't show the same product twice
# at the same price under two different names.
_DUP_NAME_MRP = {
    ("WiWu", "wiwu universal pencil s-04", 5999.0),
    ("WiWu", "wireless charger dock", 4499.0),
    ("WiWu", "wireless charger", 5999.0),
    ("WiWu", "backpack", 22999.0),
    ("WiWu", "leather backpack, black", 16999.0),
    ("Qubo", "qubo instaview with tablet", 26980.0),
}
records = [r for r in records
           if (r["brand"], r["product_name"].lower(), r["mrp"]) not in _DUP_NAME_MRP]

if __name__ == "__main__":
    print("Total parsed:", len(records))
    by_brand = {}
    for r in records:
        by_brand.setdefault(r["brand"], []).append(r)
    for b, rs in by_brand.items():
        print(f"  {b}: {len(rs)}")
    with open(os.path.join(OUT, "allbrand_pdf_records.json"), "w") as fh:
        json.dump(records, fh, indent=1, ensure_ascii=False)
