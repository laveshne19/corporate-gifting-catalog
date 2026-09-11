# -*- coding: utf-8 -*-
"""
Gift cards, sourced from woohoo.in's public gift-card listing (India's
largest gift card marketplace, run by Pine Labs). We don't sell these
ourselves at a fixed markup — gift cards are typically issued at face
value by the brand/aggregator — so mrp = landing_price = the discount
shown on the site is noted in key_specs, not priced into the product.
"""
import os, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
SRC = "woohoo.in/gift-cards"

# (name, discount_note, image_url)
ROWS = [
    ("Flipkart E-Gift Voucher", "20% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/6/06_flipkart_2.png?appId=12"),
    ("Amazon Pay E-Gift Card", "0.5% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/7/07_amazon-pay.png?appId=12"),
    ("Amazon Shopping Voucher", "2% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/4/04_amazon-shopping-voucher.png?appId=12"),
    ("Myntra E-Gift Card", "3% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/7/07_myntra.png?appId=12"),
    ("AJIO E-Gift Card", "7% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/1/01_ajio.png?appId=12"),
    ("Bigbasket E-Gift Card", "4% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/2/02_bigbasket.png?appId=12"),
    ("Blinkit E-Gift Card", "3% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/3/03_blinkit-p-5241269.png?appId=12"),
    ("Zepto E-Gift Card", "1.75% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/3/03_zepto.png?appId=12"),
    ("Levi's E-Gift Card", "10% Cashback", "https://b2cstatic.woohoo.in/media/catalog/product/1/5/15_levi_s-p-44110.png?appId=12"),
    ("Ray-Ban E-Gift Card", "8% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/2/7/27_rayban-p-1034920.png?appId=12"),
    ("Pantaloons E-Gift Card", "8.5% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/p/a/pantaloons_5157458072624500.png?appId=12"),
    ("Lifestyle E-Gift Card", "6% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/l/i/lifestyle_1_.png?appId=12"),
    ("Max Fashion E-Gift Card", "8% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/2/5/25_max_fashion-p-4971995.png?appId=12"),
    ("Westside E-Gift Card", "Free Gift Card", "https://b2cstatic.woohoo.in/media/catalog/product/0/2/02_westside_2.png?appId=12"),
    ("Forever New E-Gift Card", "7% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/4/7/47_forever_new-p-3934686.png?appId=12"),
    ("Luxe E-Gift Card (30+ Brands)", "10% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/5/05_luxe_-_30_brands-p-775418.png?appId=12"),
    ("Hamleys Luxe E-Gift Card", "10% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/6/06_hamleys_-_luxe-p-843531.png?appId=12"),
    ("Imagine Apple Premium Reseller E-Gift Card", "2.5% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/1/3/13_imagine_apple_premium_reseller-p-1623105.png?appId=12"),
    ("Helios E-Gift Card", "5% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/0/7/07_helios_2-p-4944162.jpg?appId=12"),
    ("Simon Carter E-Gift Card", "3% Discount", "https://b2cstatic.woohoo.in/media/catalog/product/3/2/32_simon_carter-p-1765745.png?appId=12"),
]

def parse():
    out = []
    for name, discount, img in ROWS:
        brand = name.replace(" E-Gift Card", "").replace(" E-Gift Voucher", "").replace(" Voucher", "")
        out.append(dict(
            brand=brand, category="Gift Cards", sub_category="E-Gift Card",
            product_name=name, model_code="",
            description=f"{name} — digital gift card, redeemable at {brand}. Available in multiple denominations for corporate gifting.",
            variant="Digital / E-Gift", key_specs=f"{discount} on issuance. Denominations available on request.",
            mrp=None, landing_price=None, warranty="",
            source_file=SRC, source_sheet="Gift Cards listing",
            image_file=img, image_source=f"Web-verified (high confidence): woohoo.in",
        ))
    return out

if __name__ == "__main__":
    recs = parse()
    print("Parsed", len(recs), "gift card records")
    with open(os.path.join(OUT, "giftcards_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
