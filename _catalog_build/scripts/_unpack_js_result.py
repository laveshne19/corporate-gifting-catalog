import json, sys

def unpack(path, out_path):
    d = json.load(open(path))
    t1 = d[0]["text"]
    idx = t1.rfind("\n\n(captured at origin")
    core = t1[:idx] if idx != -1 else t1
    arr = json.loads(core)
    arr2 = json.loads(arr) if isinstance(arr, str) else arr
    json.dump(arr2, open(out_path, "w"), indent=1, ensure_ascii=False)
    print(f"Unpacked {len(arr2)} items -> {out_path}")

if __name__ == "__main__":
    unpack(sys.argv[1], sys.argv[2])
