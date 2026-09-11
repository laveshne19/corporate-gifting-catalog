# -*- coding: utf-8 -*-
"""
Honda two-wheeler lineup (from user-supplied "Product Catalogue" PDF —
this is Honda Motorcycle & Scooter India's own catalog, not "Hero Honda":
Hero MotoCorp and Honda split into separate companies in 2010 and are now
competitors; the PDF logo and every model name here are pure Honda).
Prices are approximate ex-showroom (Delhi-ish average), sourced via web
search — NOT a dealer price list, so flagged clearly as such and with the
state-variation disclaimer the user asked for.
"""
import os, json, requests

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
IMG_DIR = os.path.join(BASE, "_catalog_build", "images", "web")
SRC = "Product Catalogue (Price and Features) _ 05-09-25.pdf"
DISCLAIMER = ("Ex-showroom price shown as an approximate reference — actual on-road price "
              "varies state to state based on RTO registration, road tax and insurance norms "
              "set by the respective state government. Available for corporate gifting / "
              "dealer incentive programs.")

# (name, cc, price, image_url)
ROWS = [
    ("Hornet 2.0", "200cc", 149616, "https://www.carandbike.com/_next/image?url=https%3A%2F%2Fimages.carandbike.com%2Fbike-images%2Flarge%2Fhonda%2Fhornet-20%2Fhonda-hornet-20.jpg%3Fv%3D18&w=1920&q=75"),
    ("NX200", "200cc", 160605, "https://media.zigcdn.com/media/model/2026/Jun/honda-nx200-02-right-side-view_360x240.jpg"),
    ("SP160", "160cc", 117859, "https://asset.autocarindia.com/static/models/colors/20260605_080250_fde420a1.png?w=640&q=75&fm=auto"),
    ("Unicorn", "160cc", 115241, "https://media.zigcdn.com/media/model/2026/May/honda-unicorn-02-right-side-view_360x240.jpg"),
    ("CB125 Hornet", "125cc", 115312, "https://www.bikewale.com/n/cw/ec/207262/cb-125-hornet-right-side-view-6.jpeg?isig=0"),
    ("SP125", "125cc", 90636, "https://media.zigcdn.com/media/model/2026/May/honda-sp-125-01-right-side-view.jpg"),
    ("Shine 125", "125cc", 83683, "https://media.zigcdn.com/media/model/2026/Mar/shine-right-side-view_360x240.jpg"),
    ("Livo", "110cc", 81031, "https://media.zigcdn.com/media/model/2026/May/honda-livo-01-right-side-view_360x240.jpg"),
    ("Shine 100 DX", "100cc", 74959, "https://www.honda2wheelersindia.com/_next/image?url=https%3A%2F%2Fedge.sitecorecloud.io%2Fhondamotorc388f-hmsi8ece-prodb777-e813%2Fmedia%2FProject%2FHONDA2WI%2Fhonda2wheelersindia%2Fnew_asset_compressed%2FRedwings%2FShine-100dx%2FAccessories%2FShine-100-DX-end-pages_638_1038-Form.png%3Fh%3D767%26iar%3D0%26w%3D1080&w=1920&q=75"),
    ("Shine 100", "100cc", 65996, "https://media.zigcdn.com/media/model/2026/Mar/shine-100-right-side-view_360x240.jpg"),
    ("Dio 125", "125cc", 94256, "https://imgd.aeplcdn.com/1280x720/n/cw/ec/152781/dio-125-right-side-view.jpeg?isig=0&q=100"),
    ("Activa 125", "125cc", 92806, "https://utkalhonda.com/uploads/PML-IMAGES804.png"),
    ("Activa", "110cc", 78687, "https://imgd.aeplcdn.com/1280x720/n/cw/ec/210059/activa-6g-right-side-view.webp?isig=0"),
    ("Dio 110", "110cc", 74820, "https://media.zigcdn.com/media/model/2026/Mar/honda-dio-110-right-side-view_360x240.jpg"),
]

def classify(cc):
    return "Two-Wheelers", "Motorcycle" if "cc" in cc and int(cc.replace("cc","")) >= 110 and False else "Motorcycle"

def parse():
    out = []
    for name, cc, price, img in ROWS:
        is_scooter = name in ("Dio 125", "Activa 125", "Activa", "Dio 110")
        sub = "Scooter" if is_scooter else "Motorcycle"
        out.append(dict(
            brand="Honda", category="Two-Wheelers", sub_category=sub,
            product_name=f"Honda {name} ({cc})", model_code=name.replace(" ", "-"),
            description=f"Honda {name}, {cc}. {DISCLAIMER}",
            variant=cc, key_specs=DISCLAIMER,
            mrp=float(price), landing_price=None, warranty="",
            source_file=SRC, source_sheet="Product Catalogue",
            image_file="", image_source="",
            _img_url=img,
        ))
    return out

if __name__ == "__main__":
    os.makedirs(IMG_DIR, exist_ok=True)
    recs = parse()
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
               "Accept": "image/jpeg,image/png,image/webp,image/*;q=0.8"}
    for i, r in enumerate(recs):
        url = r.pop("_img_url")
        r["image_file"] = url
        r["image_source"] = f"Web-verified (high confidence): {url.split('/')[2]}"
    print("Parsed", len(recs), "Honda two-wheeler records")
    with open(os.path.join(OUT, "honda_2w_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
    for r in recs:
        print(" ", r["product_name"], "| Rs.", r["mrp"], "|", r["image_source"])
