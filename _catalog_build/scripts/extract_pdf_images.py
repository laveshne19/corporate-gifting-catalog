import pymupdf, glob, os, json, hashlib

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
IMG_OUT = os.path.join(BASE, "_catalog_build", "images")
MANIFEST = os.path.join(BASE, "_catalog_build", "extracted", "pdf_image_manifest.json")

MIN_W, MIN_H = 300, 300  # skip tiny icons/logos

files = sorted(glob.glob(os.path.join(BASE, "*.pdf"))) + sorted(glob.glob(os.path.join(BASE, "*.PDF")))

manifest = {}
for f in files:
    name = os.path.basename(f)
    safe = "".join(c if c.isalnum() else "_" for c in name)[:60]
    out_dir = os.path.join(IMG_OUT, safe)
    os.makedirs(out_dir, exist_ok=True)
    d = pymupdf.open(f)
    entries = []
    seen_hashes = set()
    for page_idx in range(d.page_count):
        page = d[page_idx]
        for img_idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            try:
                base = d.extract_image(xref)
            except Exception:
                continue
            w, h = base.get("width", 0), base.get("height", 0)
            if w < MIN_W or h < MIN_H:
                continue
            data = base["image"]
            h_hash = hashlib.md5(data).hexdigest()[:12]
            if h_hash in seen_hashes:
                continue
            seen_hashes.add(h_hash)
            ext = base.get("ext", "png")
            fname = f"p{page_idx+1:03d}_{img_idx:02d}_{h_hash}.{ext}"
            fpath = os.path.join(out_dir, fname)
            with open(fpath, "wb") as fh:
                fh.write(data)
            entries.append(dict(page=page_idx+1, file=fname, width=w, height=h, rel_path=os.path.join(safe, fname)))
    manifest[name] = entries
    print(f"{name}: {len(entries)} images saved (>= {MIN_W}x{MIN_H})")

with open(MANIFEST, "w") as fh:
    json.dump(manifest, fh, indent=1)
print("Manifest saved to", MANIFEST)
