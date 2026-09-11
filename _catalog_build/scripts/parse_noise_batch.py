# -*- coding: utf-8 -*-
import os, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
SRC = "Noise price list (screenshot, Sep 2026)"

# (product_code_or_none, product_name, retailer_price)
ROWS = [
    ("AUD-HDPHN-AIRCLIPS-2-BLK", "Noise Air Clips 2 OWS - Frost Black", 3156),
    ("AUD-HDPHN-BUDSAPEX-BLK", "Noise Buds Apex Truly Wireless Bluetooth Earbuds - Soft Black", 858),
    ("AUD-HDPHN-BUDSEVOKE-BLK", "Noise Buds Evoke Truly Wireless Bluetooth Earbuds - Ebony Grain", 1045),
    ("AUD-HDPHN-BUDSEVOKE-BEIGE", "Noise Buds Evoke Truly Wireless Bluetooth Earbuds - Ivory Grain", 1045),
    ("AUD-HDPHN-BUDSMARINE-GRY", "Noise Buds Marine Truly Wireless Bluetooth Earbuds - Marine Grey", 2254),
    ("AUD-HDPHN-BUDSMARINE-BLK", "Noise Buds Marine Truly Wireless Bluetooth Earbuds - Marine Black", 2254),
    (None, "Noise Buds MVP 102 Truly Wireless Bluetooth Earbuds - Onyx Black", 1262),
    (None, "Noise Buds MVP 102 Truly Wireless Bluetooth Earbuds - Rogue Grey", 1262),
    (None, "Noise Pop Buds Truly Wireless Bluetooth Earbuds - Forest Pop", 798),
    (None, "Noise Pop Buds Truly Wireless Bluetooth Earbuds - Lilac Pop", 798),
    (None, "Noise Pop Buds Truly Wireless Bluetooth Earbuds - Moon Pop", 798),
    (None, "Noise Air Clips 2 OWS - Frost Ivory", 3156),
    (None, "Noise Buds Trance Truly Wireless Earbuds - Jet Black", 901),
    (None, "Noise Buds Trance Truly Wireless Earbuds - Snow White", 901),
    (None, "Noise Buds X2 Truly Wireless Bluetooth Earbuds - Tide Blue", 1623),
    (None, "Noise Buds X2 Truly Wireless Bluetooth Earbuds - Dune Beige", 1623),
    (None, "Noise Junior Champ 3 Kids Smartwatch - Black Blaze", 1803),
    (None, "Noise Crest Bluetooth Wireless Neckband Earphones with Mic - Velvet Black", 770),
    (None, "Noise NoiseFit Diva Smartwatch - Rose Panel", 3156),
    (None, "Noise Go Buds Truly Wireless Earbuds - Jet Black", 743),
    (None, "Noise Go Buds Truly Wireless Earbuds - Snow White", 743),
    (None, "Noise Go Buds Truly Wireless Earbuds - Cam Lilac", 743),
    (None, "Noise Airwave Bluetooth Wireless Neckband Earphones with Mic - Jet Black", 715),
    (None, "Noise Go Buds Truly Wireless Earbuds - Carbon Green", 743),
    (None, "Noise ColorFit Icon Arc Smartwatch - Jet Black", 1352),
    (None, "Noise ColorFit Icon Arc Smartwatch - Space Blue", 1352),
    (None, "Noise ColorFit Icon Arc Smartwatch - Elite Black", 1532),
    (None, "Noise Pop Buds Truly Wireless Bluetooth Earbuds - Steel Pop", 798),
    (None, "Noise ColorFit Pulse 2 Pro Smartwatch - Elite Black", 1265),
    (None, "Noise Pure Pods Truly Wireless Bluetooth Earbuds - Power Black", 2705),
    (None, "Noise Airwave Max 4 Overhead Wireless Headphone - Carbon Black", 2254),
    (None, "Noise Airwave Max 5 Overhead Wireless Headphone - Carbon Black", 4509),
    (None, "Noise Airwave Max XR Overhead Wireless Headphone - Carbon Black", 3607),
    (None, "Noise Airwave Max XR Overhead Wireless Headphone - Forest Green", 3607),
    (None, "Noise Airwave Max XR Overhead Wireless Headphone - Pearl Beige", 3607),
    (None, "Noise Buds Apex Truly Wireless Bluetooth Earbuds - Cloud Grey", 858),
    (None, "Noise View Buds Truly Wireless Bluetooth Earbuds - Metallic Black", 1925),
    (None, "Noise Fit Vortex Plus Smartwatch - Jet Black", 1837),
    (None, "Noise Fit Vortex Plus Smartwatch - Gold Link", 2200),
    (None, "Noise Junior Explorer 2 Kids Smartwatch - Power Pixel", 5411),
    (None, "Noise Buds N2 Pro Truly Wireless Bluetooth Earbuds - Aurora Red", 1623),
    (None, "Noise Buds N2 Pro Truly Wireless Bluetooth Earbuds - Lunar Silver", 1623),
    (None, "Noise Airwave Max 6 Overhead Wireless Headphone - Carbon Black", 5862),
    (None, "Noise Airwave Max 6 Overhead Wireless Headphone - Cobalt Blue", 5862),
    (None, "Noise ColorFit Macro Smartwatch - Elite Black", 1430),
    (None, "Noise ColorFit Macro Smartwatch - Elite Silver", 1430),
    (None, "Noise NoiseFit Mettalix Smartwatch - Elite Silver", 1760),
    (None, "Noise Power Series 10K mAh Wireless Magsafe Qi2 Powerbank - Onyx Black", 2062),
    (None, "Noise Power Series 10K mAh Wireless Magsafe Qi2 Powerbank - Silver", 2062),
    (None, "Noise NoiseFit Twist Smartwatch - Gold Wine", 1210),
    (None, "Noise TWO Wireless Headphone - Bold Black", 1532),
    (None, "Noise ColorFit Ultra 3 Smartwatch - Glossy Silver (Elite Edition)", 1870),
    (None, "Noise ColorFit Victor 2 Smartwatch - Jet Black", 1540),
    (None, "Noise View Buds Truly Wireless Bluetooth Earbuds - Metallic Blue", 1925),
]

def classify(name):
    n = name.lower()
    if "smartwatch" in n:
        return "Wearables", "Smartwatch"
    if "neckband" in n:
        return "Personal Audio", "Wired EP"
    if "overhead" in n or "headphone" in n:
        return "Personal Audio", "Wireless HP"
    if "powerbank" in n or "power bank" in n:
        return "Accessories", "Power Bank"
    if "buds" in n or "earbuds" in n or "clips" in n:
        return "Personal Audio", "TWS"
    return "Personal Audio", "TWS"

def parse():
    seen = set()
    out = []
    for code, name, price in ROWS:
        key = name.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        category, sub_category = classify(name)
        out.append(dict(
            brand="Noise", category=category, sub_category=sub_category,
            product_name=name, model_code=code or "", description=name,
            variant="", key_specs="",
            mrp=None, landing_price=float(price), warranty="",
            source_file=SRC, source_sheet="Noise retailer price list",
        ))
    return out

if __name__ == "__main__":
    recs = parse()
    print("Parsed", len(recs), "unique Noise records (deduped from", len(ROWS), "rows)")
    for r in recs[:6]:
        print(" ", r["sub_category"], "|", r["product_name"], "|", r["landing_price"])
    with open(os.path.join(OUT, "noise_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
