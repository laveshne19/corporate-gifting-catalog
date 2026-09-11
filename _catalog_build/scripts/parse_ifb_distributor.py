# -*- coding: utf-8 -*-
import pymupdf, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")
F = "PRICE LIST DISTRIBUTOR.pdf"

TYPES = {"Top Load", "Front Load", "Cloth Dryer", "DW", "MW"}
CAT_MAP = {"Top Load": "Top Load Washing Machine", "Front Load": "Front Load Washing Machine",
           "Cloth Dryer": "Clothes Dryer", "DW": "Dishwasher", "MW": "Microwave Oven"}
SAP_RE = re.compile(r'^\d{13}$|^TL-?\d')  # sap codes are 13-digit numeric

def get_lines():
    d = pymupdf.open(os.path.join(BASE, F))
    lines = []
    for p in d:
        for l in p.get_text().split("\n"):
            l = l.strip()
            if l:
                lines.append(l)
    return lines

def is_num_line(l):
    return bool(re.fullmatch(r'[\d,]+(\.\d+)?', l.replace(" ", "")))

def parse():
    lines = get_lines()
    # drop header/boilerplate lines
    lines = [l for l in lines if l not in ("Type", "SAP Code", "Model Name", "Capacity", "MRP", "DP",
                                            "MOP", "Colour", "Features", "Steam", "Knob") or True]
    out = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i] in TYPES:
            typ = lines[i]
            i += 1
            if i >= n or not re.fullmatch(r'\d{9,14}', lines[i].replace("-", "")):
                continue
            sap = lines[i]
            i += 1
            if i >= n:
                break
            model = lines[i]
            i += 1
            if i >= n:
                break
            capacity = lines[i]
            i += 1
            # collect numeric tokens across following lines (could be split across 1-3 lines)
            nums = []
            while i < n and len(nums) < 3:
                toks = lines[i].split()
                if all(is_num_line(t) for t in toks) and toks:
                    nums.extend(toks)
                    i += 1
                else:
                    break
            if len(nums) < 2:
                continue
            mrp = float(nums[0].replace(",", ""))
            dp = float(nums[1].replace(",", "")) if len(nums) > 1 else None
            colour = lines[i] if i < n else ""
            i += 1
            features = []
            while i < n and lines[i] not in TYPES and not re.fullmatch(r'\d{9,14}', lines[i]):
                # stop feature collection if this line looks like start of a new record (heuristic: next-next is a SAP code)
                if i + 1 < n and re.fullmatch(r'\d{9,14}', lines[i+1]) and lines[i] in TYPES:
                    break
                features.append(lines[i])
                i += 1
                if len(features) >= 4:
                    break
            out.append(dict(
                brand="IFB", category="Home Appliances", sub_category=CAT_MAP.get(typ, typ),
                product_name=model, model_code=sap, description=f"{model}, {capacity}, {colour}",
                variant=colour, key_specs=f"{capacity}; " + ", ".join(features),
                mrp=mrp, landing_price=dp, warranty="",
                source_file=F, source_sheet="distributor price list",
            ))
            continue
        i += 1
    return out

if __name__ == "__main__":
    recs = parse()
    print("Parsed", len(recs))
    for r in recs[:8]:
        print(" ", r["sub_category"], "|", r["product_name"], r["mrp"], r["landing_price"], "|", r["variant"])
    with open(os.path.join(OUT, "ifb_distributor_records.json"), "w") as fh:
        json.dump(recs, fh, indent=1, ensure_ascii=False)
