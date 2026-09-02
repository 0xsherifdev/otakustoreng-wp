#!/usr/bin/env python3
"""
Clean a workflow content result file -> normalized build/<name>_content.json
ready for render_products.py. Reusable for the full run.

Fixes: currency entities -> literal ₦; franchise name normalization;
enforce SEO title <=60 and meta description <=155 (trim at word boundary).
Usage: python3 clean_content.py <raw_task_output.json> <out.json>
"""
import json, sys, re, html

RAW, OUT = sys.argv[1], sys.argv[2]

# any rupee/naira entity or stray rupee char -> literal Naira
CUR_RE = re.compile(r"&#8377;|&#x20b9;|&#8358;|&#x20a6;|₹")

FRANCHISE_ALIASES = {
    "demon slayer (kimetsu no yaiba)": "Demon Slayer",
    "kimetsu no yaiba": "Demon Slayer",
    "jujutsu kaisen (jjk)": "Jujutsu Kaisen",
    "jjk": "Jujutsu Kaisen",
    "attack on titan (aot)": "Attack on Titan",
    "aot": "Attack on Titan",
    "dragon ball z": "Dragon Ball", "dragon ball super": "Dragon Ball",
    "one piece (one piece)": "One Piece",
    "my hero academia (mha)": "My Hero Academia",
    "hunter x hunter (hxh)": "Hunter x Hunter",
}

def fix_cur(s):
    return CUR_RE.sub("₦", s) if isinstance(s, str) else s

def norm_franchise(f):
    if not f:
        return f
    base = f.strip()
    low = base.lower()
    if low in FRANCHISE_ALIASES:
        return FRANCHISE_ALIASES[low]
    # strip parenthetical suffix e.g. "Demon Slayer (Kimetsu no Yaiba)"
    stripped = re.sub(r"\s*\(.*?\)\s*$", "", base).strip()
    if stripped.lower() in FRANCHISE_ALIASES:
        return FRANCHISE_ALIASES[stripped.lower()]
    return stripped or base

def trim(s, n):
    if len(s) <= n:
        return s
    cut = s[:n]
    # back off to last word boundary
    sp = cut.rfind(" ")
    if sp > n * 0.6:
        cut = cut[:sp]
    return cut.rstrip(" .,-—") + "."

raw = json.load(open(RAW, encoding="utf-8"))
res = raw["result"] if isinstance(raw, dict) and "result" in raw else raw

out = []
report = []
for item in res:
    c = item["content"]
    # currency across all string fields
    for k, v in list(c.items()):
        if isinstance(v, str):
            c[k] = fix_cur(v)
        elif isinstance(v, list):
            c[k] = [fix_cur(x) for x in v]
    c["franchise"] = norm_franchise(c.get("franchise", ""))
    # enforce SEO limits
    if len(c.get("seo_title", "")) > 60:
        report.append(f"{item['slug']}: seo_title trimmed {len(c['seo_title'])}->60")
        c["seo_title"] = trim(c["seo_title"], 60)
    if len(c.get("meta_description", "")) > 155:
        report.append(f"{item['slug']}: meta trimmed {len(c['meta_description'])}->155")
        c["meta_description"] = trim(c["meta_description"], 155)
    out.append({"slug": item["slug"], "product_id": item.get("product_id"),
                "content": c, "issues": item.get("issues", [])})

json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"cleaned {len(out)} -> {OUT}")
for r in report:
    print("  fix:", r)
if not report:
    print("  (no length fixes needed)")
