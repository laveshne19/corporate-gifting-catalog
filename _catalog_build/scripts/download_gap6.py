import json, sys, os, requests

WEB_DIR = "/Users/laveshbansal/Downloads/📁 Master Folder/master price list/_catalog_build/images/web"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/jpeg,image/png,image/*,*/*;q=0.8",
}

MAGIC = {
    b"\xff\xd8\xff": "jpg",
    b"\x89PNG\r\n\x1a\n": "png",
    b"RIFF": "webp",  # need further check for WEBP at offset 8
    b"GIF87a": "gif",
    b"GIF89a": "gif",
}

def sniff(data: bytes):
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    return None

def download_one(member_id, url, timeout=15):
    dest = os.path.join(WEB_DIR, f"{member_id}.jpg")
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
        r.raise_for_status()
        data = r.content
        if len(data) < 2000:
            return False, "too_small"
        kind = sniff(data)
        if kind is None:
            return False, "not_image_or_avif"
        with open(dest, "wb") as f:
            f.write(data)
        return True, kind
    except Exception as e:
        return False, str(e)[:200]

def main():
    # input: json file with list of {"member_id":..., "url":...}
    infile = sys.argv[1]
    with open(infile) as f:
        jobs = json.load(f)
    results = []
    for job in jobs:
        ok, info = download_one(job["member_id"], job["url"])
        results.append({"member_id": job["member_id"], "ok": ok, "info": info, "url": job["url"]})
        print(f"{'OK' if ok else 'FAIL'} {job['member_id']} {info}")
    outfile = sys.argv[2] if len(sys.argv) > 2 else "download_results.json"
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
