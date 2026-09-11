import pymupdf, os, json, re

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
f = "All brand price list2.pdf"
OUT = os.path.join(BASE, "_catalog_build", "extracted")

NOISE = {"nalanda", "enterprises", "scf-4", "sector", "19d", "chandigarh",
         "9115513366/9569913332", "dealer", "price", "list", "-", "september",
         "2025", "gadgets", "and", "more....", "catalog", "and", "price", "list"}

def cluster_1d(items, key, gap):
    """items: list of dict with position; returns list of clusters (lists)."""
    s = sorted(items, key=key)
    clusters = []
    cur = []
    last = None
    for it in s:
        v = key(it)
        if last is not None and v - last > gap:
            clusters.append(cur)
            cur = []
        cur.append(it)
        last = v
    if cur:
        clusters.append(cur)
    return clusters

def parse_grid_page(page):
    words = page.get_text("words")
    items = []
    for w in words:
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
        if text.lower().strip(".,-") in NOISE or text == "`":
            continue
        items.append(dict(x=x0, y=y0, text=text))
    if not items:
        return []
    col_clusters = cluster_1d(items, lambda i: i["x"], gap=60)
    products = []
    for col in col_clusters:
        row_clusters = cluster_1d(col, lambda i: i["y"], gap=55)
        for row in row_clusters:
            row_sorted = sorted(row, key=lambda i: i["y"])
            name_parts = []
            nums = []
            for it in row_sorted:
                t = it["text"].replace(",", "")
                if re.fullmatch(r'\d+', t):
                    nums.append(int(t))
                else:
                    name_parts.append(it["text"])
            if not name_parts or len(nums) < 2:
                continue
            name = " ".join(name_parts)
            price, mrp = nums[0], nums[1]
            if mrp < price:
                price, mrp = mrp, price
            products.append(dict(name=name, price=price, mrp=mrp))
    return products

if __name__ == "__main__":
    d = pymupdf.open(os.path.join(BASE, f))
    all_products = []
    target_pages = []
    for i in range(d.page_count):
        t = d[i].get_text()
        if "Dealer Price List - SEPTEMBER 2025" in t:
            target_pages.append(i)
    print("Grid pages found:", target_pages)
    for i in target_pages:
        prods = parse_grid_page(d[i])
        print(f"page {i}: {len(prods)} products")
        all_products.extend(prods)
    for p in all_products:
        print(p)
    out = []
    for p in all_products:
        out.append(dict(
            brand="Swiss Military Audio", category="Audio & Wearables", sub_category="",
            product_name=p["name"].title(), model_code="", description=p["name"].title(),
            variant="", key_specs="", mrp=float(p["mrp"]), landing_price=float(p["price"]),
            warranty="", source_file=f, source_sheet="Swiss Military grid pages",
        ))
    # "Ryze" here is an exact-MRP-match duplicate of "SM Ryze" from the
    # dedicated SM DP PRICE LIST SEPT'26.pdf (same product, same Rs.12,990
    # MRP) — drop it so it isn't listed twice under two different names.
    out = [r for r in out if not (r["product_name"].strip().lower() == "ryze" and r["mrp"] == 12990.0)]
    with open(os.path.join(OUT, "swissmilitary_records.json"), "w") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print("Saved", len(out), "records")
