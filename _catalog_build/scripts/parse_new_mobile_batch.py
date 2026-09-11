# -*- coding: utf-8 -*-
"""Parse the new Sept-2026 mobile/tablet/laptop price-list batch: Samsung Galaxy
Book (xlsx), plus Nothing, Realme, Lava, OPPO, Motorola (transcribed from
screenshots the user shared inline)."""
import json, os, re
import openpyxl

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")

def num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return round(float(v), 2)
    if isinstance(v, str):
        m = re.search(r'[\d,]+', v.replace(",", ""))
        s = re.sub(r'[^\d.]', '', v.split('(')[0])
        try:
            return round(float(s), 2)
        except ValueError:
            return None
    return None

records = []

# ================= Samsung Galaxy Book (xlsx) =================
def parse_galaxy_book():
    f = "GALAXY BOOK STOCK 1 SEP.xlsx"
    wb = openpyxl.load_workbook(os.path.join(BASE, f), read_only=True, data_only=True)
    ws = wb["Sheet1"]
    out = []
    for row in list(ws.iter_rows(values_only=True))[1:]:
        family, material, descr, qty, price = (list(row) + [None]*5)[:5]
        if not material:
            continue
        price_v = num(price)
        out.append(dict(
            brand="Samsung", category="Laptops & Computing", sub_category=str(family).strip(),
            product_name=f"{family} ({material.split(' ')[0]})", model_code=str(material).strip(),
            description=str(descr).strip(), variant="", key_specs=str(descr).strip(),
            mrp=price_v, landing_price=None, warranty="",
            source_file=f, source_sheet="Sheet1",
        ))
    return out

records += parse_galaxy_book()

# ================= Samsung Galaxy Book6 price revision (screenshot) =================
GALAXY_BOOK6_REVISION = [
    ("NP740VJG-LS1IN", "Galaxy Book6", 134990, 134990),
    ("NP740VJG-KS1IN", "Galaxy Book6", 134990, 134990),
    ("NP740VJG-KG2IN", "Galaxy Book6", 146990, 146990),
    ("NP740VJG-LG2IN", "Galaxy Book6", 146990, 146990),
    ("NP740VJG-LS2IN", "Galaxy Book6", 146990, 146990),
    ("NP740VJG-KS2IN", "Galaxy Book6", 146990, 146990),
    ("NP760VJG-KG1IN", "Galaxy Book6", 139990, 139990),
    ("NP760VJG-LG1IN", "Galaxy Book6", 139990, 139990),
    ("NP760VJG-KG2IN", "Galaxy Book6", 149990, 149990),
    ("NP760VJG-LG2IN", "Galaxy Book6", 149990, 149990),
    ("NP760XJG-KG3IN", "Galaxy Book6", 168990, 168990),
    ("NP940XJG-KG1IN", "Galaxy Book6 Pro", 192990, 192990),
    ("NP940XJG-KG3IN", "Galaxy Book6 Pro", 199990, 199990),
    ("NP940XJG-KG5IN", "Galaxy Book6 Pro", 238990, 238990),
    ("NP940XJG-KG6IN", "Galaxy Book6 Pro", 242990, 242990),
    ("NP960XJG-KG3IN", "Galaxy Book6 Pro", 255990, 255990),
    ("NP960XJG-KG4IN", "Galaxy Book6 Pro", 259990, 259990),
    ("NP960UJG-KG2IN", "Galaxy Book6 Ultra", 282990, 282990),
    ("NP960UJH-XG3IN", "Galaxy Book6 Ultra", 339990, 339990),
]
def parse_galaxy_book6_revision():
    f = "Samsung Product Price Revision - NPC Select Model GT (Aug 2026, screenshot)"
    out = []
    for code, name, dp, mrp in GALAXY_BOOK6_REVISION:
        out.append(dict(
            brand="Samsung", category="Laptops & Computing", sub_category=name,
            product_name=f"{name} ({code})", model_code=code, description=name,
            variant="", key_specs="", mrp=float(mrp), landing_price=float(dp), warranty="",
            source_file=f, source_sheet="price revision table",
        ))
    return out

records += parse_galaxy_book6_revision()

# ================= Nothing Phone (screenshots: MOP revision + margin list) =================
NOTHING_MOP = [
    ("Phone (4a)", "8GB+128GB", 44999),
    ("Phone (4a)", "8GB+256GB", 49999),
    ("Phone (4a)", "12GB+256GB", 50999),
    ("Phone (4a) Pro", "8GB+128GB", 54999),
    ("Phone (4a) Pro", "8GB+256GB", 57999),
    ("Phone (4b)", "8GB+128GB", 39999),
    ("Phone (4b)", "8GB+256GB", 40999),
]
NOTHING_RRP = [
    ("Phone (3)", "12/256", 79999),
    ("Phone (3)", "16/512", 89999),
    ("Phone (4a)", "8/128", 44999),
    ("Phone (4a)", "8/256", 49999),
    ("Phone (4a)", "12/256", 50999),
    ("Phone (4a) Pro", "8/128", 54999),
    ("Phone (4a) Pro", "8/256", 57999),
    ("Phone (4a) Pro", "12/256", 59999),
    ("Phone (3a) Lite", "8/128", 27999),
    ("Phone (3a) Lite", "8/256", 29999),
    ("Phone (4b)", "8/128", 39999),
    ("Phone (4b)", "8/256", 40999),
]
def parse_nothing():
    f = "Nothing Mobile Price List (Sept 2026, screenshot)"
    out = []
    seen = set()
    for model, variant, mop in NOTHING_MOP:
        key = (model, variant)
        seen.add(key)
        out.append(dict(
            brand="Nothing", category="Mobiles & Tablets", sub_category="Smartphone",
            product_name=f"Nothing {model} ({variant})", model_code="", description=f"Nothing {model}, {variant}",
            variant=variant, key_specs=variant, mrp=None, landing_price=float(mop), warranty="",
            source_file=f, source_sheet="MOP revision",
        ))
    for model, variant2, rrp in NOTHING_RRP:
        variant = variant2.replace("/", "GB+") + "GB"
        # avoid duplicate if MOP list already captured this exact model+variant combo (different variant format) - just add as separate RRP-sourced record
        out.append(dict(
            brand="Nothing", category="Mobiles & Tablets", sub_category="Smartphone",
            product_name=f"Nothing {model} ({variant})", model_code="", description=f"Nothing {model}, {variant}",
            variant=variant, key_specs=variant, mrp=float(rrp), landing_price=None, warranty="",
            source_file=f, source_sheet="RRP margin list",
        ))
    return out

records += parse_nothing()

# ================= Realme (Madan Sales Corp, screenshot) =================
REALME = [
    ("C100x (4G)", "4+64", 16999, 16149), ("C100i (4G)", "4+64", 14999, 14249),
    ("C83", "4+64", 18499, 17574), ("C83", "4+128", 21499, 20424), ("C83", "6+128", 24499, 23274),
    ("C85", "4+128", 21999, 20899), ("C85", "6+128", 23999, 22799),
    ("15X", "6+128", 23999, 22799), ("15X", "8+128", 25999, 24699), ("15X", "8+256", 27999, 26599),
    ("15T", "8+128", 27999, 26599), ("15T", "8+256", 29999, 28499), ("15T", "12+256", 31999, 30399),
    ("16X", "4+128", 25999, 24699), ("16X", "6+128", 27999, 26599), ("16X", "6+256", 30999, 29449),
    ("16T", "6+128", 30999, 29449), ("16T", "8+128", 32999, 31349), ("16T", "8+256", 35999, 34199),
    ("16", "8+128", 36999, 35149), ("16", "8+256", 39999, 37999), ("16", "12+256", 42999, 40849),
    ("16 Pro", "8+128", 44999, 42749), ("16 Pro", "8+256", 46999, 44649), ("16 Pro", "12+256", 49999, 47499),
    ("16 Pro+", "8+128", 53999, 51299), ("16 Pro+", "8+256", 55999, 53199), ("16 Pro+", "12+256", 58999, 56049),
    ("P4 Lite", "4+64", 17999, 17279), ("P4 Lite", "4+128", 19999, 19199), ("P4 Lite", "6+128", 22999, 22079),
    ("P4 R", "4+128", 21999, 21119), ("P4 R", "6+128", 23999, 23039), ("P4 R", "6+256", 26999, 25919),
    ("P4 Power", "8+128", 32999, 31679), ("P4 Power", "8+256", 34999, 33599), ("P4 Power", "12+256", 37999, 36479),
]
def parse_realme():
    f = "Realme Price List - Madan Sales Corp (Sept 2026, screenshot)"
    out = []
    for model, variant, mop, dp in REALME:
        out.append(dict(
            brand="Realme", category="Mobiles & Tablets", sub_category="Smartphone",
            product_name=f"Realme {model} ({variant})", model_code="", description=f"Realme {model}, {variant} RAM/Storage",
            variant=variant, key_specs=variant, mrp=float(mop), landing_price=float(dp), warranty="",
            source_file=f, source_sheet="Realme price list",
        ))
    return out

records += parse_realme()

# ================= Lava (A.S. Enterprises, screenshot) =================
LAVA = [
    ("Shark 2", "4G Smart", "4/64GB", 8999), ("Smart 4", "4G Smart", "3/32GB", 7999),
    ("Star 3", "4G Smart", "4/64GB", 8999), ("Smart 4 Plus", "4G Smart", "4/64GB", 9999),
    ("Smart 3", "4G Smart", "3/64GB", 9299),
    ("Shark 2 5G", "5G Smart", "4/128GB", 14422), ("Shark 2 5G", "5G Smart", "4/64GB", 13461),
    ("Blaze Duo2 5G", "5G Smart", "8/256GB", 20191), ("Blaze Duo 3 5G", "5G Smart", "6/128GB", 21153),
    ("Dragon 5G", "5G Smart", "4/128GB", 13941), ("Dragon 5G", "5G Smart", "6/128GB", 14903),
    ("Blaze Amoled 5G", "5G Smart", "4/128GB", 12499), ("Blaze Amoled 5G", "5G Smart", "6/128GB", 13461),
    ("Play Ultra", "5G Smart", "6/128GB", 17788), ("Play Ultra", "5G Smart", "8/128GB", 19230),
    ("Blaze Amoled2 5G", "5G Smart", "6/128GB", 14422), ("Play Max", "5G Smart", "6/128GB", 16826),
    ("Play Max", "5G Smart", "8/128GB", 18268),
    ("Hero Shakti 2026", "Feature", "", 869), ("A1 Josh", "Feature", "", 929),
    ("A1 Josh Bol 2026", "Feature", "", 949), ("A1 Tejas", "Feature", "", 1049),
    ("A1 Music", "Feature", "", 939), ("A2 Smart", "Feature", "", 1169),
    ("A3 Torch", "Feature", "", 1219), ("A3 King", "Feature", "", 1119),
    ("A7 Torch 2026", "Feature", "", 1499), ("Action 4G", "Feature", "", 1679),
    ("Gem 2025", "Feature", "", 1599),
    ("Moto 300 2026", "Moto Feature", "", 1245), ("Moto A100", "Moto Feature", "", 969),
    ("Moto A300", "Moto Feature", "", 1199), ("Moto A10E", "Moto Feature", "", 1159),
]
def parse_lava():
    f = "Lava Mobile Price List - A.S. Enterprises (Sept 2026, screenshot)"
    out = []
    for model, cat, variant, price in LAVA:
        name = f"Lava {model}" + (f" ({variant})" if variant else "")
        out.append(dict(
            brand="Lava", category="Mobiles & Tablets", sub_category=cat,
            product_name=name, model_code="", description=name,
            variant=variant, key_specs=variant, mrp=float(price), landing_price=None, warranty="",
            source_file=f, source_sheet="Lava price list",
        ))
    return out

records += parse_lava()

# ================= OPPO (Bansal Communications, screenshot) =================
OPPO = [
    ("A Series", "A6C 4G", "4+64GB", 16999, 16580), ("A Series", "A6 5G", "4+128GB", 26999, 26090),
    ("A Series", "A6 5G", "6+128GB", 28999, 28020), ("A Series", "A6 5G", "6+256GB", 31999, 30920),
    ("A Series", "A6 Pro 5G", "8+128GB", 32999, 31880), ("A Series", "A6 Pro 5G", "8+256GB", 35999, 34780),
    ("A Series", "A6S 5G", "4+128GB", 24999, 24150), ("A Series", "A6S 5G", "6+128GB", 27999, 27050),
    ("A Series", "A6X 4G", "4+64GB", 12999, 12680), ("A Series", "A6X 5G", "4+128GB", 21999, 21360),
    ("A Series", "A6X 5G", "4+64GB", 18999, 18450), ("A Series", "A6X 5G", "6+128GB", 24999, 24270),
    ("F Series", "F31 5G", "8+128GB", 26999, 25960), ("F Series", "F31 5G", "8+256GB", 28999, 27880),
    ("F Series", "F31 Pro 5G", "12+128GB", 31999, 30770), ("F Series", "F31 Pro 5G", "8+128GB", 27999, 26920),
    ("F Series", "F31 Pro 5G", "8+256GB", 29999, 28850), ("F Series", "F31 Pro+ 5G", "12+256GB", 34999, 33650),
    ("F Series", "F31 Pro+ 5G", "8+256GB", 32999, 31730), ("F Series", "F33 5G", "6+128GB", 34999, 33650),
    ("F Series", "F33 5G", "8+128GB", 36999, 35580), ("F Series", "F33 5G", "8+256GB", 39999, 38460),
    ("F Series", "F33 Pro 5G", "8+128GB", 39999, 38460), ("F Series", "F33 Pro 5G", "8+256GB", 43999, 42310),
    ("K Series", "K14 5G", "6+128GB", 23999, 23300), ("K Series", "K14 5G", "6+256GB", 25999, 25240),
    ("K Series", "K14 5G", "8+256GB", 28999, 28150), ("K Series", "K14x 5G", "4+64GB", 17999, 17470),
    ("K Series", "K14x 5G", "4+128GB", 19999, 19420), ("K Series", "K14x 5G", "6+128GB", 22999, 22330),
    ("Reno Series", "Reno 14 5G", "8+256GB", 44999, 43270), ("Reno Series", "Reno 15", "12+256GB", 50999, 49040),
    ("Reno Series", "Reno 15", "12+512GB", 55999, 53850), ("Reno Series", "Reno 15", "8+256GB", 47999, 46150),
    ("Reno Series", "Reno 15 Pro", "12+256GB", 67999, 65380), ("Reno Series", "Reno 15 Pro", "12+512GB", 72999, 70190),
    ("Reno Series", "Reno 15 Pro Mini", "12+256GB", 59999, 57690), ("Reno Series", "Reno 15 Pro Mini", "12+512GB", 64999, 62500),
    ("Reno Series", "Reno 15C", "12+256GB", 44999, 43270), ("Reno Series", "Reno 16C 5G", "8+128GB", 49999, 48080),
    ("Reno Series", "Reno 16C 5G", "8+256GB", 53999, 51920), ("Reno Series", "Reno 16C 5G", "12+256GB", 59999, 57690),
    ("Reno Series", "Reno 16 5G", "8+256GB", 66999, 64420), ("Reno Series", "Reno 16 5G", "12+256GB", 72999, 70190),
    ("Find X Series", "Find X9", "12+256GB", 84999, 81730), ("Find X Series", "Find X9", "16+512GB", 94999, 91350),
    ("Find X Series", "Find X9 Pro", "16+512GB", 109999, 105770), ("Find X Series", "Find X9S", "12+256GB", 84999, 81730),
    ("Find X Series", "Find X9S", "12+512GB", 94999, 91350), ("Find X Series", "Find X9 Ultra", "16+512GB", 169999, 163460),
]
def parse_oppo():
    f = "OPPO Rate List - Bansal Communications (Sept 2026, screenshot)"
    out = []
    for series, model, variant, mop, dp in OPPO:
        out.append(dict(
            brand="OPPO", category="Mobiles & Tablets", sub_category=series,
            product_name=f"OPPO {model} ({variant})", model_code="", description=f"OPPO {model}, {variant}, {series}",
            variant=variant, key_specs=f"{series}, {variant}", mrp=float(mop), landing_price=float(dp), warranty="",
            source_file=f, source_sheet="OPPO rate list",
        ))
    return out

records += parse_oppo()

# ================= Motorola (scheme payout table, screenshot) =================
MOTOROLA = [
    ("G06", "", 15999), ("G37", "4+64", 18999), ("G37 Power", "4+64", 19999),
    ("G37 Power", "4+128", 21999), ("G37 Power", "8+128", 25999), ("G57 Power", "8+128", 21999),
    ("G67 Power", "8+128", 22999), ("G67 Power", "12+256", 27999), ("G77 Power", "4+128", 24999),
    ("G77 Power", "8+128", 27999), ("G Max", "6+128", 27999),
    ("Edge 60 Fusion", "12+256", 29999), ("Edge 70 Fusion", "8+128", 30999),
    ("Edge 70 Fusion", "8+256", 32999), ("Edge 70 Fusion", "12+256", 34999),
    ("Edge 70 Fusion", "12+512", 38999), ("Edge 70", "", 29999),
    ("Edge 60 Pro", "8+256", 29999), ("Edge 60 Pro", "12+256", 33999),
    ("Edge 70 Pro", "8+256", 39999), ("Edge 70 Pro", "12+256", 42999),
    ("Edge 70 Pro+", "12+256", 47999),
    ("Edge 70 Max", "8+256", 54999), ("Edge 70 Max", "12+256", 59999),
    ("Signature", "12/256 GB", 59999), ("Signature", "16/512 GB", 64999), ("Signature", "16/1 TB", 69999),
    ("Razr Fold", "12+256", 149999), ("Razr Fold", "16+512", 159999), ("Razr Fold (FIFA)", "16+512", 169999),
    ("Razr 60", "8+256", 49999), ("Razr 60 Ultra", "16+512", 79999),
]
def parse_motorola():
    f = "Motorola Scheme Price List (Sept 2026, screenshot)"
    out = []
    for model, variant, mop in MOTOROLA:
        name = f"Motorola {model}" + (f" ({variant})" if variant else "")
        out.append(dict(
            brand="Motorola", category="Mobiles & Tablets", sub_category="Smartphone",
            product_name=name, model_code="", description=name,
            variant=variant, key_specs=variant, mrp=float(mop), landing_price=None, warranty="",
            source_file=f, source_sheet="Motorola scheme list",
        ))
    return out

records += parse_motorola()

if __name__ == "__main__":
    by_brand = {}
    for r in records:
        by_brand[r["brand"]] = by_brand.get(r["brand"], 0) + 1
    for b, c in by_brand.items():
        print(b, c)
    print("TOTAL", len(records))
    with open(os.path.join(OUT, "new_mobile_batch_records.json"), "w") as fh:
        json.dump(records, fh, indent=1, ensure_ascii=False)
