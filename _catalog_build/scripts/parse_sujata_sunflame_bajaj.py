# -*- coding: utf-8 -*-
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")

def get_lines(fname):
    d = pymupdf.open(os.path.join(BASE, fname))
    lines = []
    for p in d:
        for l in p.get_text().split("\n"):
            l = l.strip()
            if l:
                lines.append(l)
    return lines

NUM_RE = re.compile(r'^[\d,]+(\.\d+)?$')
BOILERPLATE = {"sujata models", "dealer nlc", "(incl. gst)", "mop", "mrp", "(incl. all taxes)",
               "dealers price list", "(w.e.f. 10th august 2026)"}

def parse_sujata():
    lines = get_lines("Sujata Price List.pdf")
    out = []
    cur_cat = ""
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].lower() in BOILERPLATE:
            i += 1
            continue
        if i + 3 < n and NUM_RE.match(lines[i+1]) and NUM_RE.match(lines[i+2]) and NUM_RE.match(lines[i+3]):
            name = lines[i]
            nlc, mop, mrp = lines[i+1], lines[i+2], lines[i+3]
            out.append(dict(
                brand="Sujata", category=cur_cat or "Kitchen Appliances", sub_category="",
                product_name=name, model_code="", description=name, variant="", key_specs="",
                mrp=float(mrp.replace(",", "")), landing_price=float(nlc.replace(",", "")),
                warranty="", source_file="Sujata Price List.pdf", source_sheet="page text",
            ))
            i += 4
            continue
        cur_cat = lines[i]
        i += 1
    return out


def parse_sunflame():
    lines = get_lines("Sunflame Price List - Direct Dealer W.E.F 15th Jun 2026.pdf")
    return lines

def parse_bajaj():
    lines = get_lines("bajaj price list.pdf")
    return lines


if __name__ == "__main__":
    sujata = parse_sujata()
    print("Sujata:", len(sujata))
    for r in sujata[:5]:
        print(" ", r["category"], "|", r["product_name"], r["mrp"], r["landing_price"])
    with open(os.path.join(OUT, "sujata_records.json"), "w") as fh:
        json.dump(sujata, fh, indent=1, ensure_ascii=False)

    print("\n--- Sunflame raw (first 80) ---")
    for l in parse_sunflame()[:80]:
        print(repr(l))
    print("\n--- Bajaj raw (first 80) ---")
    for l in parse_bajaj()[:80]:
        print(repr(l))
