# -*- coding: utf-8 -*-
import os, ssl, urllib.request, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "images", "brand_logos")
os.makedirs(OUT_DIR, exist_ok=True)
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
SSL_CTX = ssl._create_unverified_context()

LOGOS = {
    "Amazon": "https://pngimg.com/uploads/amazon/amazon_PNG17.png",
    "BOYA": "https://www.dokkantech.com/cdn/shop/collections/boya-7272389.png",
    "Bajaj": "https://crystalpng.com/wp-content/uploads/2025/09/Bajaj-Logo.png",
    "Belkin": "https://1000logos.net/wp-content/uploads/2020/09/Belkin-Logo.png",
    "Bose": "https://logos-world.net/wp-content/uploads/2023/01/Bose-Logo.png",
    "Cello": "https://images.seeklogo.com/logo-png/30/1/cello-logo-png_seeklogo-305045.png",
    "Crompton": "https://upload.wikimedia.org/wikipedia/commons/9/93/Crompton_Greaves_Logo.png",
    "Fastrack": "https://upload.wikimedia.org/wikipedia/commons/b/b2/Fastrack_logo.png",
    "Fire-Boltt": "https://vectorseek.com/wp-content/uploads/2023/04/Firebolt-Logo-Vector-300x300.jpg",
    "Haier": "https://crystalpng.com/wp-content/uploads/2025/09/haier-logo.png",
    "Havells": "https://1000logos.net/wp-content/uploads/2021/04/Havells-logo.png",
    "IFB": "https://companieslogo.com/img/orig/IFBIND.NS_BIG-577df970.png",
    "Intex": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Intex_Logo.jpg",
    "La Opala": "https://images.seeklogo.com/logo-png/55/1/laopala-logo-png_seeklogo-555917.png",
    "Lava": "https://images.seeklogo.com/logo-png/25/1/lava-logo-png_seeklogo-258725.png",
    "Lenovo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Lenovo_Global_Corporate_Logo.png/960px-Lenovo_Global_Corporate_Logo.png",
    "Lifelong": "https://frappe.io/files/Lifelong%20Logo.jpg",
    "Luminarc": "https://cdn.freebiesupply.com/logos/large/2x/luminarc-logo-png-transparent.png",
    "Marshall": "https://1000logos.net/wp-content/uploads/2020/04/Marshall-logo.jpg",
    "Mivi": "https://upload.wikimedia.org/wikipedia/commons/8/80/Mivi_Logo.png",
    "Motorola": "https://banner2.cleanpng.com/20180718/vrg/499810e1e983fa6ac70f709efbbd97e7.webp",
    "Noise": "https://adgully.com/img/800/202004/noise.jpg",
    "Nothing": "https://upload.wikimedia.org/wikipedia/commons/0/00/Nothing_Logo.webp",
    "OPPO": "https://upload.wikimedia.org/wikipedia/commons/c/c8/OPPO_logo.png",
    "Otek": "https://otekworld.com/cdn/shop/files/Otek_Logo_mob_e3b99de0-780f-42e0-8273-ed9c3e8f7b80.svg",
    "Philips": "https://cdn.freebiesupply.com/images/large/2x/philips-logo-png-transparent.png",
    "Portronics": "https://cdn.brandfetch.io/id911xtA0s/w/360/h/79/theme/light/logo.png",
    "Preethi": "https://preethizodiac.com/wp-content/uploads/2019/08/Preethi-Logo-02.png",
    "Prestige": "https://www.freelogovectors.net/wp-content/uploads/2020/12/prestige-logo.png",
    "Qubo": "https://www.smarthomeworld.in/wp-content/uploads/2021/11/Qubo_logo.jpg",
    "Realme": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Realme-realme-_logo_box-RGB-01.png",
    "Safari": "https://companieslogo.com/img/orig/SAFARI.NS_BIG-fd5d80fc.png",
    "Samsung": "https://upload.wikimedia.org/wikipedia/commons/f/f1/Samsung_logo_blue.png",
    "Sennheiser": "https://cdn.freebiesupply.com/logos/large/2x/sennheiser-logo-png-transparent.png",
    "Skybags": "https://images.seeklogo.com/logo-png/34/1/skybags-logo-png_seeklogo-343860.png",
    "Skyline": "https://skylineappliances.online/cdn/shop/files/skyline_logo_ca874d1d-20f9-414d-a89f-a529e30546e3.png",
    "Sujata": "https://cdn.brandfetch.io/ida3Uc6XLu/w/350/h/110/theme/dark/logo.png",
    "Sunflame": "https://images.seeklogo.com/logo-png/30/2/sunflame-logo-png_seeklogo-305044.png",
    "Swiss Military": "https://images.seeklogo.com/logo-png/38/1/swiss-military-logo-png_seeklogo-388300.png",
    "Symphony": "https://symphonylimited.com/wp-content/uploads/2022/12/Symphony-ToT-Logo-e1671795456474.png",
    "Titan": "https://vectorseek.com/wp-content/uploads/2023/06/Titan-Watches-Logo-Vector-01.jpg",
    "Usha": "https://images.seeklogo.com/logo-png/33/2/usha-fan-logo-png_seeklogo-336457.png",
    "VIP": "https://images.seeklogo.com/logo-png/34/1/vip-logo-png_seeklogo-345307.png",
    "Welspun": "https://companieslogo.com/img/orig/WELSPUNIND.NS-98ce7058.png",
    "Whirlpool": "https://upload.wikimedia.org/wikipedia/commons/1/10/Whirlpool_Corporation_Logo.png",
    "WiWu": "https://www.wiwu.com/cdn/shop/files/logo.png",
    "boAt": "https://upload.wikimedia.org/wikipedia/commons/2/24/Boat-logo.png",
    "boUlt": "https://cdn.brandfetch.io/idXSHJ3GSR/w/500/h/136/theme/dark/logo.png",
}

def ext_from_url(url):
    u = url.lower().split("?")[0]
    for e in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
        if u.endswith(e):
            return e
    return ".png"

def main():
    results = {}
    ok, fail = 0, 0
    for brand, url in LOGOS.items():
        ext = ext_from_url(url)
        fname = brand.replace(" ", "_").replace("/", "-") + ext
        fpath = os.path.join(OUT_DIR, fname)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as resp:
                blob = resp.read()
            if len(blob) < 300:
                raise ValueError("suspiciously small response")
            open(fpath, "wb").write(blob)
            results[brand] = f"brand_logos/{fname}"
            ok += 1
        except Exception as e:
            print(f"FAIL {brand}: {e}")
            fail += 1

    json.dump(results, open(os.path.join(BASE, "_catalog_build", "output", "brand_logo_map.json"), "w"), indent=1, ensure_ascii=False)
    print(f"\nDone: {ok} downloaded, {fail} failed, {len(LOGOS)} total")

if __name__ == "__main__":
    main()
