# -*- coding: utf-8 -*-
import os, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
SRC = "WiWU_Dealer_Price_List.pdf"

# (code, name, category, sub_category, variant, mrp_or_None, dealer_price)
ROWS = [
    ("Wi-C062", "27W Neolink Silicone Cable (2m)", "Accessories", "Cable", "White, C-L", None, 270),
    ("Wi-C062", "27W Neolink Silicone Cable (1m)", "Accessories", "Cable", "Pink/Green, C-L", None, 200),
    ("Wi-C101", "240W Essen Nylon Braided Cable", "Accessories", "Cable", "C-C, 1.5m", None, 270),
    ("Wi-C060", "60W Titanlink 3-in-1 Cable", "Accessories", "Cable", "Grey, C to C+C+L", None, 470),
    ("Wi-C059", "66W Titanlink 3-in-1 Cable", "Accessories", "Cable", "Grey, A to C+Micro+L, 1.2m", None, 390),
    ("Wi-P064", "Classic Stand Wireless Power Bank", "Accessories", "Power Bank", "10000mAh", None, 1550),
    ("PM501", "Power Mega 67W Charger+Cable+PB", "Accessories", "Power Bank", "15000mAh", None, 4250),
    ("Wi-P057", "Knight Series 35W Power Bank", "Accessories", "Power Bank", "10000mAh", None, 2390),
    ("Wi-P056", "22.5W Elite Power Bank", "Accessories", "Power Bank", "10000mAh, Silver", None, 1940),
    ("Wi-WM007", "Dual Wireless Lavalier Microphone", "Accessories", "Microphone", "Real-time noise reduction, dual mic", 5999, 1499),
    ("Wi-CC026", "200W Triple-Port Car Charger", "Accessories", "Car Charger", "USB-C PD PPS, metal body", 3999, 1650),
    ("", "8-in-1 Desktop Power Station", "Accessories", "Desktop Hub", "Consolidates cables & ports", 9999, 3650),
    ("Wi-QC029", "Nano Series 30W Fast Car Charger", "Accessories", "Car Charger", "USB-C + USB-C dual output", 2499, 499),
    ("FMK-05", "Foldable Wireless Keyboard", "Accessories", "Keyboard", "Fold-flat design for travel", 6999, 2299),
    ("", "Pencil Max Universal Stylus", "Accessories", "Stylus", "iOS & Android, palm rejection, magnetic attach", 5999, 1499),
    ("S-04", "Universal Pencil S-04", "Accessories", "Stylus", "Compatible with major tablets", 5999, 1299),
    ("Wi-W037", "3-in-1 Magnetic Wireless Charger Dock", "Accessories", "Wireless Charger", "Phone, watch & earbuds together", 4499, 999),
    ("Wi-QC031", "Bluetooth 5.3 Car FM Transmitter", "Accessories", "Car Accessory", "RGB light, 38W fast charging", 2999, 599),
    ("Wi-FS015", "Hurricane Ultra High-Speed Fan", "Accessories", "Fan", "4000mAh, desk & travel use", 9999, 3299),
    ("", "Foldable 3-in-1 Wireless Charger", "Accessories", "Wireless Charger", "Phone/watch/earbuds, folds flat for travel", 5999, 1450),
    ("Wi-M23", "Magnetic Apple Watch Charger", "Accessories", "Wireless Charger", "USB-C & Lightning input", 2999, 649),
    ("Wi-CP003", "CarPlay Wireless Adapter", "Accessories", "Car Accessory", "Wireless Apple CarPlay dongle", 5999, 2299),
    ("Wi-WM006", "AI Noise-Cancelling Lavalier Mic", "Accessories", "Microphone", "30H battery, ultra-low latency", 5999, 2499),
    ("", "AirPods 3-in-1 Wireless Charging Stand", "Accessories", "Wireless Charger", "iPhone/Watch/AirPods, tri-device charging stand", 6999, 2150),
    ("Wi-W038", "3-in-1 Magnetic Wireless Charging Stn", "Accessories", "Wireless Charger", "iPhone, Watch & Earbuds", 6999, 2550),
    ("", "Warriors Backpack Pro Max", "Luggage & Bags", "Backpack", "15.6\", Black, durable nylon, 30L, 2000g", 22999, 9200),
    ("", "Master Fingerprint Lock Backpack", "Luggage & Bags", "Backpack", "15.6\", Black, anti-theft fingerprint lock", 16999, 6800),
    ("", "Warriors Laptop Sleeve", "Luggage & Bags", "Laptop Sleeve", "14\", Black, CORDURA 1000D nylon, YKK zip", 6999, 2800),
    ("", "Ora Tote", "Luggage & Bags", "Tote Bag", "14\"/16\", Gray/Ivory, waterproof, laptop layer", 6999, 2800),
    ("", "Cozy Classic Case (14\")", "Luggage & Bags", "Laptop Bag", "Black/Gray/Purple, 900D polyester + microfiber", 5499, 2200),
    ("", "Cozy Classic Case (16\")", "Luggage & Bags", "Laptop Bag", "Black/Gray, 900D polyester + microfiber", 5999, 2400),
    ("", "Hali Vertical Layer Bag", "Luggage & Bags", "Laptop Bag", "11\"/14\", Black, waterproof 1680D + PU leather", 5999, 2400),
    ("", "Alpha Slim Sleeve", "Luggage & Bags", "Laptop Sleeve", "13\"-16\", Black/Grey, corner-patent, YKK zip, TPU", 5499, 2200),
    ("", "Cosmo Slim Laptop Bag", "Luggage & Bags", "Laptop Bag", "13.3\", Pink/Black/Grey, waterproof Lycra, embossed", 5999, 2400),
    ("", "Alpha Double Layer Sleeve", "Luggage & Bags", "Laptop Sleeve", "13\"-16\", Black/Grey, corner-patent, YKK zip, TPU", 5999, 2400),
    ("", "Paralle Hardshell Bag (11\")", "Luggage & Bags", "Organiser Bag", "Black/Green/Gray, military shockproof hard case", 5499, 2200),
    ("", "Paralle Hardshell Bag (12.9\")", "Luggage & Bags", "Organiser Bag", "Black/Green/Gray, military shockproof hard case", 5999, 2400),
]

def parse():
    out = []
    for code, name, cat, subcat, variant, mrp, dealer in ROWS:
        out.append(dict(
            brand="WiWu", category=cat, sub_category=subcat,
            product_name=name, model_code=code, description=f"{name} — {variant}",
            variant=variant, key_specs=variant,
            mrp=float(mrp) if mrp else None, landing_price=float(dealer), warranty="",
            source_file=SRC, source_sheet="Dealer Catalog & Price List",
        ))
    return out

if __name__ == "__main__":
    recs = parse()
    print("Parsed", len(recs), "WiWu records")
    with_mrp = sum(1 for r in recs if r["mrp"])
    print("With MRP from catalog:", with_mrp, "| Need MRP scraped:", len(recs) - with_mrp)
    with open(os.path.join(OUT, "wiwu_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
