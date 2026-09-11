# -*- coding: utf-8 -*-
"""
Deterministic extraction of all 13 vendor xlsx price lists into a normalized
list of product dicts. Each vendor has a hand-written parser because column
layouts differ significantly (inspected via inspect_xlsx.py output).
"""
import openpyxl, os, json, re

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")

def ws_rows(path, sheet):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    return list(wb[sheet].iter_rows(values_only=True))

def num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return round(float(v), 2)
    if isinstance(v, str):
        s = v.replace(",", "").replace("₹", "").strip()
        try:
            return round(float(s), 2)
        except ValueError:
            return None
    return None

def clean(v):
    if v is None:
        return ""
    return str(v).strip()

def mk(brand, category, sub_category, product_name, model_code, description,
       variant, key_specs, mrp, landing_price, warranty, source_file, source_sheet):
    return dict(
        brand=brand, category=category, sub_category=sub_category,
        product_name=product_name, model_code=model_code, description=description,
        variant=variant, key_specs=key_specs, mrp=mrp, landing_price=landing_price,
        warranty=warranty, source_file=source_file, source_sheet=source_sheet,
    )

records = []

# ---------------------------------------------------------------- Belkin
def parse_belkin():
    f = "Belkin Apr-2026 Price list.xlsx"
    rows = ws_rows(os.path.join(BASE, f), "New Price ")
    cur_cat = None
    out = []
    for r in rows[2:]:
        if r[0] is None and r[1] and r[9] == 'MRP ':
            continue
        if r[0] is None and r[1]:
            cur_cat = clean(r[1])
            continue
        if r[0] is None:
            continue
        sr, code, desc, spec1, spec2, spec3, spec4, spec5, warranty, mrp, arp = (list(r) + [None]*11)[:11]
        specs = ", ".join([str(x) for x in [spec2, spec3, spec4, spec5] if x])
        out.append(mk("Belkin", "Electronics Accessories", cur_cat or "Accessories",
                       clean(desc), clean(code), clean(desc), clean(spec1), specs,
                       num(mrp), num(arp), clean(warranty), f, "New Price"))
    return out

# ---------------------------------------------------------------- Crompton
def parse_crompton():
    f = "Crompton List.xlsx"
    rows = ws_rows(os.path.join(BASE, f), "Sheet1")
    cur_cat = None
    out = []
    for r in rows[3:]:
        if r[0] and all(x is None for x in r[1:]):
            cur_cat = clean(r[0])
            continue
        if not r[0]:
            continue
        model, sweep, colour, feature, pack, mrp, price = (list(r) + [None]*7)[:7]
        specs = ", ".join([str(x) for x in [sweep, feature] if x])
        out.append(mk("Crompton", "Home Appliances & Fans", cur_cat or "Fans",
                       clean(model), "", clean(model), clean(colour), specs,
                       num(mrp), num(price), "", f, "Sheet1"))
    return out

# ---------------------------------------------------------------- GT / boAt
def parse_boat():
    f = "GT Price List_01-Sep'26 (1).xlsx"
    rows = ws_rows(os.path.join(BASE, f), "Retailer NLC")
    header = [clean(h) for h in rows[2]]
    idx = {h: i for i, h in enumerate(header)}
    out = []
    for r in rows[3:]:
        if not r[idx.get('M Name', 1)]:
            continue
        name = clean(r[idx['M Name']])
        cat = clean(r[idx['Category']])
        subcat = clean(r[idx['Sub-Category']])
        srp = num(r[idx['SRP']])
        nlc = num(r[idx.get('Retailer NLC After Pri./Sec.& Add.  Schemes', -1)]) if 'Retailer NLC After Pri./Sec.& Add.  Schemes' in idx else None
        mcode = clean(r[idx.get('M Code', 0)])
        out.append(mk("boAt", cat or "Audio & Wearables", subcat, name, mcode, name,
                       "", subcat, srp, nlc, "", f, "Retailer NLC"))
    return out

# ---------------------------------------------------------------- Goboult
def parse_goboult():
    f = "Goboult B2B Price List_2026_Jan..xlsx"
    rows = ws_rows(os.path.join(BASE, f), "Sheet1")
    out = []
    for r in rows[7:]:
        model = r[2]
        if not model:
            continue
        desc = r[3]; cat = r[4]; mrp = r[5]; dp = r[8]
        out.append(mk("boUlt", cat or "Audio", cat, clean(model), clean(model),
                       clean(desc), "", clean(desc), num(mrp), num(dp), "", f, "Sheet1"))
    return out

# ---------------------------------------------------------------- IFB
def parse_ifb():
    f = "IFB list.xlsx"
    out = []
    path = os.path.join(BASE, f)

    # FL / TL / CD -- Washing machines / dryer
    for sheet, cat in [("FL", "Front Load Washing Machine"), ("TL", "Top Load Washing Machine"), ("CD", "Clothes Dryer")]:
        rows = ws_rows(path, sheet)
        header = [clean(h) for h in rows[0]]
        idx = {h: i for i, h in enumerate(header)}
        for r in rows[1:]:
            if not r[idx.get('Model name', idx.get('Model Name', idx.get('New Model Name', 2)))]:
                continue
            model = r[idx.get('Model name', idx.get('Model Name', idx.get('New Model Name')))]
            cap = r[idx.get('Capacity')]
            mrp = r[idx.get('MRP')]
            dp = r[idx.get('DP')]
            colour = r[idx.get('Colour')]
            out.append(mk("IFB", "Home Appliances", cat, clean(model), clean(model),
                           f"{clean(model)} - {cap} kg" if cap else clean(model),
                           clean(colour), f"{cap} kg" if cap else "", num(mrp), num(dp), "", f, sheet))

    # MW-DW-KA microwave/dishwasher/kitchen appliances
    rows = ws_rows(path, "MW-DW-KA")
    for r in rows[2:]:
        if not r[2]:
            continue
        pcat, sap, model, channel, series1, series2, newmrp, mrp1, dp1, srp1, mrp2, dp2, srp2 = (list(r) + [None]*13)[:13]
        cat_map = {"MWO": "Microwave Oven", "DW": "Dishwasher", "KA": "Kitchen Appliance"}
        cat = cat_map.get(clean(pcat), clean(pcat) or "Kitchen Appliance")
        mrp = mrp2 if mrp2 else mrp1
        dp = dp2 if dp2 else dp1
        out.append(mk("IFB", "Home Appliances", cat, clean(model), clean(model),
                       clean(series1), "", clean(series1), num(mrp), num(dp), "", f, "MW-DW-KA"))

    # Star rating sheets -> refrigerators
    for sheet in ["2026 Star Rating", "2025 Star Rating"]:
        rows = ws_rows(path, sheet)
        header = [clean(h) for h in rows[0]]
        idx = {h: i for i, h in enumerate(header)}
        mrp_key = "MRP" if "MRP" in idx else "MRP (Rs.)"
        dp_key = "DP" if "DP" in idx else "DP (Rs.)"
        for r in rows[1:]:
            desc_idx = idx.get('Model Description 2026', idx.get('Model Description'))
            if desc_idx is None or not r[desc_idx]:
                continue
            desc = r[desc_idx]
            finish = r[idx.get('Finish Name', -1)] if 'Finish Name' in idx else None
            star = r[idx.get('Star', -1)] if 'Star' in idx else None
            mrp = r[idx.get(mrp_key)]
            dp = r[idx.get(dp_key)]
            out.append(mk("IFB", "Home Appliances", "Refrigerator (Direct Cool)", clean(desc), clean(desc),
                           f"{clean(desc)} {clean(finish)} {star or ''}★".strip(),
                           clean(finish), f"{star}★" if star else "", num(mrp), num(dp), "", f, sheet))

    # AC new model
    rows = ws_rows(path, "AC new Model")
    for r in rows[1:]:
        if not r[1]:
            continue
        sap, model, model2, mrp, dp, mop = (list(r) + [None]*6)[:6]
        out.append(mk("IFB", "Home Appliances", "Air Conditioner", clean(model), clean(model),
                       clean(model), "", "", num(mrp), num(dp), "", f, "AC new Model"))

    # AC old model
    rows = ws_rows(path, "AC old Model")
    for r in rows[2:]:
        series, cap, sap, detail, mrp, dp = (list(r) + [None]*10)[:6]
        if not detail:
            continue
        mrp_v = num(mrp)
        dp_v = num(dp)
        out.append(mk("IFB", "Home Appliances", "Air Conditioner", clean(detail), clean(detail),
                       clean(detail), clean(series), clean(cap) if cap else "", mrp_v, dp_v, "", f, "AC old Model"))
    return out

# ---------------------------------------------------------------- Lifelong
def parse_lifelong():
    f = "Life long B2B Pricng sheet 16th April.xlsx"
    path = os.path.join(BASE, f)
    sheet_cat = {
        "SHA": "Small Home Appliances", "HCD": "Health, Care & Wellness Devices",
        "Sports & fitness": "Sports & Fitness", "Electronics": "Electronics & Gadgets",
        "Home Improvement": "Home Improvement & Safety", "Emerging Innovation": "Innovative Gadgets",
        "Personal Care": "Personal Care Appliances", "Seasonal Products": "Seasonal Products",
    }
    out = []
    for sheet, cat in sheet_cat.items():
        rows = ws_rows(path, sheet)
        header_row_idx = 0
        for i, r in enumerate(rows[:3]):
            if r and any(c and 'SKU' in str(c) for c in r):
                header_row_idx = i
                break
        header = [clean(h) for h in rows[header_row_idx]]
        idx = {h: i for i, h in enumerate(header)}
        subcat_key = 'Sub Cat' if 'Sub Cat' in idx else ('SubCat' if 'SubCat' in idx else ('Sub Category' if 'Sub Category' in idx else ('Category' if 'Category' in idx else None)))
        for r in rows[header_row_idx+1:]:
            sku_i = idx.get('SKU')
            if sku_i is None or not r[sku_i]:
                continue
            desc = r[idx.get('Description', -1)]
            mrp = r[idx.get('MRP', -1)] if 'MRP' in idx else (r[idx.get('MRP ')] if 'MRP ' in idx else None)
            b2b = None
            for k in idx:
                if 'B2B Price' in k:
                    b2b = r[idx[k]]
            warranty = r[idx.get('Warranty', -1)] if 'Warranty' in idx else None
            subcat = clean(r[idx[subcat_key]]) if subcat_key else ""
            out.append(mk("Lifelong", cat, subcat, clean(desc), clean(r[sku_i]),
                           clean(desc), "", subcat, num(mrp), num(b2b), clean(warranty), f, sheet))
    return out

# ---------------------------------------------------------------- Marshall
def parse_marshall():
    f = "Marshall updated DP Price list.xlsx"
    rows = ws_rows(os.path.join(BASE, f), "Dealer Price List")
    out = []
    for r in rows[1:]:
        if not r[0]:
            continue
        dea, desc, colour, mrp, mop, margin, nlc = (list(r) + [None]*7)[:7]
        name = re.sub(r'\s+', ' ', clean(dea)).strip()
        out.append(mk("Marshall", "Audio", "Bluetooth Speaker", name, clean(desc),
                       name, clean(colour), "", num(mrp), num(nlc), "", f, "Dealer Price List"))
    return out

# ---------------------------------------------------------------- Preethi
def parse_preethi():
    f = "PREETHI Appliances List.xlsx"
    rows = ws_rows(os.path.join(BASE, f), "Final Price List of Corp Incent")
    out = []
    for r in rows[1:]:
        if not r[2]:
            continue
        cat, code, model, modelno, mrp, price, ean, hsn, cases = (list(r) + [None]*9)[:9]
        out.append(mk("Preethi", "Kitchen Appliances", clean(cat), clean(model), clean(modelno),
                       f"{clean(model)} ({clean(modelno)})", "", clean(cat), num(mrp), num(price), "", f, "Final Price List of Corp Incent"))
    return out

# ---------------------------------------------------------------- Philips
def parse_philips():
    f = "Philips.xlsx"
    rows = ws_rows(os.path.join(BASE, f), "Sheet1")
    out = []
    for r in rows[3:]:
        if not r[2]:
            continue
        product, subcat, modelno, partcode, desc, mrp, exgst, incgst = (list(r) + [None]*8)[:8]
        out.append(mk("Philips", clean(product) or "Electronics", clean(subcat), clean(desc), clean(modelno),
                       clean(desc), "", clean(subcat), num(mrp), num(incgst), "", f, "Sheet1"))
    return out

# ---------------------------------------------------------------- Thermoware
def parse_thermoware():
    f = "REVISED NEW THERMOWARE DP & MRP PRICE LIST - 09.04.2026.xlsx"
    rows = ws_rows(os.path.join(BASE, f), "THERMOWARE PRICE LIST")
    out = []
    for r in rows[2:]:
        if not r[1]:
            continue
        group, name, pkd, dp, mrp, gst = (list(r) + [None]*6)[:6]
        out.append(mk("Thermoware", "Kitchen & Dining", clean(group), clean(name), "",
                       clean(name), "", clean(group), num(mrp), num(dp), "", f, "THERMOWARE PRICE LIST"))
    return out

# ---------------------------------------------------------------- Usha
def parse_usha():
    f = "Usha List.xlsx"
    rows = ws_rows(os.path.join(BASE, f), "Pricing w.e.f 010626")
    out = []
    for r in rows[1:]:
        if not r[4]:
            continue
        division, rating, cat, matcode, desc, mrp, gdbp, supp_pct, supp_unit, billing, invoice = (list(r) + [None]*11)[:11]
        out.append(mk("Usha", "Home Appliances & Fans", clean(cat), clean(desc), clean(matcode),
                       clean(desc), "", clean(cat), num(mrp), num(invoice), "", f, "Pricing w.e.f 010626"))
    return out

# ---------------------------------------------------------------- Whirlpool
def parse_whirlpool():
    f = "Whirlpool ASM MAY PRICE LIST 2026.xlsx"
    rows = ws_rows(os.path.join(BASE, f), "Sheet1")
    out = []
    for r in rows[1:]:
        if not r[1]:
            continue
        material, desc, cat, mrp, dp, asm, price = (list(r) + [None]*7)[:7]
        cat_map = {"NF": "Refrigerator", "WM": "Washing Machine", "AC": "Air Conditioner"}
        catn = cat_map.get(clean(cat), clean(cat) or "Home Appliances")
        out.append(mk("Whirlpool", "Home Appliances", catn, clean(desc), clean(material),
                       clean(desc), "", catn, num(mrp), num(price), "", f, "Sheet1"))
    return out

# ---------------------------------------------------------------- Portronics
def parse_portronics():
    f = "dp list portronics august (1).xlsx"
    rows = ws_rows(os.path.join(BASE, f), "Sheet1")
    out = []
    for r in rows[3:]:
        if not r[1]:
            continue
        _, code, product, colour, cat, supercat, ean, hsn, mrp, taxrate, pregst, gst, allincl = (list(r) + [None]*13)[:13]
        out.append(mk("Portronics", clean(supercat) or "Electronics Accessories", clean(cat), clean(product), clean(code),
                       clean(product), clean(colour), clean(cat), num(mrp), num(allincl), "", f, "Sheet1"))
    return out


ALL_PARSERS = [
    parse_belkin, parse_crompton, parse_boat, parse_goboult, parse_ifb,
    parse_lifelong, parse_marshall, parse_preethi, parse_philips,
    parse_thermoware, parse_usha, parse_whirlpool, parse_portronics,
]

if __name__ == "__main__":
    all_records = []
    summary = []
    for fn in ALL_PARSERS:
        recs = fn()
        all_records.extend(recs)
        summary.append(f"{fn.__name__}: {len(recs)} records")
    print("\n".join(summary))
    print("TOTAL:", len(all_records))
    with open(os.path.join(OUT, "xlsx_records.json"), "w") as f:
        json.dump(all_records, f, indent=1, ensure_ascii=False)
    print("Saved to", os.path.join(OUT, "xlsx_records.json"))
