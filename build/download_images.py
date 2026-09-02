#!/usr/bin/env python3
"""
Download every product image from catalog.json into products/<slug>/.
Resumable (skips files already present). Writes a per-folder _images.txt
manifest and a global build/download.log. No external deps.
"""
import json, os, sys, urllib.request, urllib.error, concurrent.futures, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG = os.path.join(ROOT, "build", "catalog.json")
PRODUCTS_DIR = os.path.join(ROOT, "products")
LOG = os.path.join(ROOT, "build", "download.log")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "\
     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"

catalog = json.load(open(CATALOG, encoding="utf-8"))
os.makedirs(PRODUCTS_DIR, exist_ok=True)

def ext_of(url):
    tail = url.split("?")[0].rsplit(".", 1)
    e = tail[1].lower() if len(tail) == 2 and len(tail[1]) <= 5 else "jpg"
    return "jpg" if e == "jpeg" else e

tasks = []  # (url, dest_path)
for rec in catalog:
    folder = os.path.join(PRODUCTS_DIR, rec["slug"])
    os.makedirs(folder, exist_ok=True)
    manifest = []
    for i, url in enumerate(rec["images"], 1):
        fname = f"{i:02d}.{ext_of(url)}"
        dest = os.path.join(folder, fname)
        manifest.append(f"{fname}\t{url}")
        tasks.append((url, dest))
    with open(os.path.join(folder, "_images.txt"), "w", encoding="utf-8") as f:
        f.write("filename\turl\n" + "\n".join(manifest) + "\n")

total = len(tasks)
done = skipped = failed = 0
lock_log = open(LOG, "a", encoding="utf-8")

def fetch(task):
    url, dest = task
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return ("skip", url)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if not data:
                raise ValueError("empty")
            tmp = dest + ".part"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, dest)
            return ("ok", url)
        except Exception as e:
            if attempt == 2:
                return ("fail", f"{url} :: {e}")
            time.sleep(1.5 * (attempt + 1))

t0 = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
    for status, info in ex.map(fetch, tasks):
        if status == "ok": done += 1
        elif status == "skip": skipped += 1
        else:
            failed += 1
            lock_log.write(f"FAIL {info}\n"); lock_log.flush()
        n = done + skipped + failed
        if n % 100 == 0 or n == total:
            msg = f"[{n}/{total}] ok={done} skip={skipped} fail={failed} {time.time()-t0:.0f}s"
            print(msg, flush=True)
            lock_log.write(msg + "\n"); lock_log.flush()

print(f"DONE ok={done} skip={skipped} fail={failed} total={total}", flush=True)
lock_log.write(f"DONE ok={done} skip={skipped} fail={failed} total={total}\n")
lock_log.close()
