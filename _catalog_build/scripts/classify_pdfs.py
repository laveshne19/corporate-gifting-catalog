import pymupdf, glob, os, re, json

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
OUT = os.path.join(BASE, "_catalog_build", "extracted")

files = sorted(glob.glob(os.path.join(BASE, "*.pdf"))) + sorted(glob.glob(os.path.join(BASE, "*.PDF")))

report = []
for f in files:
    name = os.path.basename(f)
    try:
        d = pymupdf.open(f)
        n = d.page_count
        total_chars = 0
        price_hits = 0
        sample_text = ""
        img_count = 0
        for i, page in enumerate(d):
            txt = page.get_text()
            total_chars += len(txt)
            price_hits += len(re.findall(r'(?:MRP|Rs\.?|₹|INR)\s*[:\-]?\s*[\d,]+', txt, re.IGNORECASE))
            img_count += len(page.get_images())
            if i < 2:
                sample_text += txt[:500]
        chars_per_page = total_chars / max(n, 1)
        report.append(dict(file=name, pages=n, chars_per_page=round(chars_per_page,1),
                            price_pattern_hits=price_hits, image_count=img_count,
                            sample=sample_text[:400].replace("\n"," | ")))
    except Exception as e:
        report.append(dict(file=name, error=str(e)))

with open(os.path.join(OUT, "pdf_classification.json"), "w") as fh:
    json.dump(report, fh, indent=1, ensure_ascii=False)

for r in report:
    if 'error' in r:
        print(r['file'], 'ERROR', r['error'])
    else:
        print(f"{r['file'][:60]:60s} pages={r['pages']:4d} chars/pg={r['chars_per_page']:7.1f} price_hits={r['price_pattern_hits']:4d} imgs={r['image_count']:4d}")
