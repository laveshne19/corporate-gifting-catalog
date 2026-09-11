# -*- coding: utf-8 -*-
"""
Resize/compress all site images IN PLACE, preserving each file's exact
filename and extension (no renaming). This keeps site/images always in sync
with the paths recorded in master_consolidated.json — the master pool at
_catalog_build/images/ is never touched or renamed by this script.
"""
import os
from PIL import Image

BASE = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list"
SITE_IMG_DIR = os.path.join(BASE, "_catalog_build", "site", "images")
MAX_DIM = 640
JPEG_QUALITY = 72

total_before = total_after = count = errors = 0

for root, dirs, files in os.walk(SITE_IMG_DIR):
    for f in files:
        fp = os.path.join(root, f)
        try:
            before = os.path.getsize(fp)
            with Image.open(fp) as im:
                if im.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", im.size, (255, 255, 255))
                    im = im.convert("RGBA")
                    bg.paste(im, mask=im.split()[-1])
                    im = bg
                else:
                    im = im.convert("RGB")
                w, h = im.size
                if max(w, h) > MAX_DIM:
                    ratio = MAX_DIM / max(w, h)
                    im = im.resize((max(1, int(w * ratio)), max(1, int(h * ratio))), Image.LANCZOS)
                # Always encode as JPEG bytes for max compression, but keep the
                # original filename/extension unchanged so every reference in
                # master_consolidated.json / index.html still resolves — browsers
                # sniff actual image content for <img> tags regardless of extension.
                im.save(fp, "JPEG", quality=JPEG_QUALITY, optimize=True)
            after = os.path.getsize(fp)
            total_before += before
            total_after += after
            count += 1
        except Exception:
            errors += 1

print(f"Compressed {count} images in place (same filenames): "
      f"{total_before/1024/1024:.1f}MB -> {total_after/1024/1024:.1f}MB "
      f"({(1-total_after/max(total_before,1))*100:.0f}% smaller). Errors: {errors}")
