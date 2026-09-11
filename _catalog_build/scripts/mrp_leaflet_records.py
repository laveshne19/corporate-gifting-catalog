# -*- coding: utf-8 -*-
import os, json

OUT = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list/_catalog_build/extracted"
f = "MRP Leaflet_V4.pdf"

def rec(name, cat, mrp, specs):
    return dict(brand="Qubo", category=cat, sub_category="", product_name=name, model_code="",
                description=f"{name} - {specs}", variant="", key_specs=specs, mrp=mrp,
                landing_price=None, warranty="", source_file=f, source_sheet="page 1-2 (vision)")

records = [
    rec("Smart Door Lock Ultra", "Smart Home Devices", 38990, "Wi-Fi, Aerospace Grade Alloy, 4 bolts+1 Deadbolt, Child & Privacy Lock, min door 35mm, Battery 6+ months"),
    rec("Smart Door Lock Nova", "Smart Home Devices", 27990, "Aluminium Alloy Body, 4 bolts+1 Deadbolt, Privacy Lock, min door 32mm (Black MRP 25,990 / Gold MRP 27,990)"),
    rec("Smart Door Lock Alpha", "Smart Home Devices", 22990, "Aluminium Alloy Body, 2 bolts, min door 30mm, Battery 12+ months (Black MRP 21,990 / Gold MRP 22,990)"),
    rec("Smart Door Lock Optima", "Smart Home Devices", 17990, "Aluminium Alloy Body, 4 bolts, min door 32mm, Battery 12+ months"),
    rec("Video Doorbell Pro", "Smart Home Devices", 14990, "2K Resolution, 3MP Sensor, Two-Way Talk, Wi-Fi, AI Person Detection, Wireless Chime"),
    rec("InstaView", "Smart Home Devices", 26980, "1280x800 Resolution, Two-Way Talk, Wi-Fi, compatible with Smart Door Lock"),
    rec("Smart Air Purifier Q200", "Smart Home Devices", 12990, "Coverage 200 sq ft, CADR 150 m3/h, 4-in-1 True HEPA13 filter, App + Voice Control"),
    rec("Smart Air Purifier Q400", "Smart Home Devices", 17990, "Coverage 400 sq ft, CADR 300 m3/h, 4-in-1 True HEPA13 filter"),
    rec("Smart Air Purifier Q500", "Smart Home Devices", 22990, "Coverage 500 sq ft, CADR 350 m3/h, 4-in-1 True HEPA13 filter"),
    rec("Smart Air Purifier Q600", "Smart Home Devices", 24990, "Coverage 600 sq ft, CADR 450 m3/h, 4-in-1 True HEPA13 filter"),
    rec("Smart Air Purifier Q1000", "Smart Home Devices", 29990, "Coverage 1000 sq ft, CADR 600 m3/h, 4-in-1 True HEPA13 filter"),
    rec("Smart Air Purifier R250", "Smart Home Devices", 15990, "Coverage 250 sq ft, CADR 150 m3/h, 4-in-1 True HEPA13 filter"),
    rec("Smart Air Purifier R700", "Smart Home Devices", 28990, "Coverage 700 sq ft, CADR 460 m3/h, 4-in-1 True HEPA13 filter"),
    rec("Smart Cam 360 3MP", "Smart Home Devices", 3990, "3MP Sensor, 1296p, Pan Tilt Zoom, Two-Way Talk, AI Person Detection, Colored Night Vision"),
    rec("Smart Cam 360 2K Prime", "Smart Home Devices", 4490, "3MP Sensor, 1296p, Pan Tilt Zoom, Two-Way Talk, AI Person Detection, Colored Night Vision"),
    rec("Smart Cam 360 4MP", "Smart Home Devices", 5490, "4MP Sensor, 1296p, Pan Tilt Zoom, Two-Way Talk, AI Person Detection, Colored Night Vision"),
    rec("Smart Bullet Camera", "Smart Home Devices", 7990, "3MP Sensor, 1296p, 130deg FOV, AI Person Detection, IP66 Rating, Colored Night Vision"),
]

with open(os.path.join(OUT, "mrp_leaflet_records.json"), "w") as fh:
    json.dump(records, fh, indent=1, ensure_ascii=False)
print("Saved", len(records), "Qubo MRP Leaflet records")
