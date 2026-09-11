# -*- coding: utf-8 -*-
"""
Computes a customer-facing "budget bracket" per product: NLC (landing_price,
whichever basis the source gave — distributor or retailer) plus a 15-35%
margin band, rounded to a clean display bracket. This is what the site
filters/sorts by — never the raw NLC and never the MRP.

If landing_price is missing but mrp exists, back-estimate an implied NLC
(mrp / 1.25) and flag it as estimated rather than sourced.

MRP CAP: for higher-ticket products, landing_price can sit close to MRP
(thin distributor margins are normal on premium electronics), which let
the NLC-based budget_high exceed MRP entirely — a product can't have an
"estimated budget" above its own sticker price, that reads as broken to a
buyer. So after computing the NLC-based band, we cap budget_high (and
budget_low with it) to stay a sensible gap below MRP, sized by price tier
— tighter gap allowed at high price points (thin real-world margins are
normal there), wider gap for cheap items (deeper street discounting is
normal there).
"""
import json, os

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT_DIR = os.path.join(BASE, "_catalog_build", "output")

MARGIN_LOW = 0.15
MARGIN_HIGH = 0.35

# (mrp_threshold, min_gap_fraction) — budget_high capped at mrp * (1 - gap),
# checked top-down, first match wins.
MRP_GAP_TIERS = [
    (40000, 0.10),
    (10000, 0.12),
    (5000, 0.15),
    (0, 0.20),
]

def round_bracket(v, direction):
    if v < 1000:
        step = 50
    elif v < 5000:
        step = 100
    elif v < 20000:
        step = 500
    elif v < 100000:
        step = 1000
    else:
        step = 5000
    if direction == "down":
        return int((v // step) * step)
    return int(-(-v // step) * step)  # ceil

def mrp_gap_fraction(mrp):
    for threshold, frac in MRP_GAP_TIERS:
        if mrp >= threshold:
            return frac
    return MRP_GAP_TIERS[-1][1]

def compute(record):
    landing = record.get("landing_price")
    mrp = record.get("mrp")
    basis = "landing_price"
    nlc = None
    if landing:
        nlc = float(landing)
    elif mrp:
        nlc = float(mrp) / 1.25
        basis = "estimated_from_mrp"
    if not nlc or nlc <= 0:
        record["budget_low"] = None
        record["budget_high"] = None
        record["budget_basis"] = None
        return record
    raw_low = nlc * (1 + MARGIN_LOW)
    raw_high = nlc * (1 + MARGIN_HIGH)
    if mrp and mrp > 0:
        cap = mrp * (1 - mrp_gap_fraction(mrp))
        if raw_high > cap:
            # rescale both ends down, preserving the low/high ratio, so the
            # band width still looks proportionate rather than collapsing
            spread_ratio = raw_low / raw_high
            raw_high = cap
            raw_low = cap * spread_ratio
            if basis == "landing_price":
                basis = "landing_price_mrp_capped"
    low = round_bracket(raw_low, "down")
    high = round_bracket(raw_high, "up")
    mrp_floor = None
    if mrp and mrp > 0:
        mrp_floor = round_bracket(mrp * (1 - mrp_gap_fraction(mrp)), "down")
        if high > mrp_floor:
            high = mrp_floor
    if high <= low:
        step = 50 if low < 1000 else 100
        # bumping `high` up would undo the mrp cap on very cheap items
        # (step granularity is coarse relative to the value) — push `low`
        # down by a step instead, so the mrp ceiling always holds.
        if mrp_floor is not None and high + step > mrp_floor:
            low = max(0, low - step)
        else:
            high = low + step
    record["budget_low"] = low
    record["budget_high"] = high
    record["budget_basis"] = basis
    return record

def main():
    path = os.path.join(OUT_DIR, "master_consolidated.json")
    data = json.load(open(path))
    sourced = 0
    capped = 0
    estimated = 0
    none_count = 0
    for r in data:
        compute(r)
        if r["budget_basis"] == "landing_price":
            sourced += 1
        elif r["budget_basis"] == "landing_price_mrp_capped":
            capped += 1
        elif r["budget_basis"] == "estimated_from_mrp":
            estimated += 1
        else:
            none_count += 1
    json.dump(data, open(path, "w"), indent=1, ensure_ascii=False)
    print(f"Total: {len(data)}")
    print(f"Budget bracket from real NLC: {sourced}")
    print(f"Budget bracket from real NLC, MRP-capped: {capped}")
    print(f"Budget bracket estimated from MRP (no NLC available): {estimated}")
    print(f"No budget bracket (missing both): {none_count}")
    # sample
    import random
    sample = [r for r in data if r["budget_low"]]
    for r in random.sample(sample, 6):
        print(f"  {r['brand']:15s} {r['product_name'][:40]:40s} NLC~{r.get('landing_price')} MRP={r.get('mrp')} -> Rs.{r['budget_low']}-{r['budget_high']} ({r['budget_basis']})")

if __name__ == "__main__":
    main()
