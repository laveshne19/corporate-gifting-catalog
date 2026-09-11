# -*- coding: utf-8 -*-
import json, os
from datetime import date
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")
VERSION_TAG = date.today().strftime("%Y%m%d")

COLUMNS = [
    ("product_id", "Product ID", 12),
    ("brand", "Brand / Vendor", 16),
    ("product_name", "Product Name", 42),
    ("description", "Full Description", 50),
    ("category", "Category", 22),
    ("sub_category", "Sub-Category", 20),
    ("variant", "Variant / Colour", 16),
    ("key_specs", "Key Specs / Features", 40),
    ("mrp", "MRP (Rs.)", 12),
    ("landing_price", "Landing / Dealer Price (Rs.)", 16),
    ("price_range_category", "Price Range Category", 26),
    ("image_file", "Image File / Link", 34),
    ("mrp_source", "Source of MRP", 30),
    ("image_source", "Source of Image", 30),
    ("date_last_updated", "Date Last Updated", 14),
]

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=10)
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

INVALID_SHEET_CHARS = set('\\/?*[]:')

def safe_sheet_title(title):
    cleaned = "".join(c for c in title if c not in INVALID_SHEET_CHARS)
    return cleaned[:31]

def write_sheet(wb, title, records):
    ws = wb.create_sheet(safe_sheet_title(title))
    for ci, (key, label, width) in enumerate(COLUMNS, 1):
        cell = ws.cell(row=1, column=ci, value=label)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(ci)].width = width
    ws.freeze_panes = "A2"
    for ri, r in enumerate(records, 2):
        for ci, (key, label, width) in enumerate(COLUMNS, 1):
            val = r.get(key, "")
            cell = ws.cell(row=ri, column=ci, value=val)
            cell.border = BORDER
            if key in ("mrp", "landing_price") and val:
                cell.number_format = "#,##0"
            if key in ("description", "key_specs"):
                cell.alignment = Alignment(wrap_text=True, vertical="top")
    if records:
        last_row = len(records) + 1
        last_col = get_column_letter(len(COLUMNS))
        ref = f"A1:{last_col}{last_row}"
        tab = Table(displayName=f"tbl_{title.replace(' ', '_').replace('-', '_').replace('/', '_')[:20]}_{abs(hash(title))%10000}", ref=ref)
        tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        ws.add_table(tab)
    return ws

def main():
    recs = json.load(open(os.path.join(OUT_DIR, "master_consolidated.json")))
    recs.sort(key=lambda r: (r["brand"], r["category"], r["product_name"]))

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    # ---- Summary / QA sheet first ----
    summary = wb.create_sheet("Summary & QA")
    total = len(recs)
    with_mrp = sum(1 for r in recs if r["mrp"] is not None)
    with_landing = sum(1 for r in recs if r["landing_price"] is not None)
    with_image = sum(1 for r in recs if r.get("image_file"))
    scraped_mrp = sum(1 for r in recs if "scraped" in (r.get("mrp_source") or "").lower())
    scraped_img = sum(1 for r in recs if "scraped" in (r.get("image_source") or "").lower())
    complete = sum(1 for r in recs if r["mrp"] is not None and r.get("image_file"))
    brands = sorted(set(r["brand"] for r in recs))

    rows = [
        ["Nalanda Enterprises — Master Gift Catalog: Data Quality Summary", ""],
        ["Version / Batch", f"v{VERSION_TAG}"],
        ["Generated On", date.today().isoformat()],
        ["", ""],
        ["Total Products Catalogued", total],
        ["Total Vendors / Brands", len(brands)],
        ["Products with MRP", f"{with_mrp} ({with_mrp/total*100:.1f}%)"],
        ["Products with Landing/Dealer Price", f"{with_landing} ({with_landing/total*100:.1f}%)"],
        ["Products with an Image", f"{with_image} ({with_image/total*100:.1f}%)"],
        ["Products with Complete Data (MRP + Image)", f"{complete} ({complete/total*100:.1f}%)"],
        ["MRP filled via web verification", scraped_mrp],
        ["Images sourced via web scraping", scraped_img],
        ["Products with unresolved data gaps (no MRP)", total - with_mrp],
        ["", ""],
        ["Brands / Vendors Included", ", ".join(brands)],
    ]
    for r in rows:
        summary.append(r)
    summary.column_dimensions["A"].width = 45
    summary.column_dimensions["B"].width = 90
    for cell in summary["A"]:
        cell.font = Font(bold=True)
    summary["A1"].font = Font(bold=True, size=14, color="1F4E78")

    # ---- Master sheet (all products) ----
    write_sheet(wb, "Master Catalog", recs)

    # ---- Per price-range sheets ----
    from collections import defaultdict
    by_range = defaultdict(list)
    for r in recs:
        by_range[r["price_range_category"]].append(r)
    range_order = ["Budget (Under Rs.500)", "Everyday (Rs.500 - Rs.1,500)", "Mid-Range (Rs.1,500 - Rs.5,000)",
                   "Premium (Rs.5,000 - Rs.15,000)", "Luxury (Rs.15,000 - Rs.40,000)",
                   "Ultra-Luxury (Above Rs.40,000)", "Unpriced / Needs MRP"]
    for rng in range_order:
        if rng in by_range:
            write_sheet(wb, rng, by_range[rng])

    # ---- Per brand sheets for top brands (optional, only if not too many) ----
    out_path = os.path.join(OUT_DIR, f"Nalanda_Master_Gift_Catalog_{VERSION_TAG}.xlsx")
    wb.save(out_path)
    print("Saved", out_path)
    print("Total products:", total, "| with MRP:", with_mrp, "| with image:", with_image)

if __name__ == "__main__":
    main()
