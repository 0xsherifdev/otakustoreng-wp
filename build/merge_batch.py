#!/usr/bin/env python3
"""Merge a product-batch workflow output into build/products_done.json (dedup by slug)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DONE = os.path.join(HERE, "products_done.json")

raw = json.load(open(sys.argv[1], encoding="utf-8"))
res = raw.get("result") if isinstance(raw, dict) else raw
res = res or []

done = json.load(open(DONE, encoding="utf-8")) if os.path.exists(DONE) else []
by_slug = {d["slug"]: d for d in done}
added = 0
for it in res:
    if it and it.get("slug"):
        if it["slug"] not in by_slug:
            added += 1
        by_slug[it["slug"]] = it
merged = list(by_slug.values())
json.dump(merged, open(DONE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"batch results: {len(res)} | newly added: {added} | accumulator total: {len(merged)}")
